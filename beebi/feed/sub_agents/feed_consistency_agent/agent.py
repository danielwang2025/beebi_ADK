import pandas as pd
import re
from typing import Optional, Dict, Any
import numpy as np

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

def analyze_feed_consistency(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    if feed_df.empty:
        return {
            "summary": "No feeding records found.",
            "time_variability_cv": None,
            "volume_variability_cv": None,
            "time_pattern": None,
            "volume_pattern": None,
            "recommendation": "Please check for missing or unrecorded data."
        }

    now = feed_df["StartTime"].max()

    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    recent_df = recent_df.dropna(subset=["StartTime", "Volume_ml"])
    recent_df.sort_values("StartTime", inplace=True)

    if recent_df.empty or recent_df.shape[0] < 2:
        return {
            "summary": f"Insufficient feeding records in the last {days} days to calculate variability." if days else "Insufficient feeding records to calculate variability.",
            "time_variability_cv": None,
            "volume_variability_cv": None,
            "time_pattern": None,
            "volume_pattern": None,
            "recommendation": "Please ensure data completeness."
        }

    # Calculate feeding time intervals (hours)
    intervals = recent_df["StartTime"].diff().dt.total_seconds().dropna() / 3600
    # Get feeding volumes (Volume_ml, in ml)
    volumes = recent_df["Volume_ml"].dropna()

    # Calculate coefficient of variation (CV = std dev / mean) as variability measure
    time_cv = intervals.std() / intervals.mean() if intervals.mean() != 0 else np.nan
    volume_cv = volumes.std() / volumes.mean() if volumes.mean() != 0 else np.nan

    # Evaluate time variability
    if time_cv < 0.2:
        time_pattern = "Feeding intervals are very regular."
    elif time_cv > 0.5:
        time_pattern = "Feeding intervals vary significantly, showing irregularity."
    else:
        time_pattern = "Feeding intervals show moderate variability, generally normal."

    # Evaluate volume variability
    if volume_cv < 0.2:
        volume_pattern = "Feeding volumes are fairly stable with low variability."
    elif volume_cv > 0.5:
        volume_pattern = "Feeding volumes vary greatly, possibly indicating unstable feeding amounts."
    else:
        volume_pattern = "Feeding volumes have some variability, within a normal range."

    # Combined recommendation
    recommendation = (
        f"Time variability: {time_pattern} Feeding volume variability: {volume_pattern}. "
        "If large variability exists, consider observing the baby's condition and feeding habits, "
        "and consult a pediatrician if necessary."
    )

    return {
        "summary": f"Feeding time and volume variability analysis for the last {days} days." if days else "Feeding time and volume variability analysis.",
        "time_variability_cv": round(time_cv, 3) if not np.isnan(time_cv) else None,
        "volume_variability_cv": round(volume_cv, 3) if not np.isnan(volume_cv) else None,
        "time_pattern": time_pattern,
        "volume_pattern": volume_pattern,
        "recommendation": recommendation
    }


from google.adk.agents import Agent

feed_consistency_agent = Agent(
    name="feed_consistency_analyst",
    model="gemini-2.5-flash",
    description="An agent that analyzes the consistency of feeding times and volumes to detect regularity or instability.",
    instruction="""
    You are a feed consistency analyst agent.
    Your task is to analyze the variability of feeding times and feeding volumes over a given period.
    Identify whether the feeding pattern is regular or shows instability that might indicate baby's discomfort or feeding habit issues.
    Use the analyze_feed_consistency tool to generate your report.
    """,
    tools=[analyze_feed_consistency],
)
