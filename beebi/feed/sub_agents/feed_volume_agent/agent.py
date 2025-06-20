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

def analyze_feed_volume(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    # Return message if no data is found
    if feed_df.empty:
        return {
            "summary": "No feeding records found.",
            "total_volume_ml": 0,
            "average_volume_per_feed": 0,
            "feeds_per_day": 0,
            "recommendation": "Please check for missing or unrecorded data."
        }

    now = feed_df["StartTime"].max()

    # If days are specified, filter data for the most recent N days
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    if recent_df.empty:
        return {
            "summary": f"No feeding records found in the last {days} days." if days else "No feeding records found.",
            "total_volume_ml": 0,
            "average_volume_per_feed": 0,
            "feeds_per_day": 0,
            "recommendation": "Please check for missing or unrecorded data."
        }

    total_volume = recent_df["Volume_ml"].sum()
    feed_count = recent_df.shape[0]
    avg_per_feed = recent_df["Volume_ml"].mean()
    feeds_per_day = feed_count / days if days else feed_count

    if avg_per_feed < 90:
        rec = "The baby consumes a relatively small amount per feed. Consider checking for weak sucking or overly short intervals between feeds."
    elif avg_per_feed > 150:
        rec = "The baby consumes a relatively large amount per feed. Watch for signs of vomiting or bloating."
    else:
        rec = "The baby's milk intake per feed is within a healthy range. You can maintain the current feeding strategy."

    return {
        "summary": f"In the past {days} days, {feed_count} feeds were recorded with a total intake of {total_volume} ml, averaging {avg_per_feed:.1f} ml per feed." if days else f"A total of {feed_count} feeds were recorded with {total_volume} ml intake, averaging {avg_per_feed:.1f} ml per feed.",
        "total_volume_ml": int(total_volume),
        "average_volume_per_feed": round(avg_per_feed, 1),
        "feeds_per_day": round(feeds_per_day, 2),
        "recommendation": rec
    }

from google.adk.agents import Agent

feed_volume_agent = Agent(
    name="feed_volume_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes baby feeding data over a specified number of days.",
    instruction="""
    You are a feeding volume analyst agent responsible for analyzing feeding volume patterns.
    You can provide insights into total volume, frequency, and suggestions based on baby's milk intake.
    Use the analyze_feed_volume tool to generate your report.
    """,
    tools=[analyze_feed_volume],
)
