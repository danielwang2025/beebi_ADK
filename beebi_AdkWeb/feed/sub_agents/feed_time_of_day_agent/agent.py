import pandas as pd
import re
from typing import Optional, Dict, Any

from beebi.data.db_utils import fetch_activity_data  # Use database utility to fetch data

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

    # Extract ml value
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

def analyze_feed_time_of_day(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    # Return message if no data is available
    if feed_df.empty:
        return {
            "summary": "No feeding records found.",
            "peak_periods": {},
            "recommendation": "Please check for missing or unrecorded data."
        }

    now = feed_df["StartTime"].max()

    # Filter for the last N days if specified
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    if recent_df.empty:
        return {
            "summary": f"No feeding records found in the last {days} days." if days else "No feeding records found.",
            "peak_periods": {},
            "recommendation": "Please check for missing or unrecorded data."
        }

    # Define time period classification
    def time_period(hour):
        if 6 <= hour < 10:
            return "morning"
        elif 10 <= hour < 14:
            return "noon"
        elif 17 <= hour < 20:
            return "evening"
        else:
            return "night"

    recent_df["Period"] = recent_df["StartTime"].dt.hour.apply(time_period)

    # Count feedings per time period
    counts = recent_df["Period"].value_counts().to_dict()
    total_feeds = sum(counts.values())

    if total_feeds == 0:
        return {
            "summary": f"Insufficient feeding data in the last {days} days to analyze time distribution.",
            "peak_periods": {},
            "recommendation": "Please check for missing or unrecorded data."
        }

    peak_periods = {period: round(count / total_feeds * 100, 1) for period, count in counts.items()}

    # Identify peak feeding period
    peak_time = max(peak_periods, key=peak_periods.get)

    recommendation = (
        f"The baby feeds most frequently during the {peak_time} period, accounting for {peak_periods[peak_time]}% of feedings. "
        "Consider adjusting the feeding schedule to align with this peak period to avoid excessive hunger or overly frequent feeding. "
        "If night feedings are frequent, you may consider improving the sleep environment to reduce disturbances."
    )

    return {
        "summary": f"Feeding time distribution over the past {days} days (%): {peak_periods}",
        "peak_periods": peak_periods,
        "recommendation": recommendation
    }

from google.adk.agents import Agent

feed_time_of_day_agent = Agent(
    name="feed_time_of_day_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes peak feeding times of day to help parents optimize feeding schedules.",
    instruction="""
    You analyze baby's feeding data to find peak feeding periods during the day: morning, noon, evening, and night.
    Your insights help parents optimize feeding rhythms and predict baby's hunger times.

    Use the analyze_feed_time_of_day tool to generate your analysis and recommendations.
    """,
    tools=[analyze_feed_time_of_day],
)
