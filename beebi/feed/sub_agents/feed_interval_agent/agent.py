import pandas as pd
import re
from typing import Optional, Dict, Any

from beebi.data.db_utils import fetch_activity_data  # Use database utilities to fetch data

def preprocess_feed_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Feed", since_days=since_days)
    if df.empty:
        return df

    # Convert time format
    df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")

    # Extract ml values
    def extract_ml(value):
        if pd.isna(value):
            return None
        match = re.search(r"(\d+)\s*ml", str(value))
        return int(match.group(1)) if match else None

    df["Volume_ml"] = df["EndCondition"].apply(extract_ml)
    feed_df = df[df["Volume_ml"].notnull()].copy()
    feed_df = feed_df.dropna(subset=["StartTime"])
    feed_df.sort_values("StartTime", inplace=True)

    return feed_df[["StartTime", "StartCondition", "Volume_ml"]]

def analyze_feed_intervals(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    # If no feeding data, return prompt immediately
    if feed_df.empty or feed_df.shape[0] < 2:
        return {
            "summary": "Not enough feeding records to calculate intervals.",
            "average_interval_hours": None,
            "min_interval_hours": None,
            "max_interval_hours": None,
            "std_dev_hours": None,
            "recommendation": "Please check for missing or unrecorded data."
        }

    now = feed_df["StartTime"].max()

    # Filter data for the last N days if specified
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    recent_df = recent_df.dropna(subset=["StartTime"])
    recent_df.sort_values("StartTime", inplace=True)

    if recent_df.shape[0] < 2:
        return {
            "summary": f"Too few feeding records in the last {days} days to calculate intervals." if days else "Too few feeding records to calculate intervals.",
            "average_interval_hours": None,
            "min_interval_hours": None,
            "max_interval_hours": None,
            "std_dev_hours": None,
            "recommendation": "Please check for missing or unrecorded data."
        }

    # Calculate intervals (hours)
    intervals = recent_df["StartTime"].diff().dropna().dt.total_seconds() / 3600
    avg_interval = intervals.mean()
    min_interval = intervals.min()
    max_interval = intervals.max()
    std_dev = intervals.std()

    # Simple regularity analysis
    if std_dev < 1:
        pattern = "Feeding intervals are very regular."
    elif std_dev > 3:
        pattern = "Feeding intervals vary widely, possibly due to inconsistent schedule or missing records."
    else:
        pattern = "Feeding intervals fluctuate moderately, which is generally normal."

    return {
        "summary": f"On average, feeding occurs every {avg_interval:.1f} hours (min {min_interval:.1f} hours, max {max_interval:.1f} hours) in the last {days} days." if days else f"On average, feeding occurs every {avg_interval:.1f} hours (min {min_interval:.1f} hours, max {max_interval:.1f} hours).",
        "average_interval_hours": round(avg_interval, 1),
        "min_interval_hours": round(min_interval, 1),
        "max_interval_hours": round(max_interval, 1),
        "std_dev_hours": round(std_dev, 2),
        "recommendation": pattern
    }


from google.adk.agents import Agent

feed_interval_agent = Agent(
    name="feed_interval_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes baby feeding intervals over a specified number of days.",
    instruction="""
    You are a feeding interval analyst agent responsible for analyzing the timing between feeding sessions.
    You help detect patterns such as overly frequent feeding, long gaps between sessions, or irregular schedules.
    Use the analyze_feed_intervals tool to generate your report. Your output should be clear, concise, and insightful for parents or caregivers.
    """,
    tools=[analyze_feed_intervals],
)
