import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from beebi.data.db_utils import fetch_activity_data  # Use database utility to fetch data

def preprocess_sleep_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Sleep", since_days=since_days)
    if df.empty:
        return df
    # Convert time and numeric types
    df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
    df["EndTime"] = pd.to_datetime(df["EndTime"], errors="coerce")
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    # Keep only valid records
    df = df.dropna(subset=["StartTime", "EndTime", "Duration"])
    # Keep only records of type Sleep
    if "Type" in df.columns:
        df = df[df["Type"] == "Sleep"].copy()
    df = df.sort_values("StartTime")
    return df

def analyze_sleep_sessions(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze sleep data and return key statistics.
    Supports analysis of data from the last N days, defaults to all data.
    """
    sleep_df = preprocess_sleep_data(days=days, customer_id=customer_id)
    if sleep_df.empty:
        return {
            "status": "success",
            "report": "No sleep data found."
        }

    now = sleep_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = sleep_df["StartTime"].min()
    recent_df = sleep_df[sleep_df["StartTime"] >= start_date].copy()
    if recent_df.empty:
        return {
            "status": "success",
            "report": f"No sleep data found for the last {days} days." if days else "No valid sleep data found."
        }

    # Calculate sleep duration in hours (Duration is in minutes)
    recent_df["DurationHours"] = recent_df["Duration"] / 60.0

    # Daily total sleep duration
    recent_df["Date"] = recent_df["StartTime"].dt.date
    daily_sleep = recent_df.groupby("Date")["DurationHours"].sum().reset_index()

    total_days = daily_sleep["Date"].nunique()
    total_sessions = len(recent_df)
    total_duration_hours = recent_df["DurationHours"].sum()

    average_per_day = round(total_duration_hours / total_days, 2) if total_days else 0
    average_per_session = round(recent_df["Duration"].mean(), 2) if total_sessions else 0

    # Sleep quality distribution: poor < 6h, good 6-8h, rich > 8h
    recent_df["Quality"] = recent_df["DurationHours"].apply(
        lambda h: "Poor" if h < 6 else ("Rich" if h > 8 else "Good")
    )
    quality_counts = recent_df["Quality"].value_counts().to_dict()

    return {
        "status": "success",
        "report": {
            "days_analyzed": total_days,
            "total_sessions": total_sessions,
            "avg_hours_per_day": average_per_day,
            "avg_duration_per_session_minutes": average_per_session,
            "sleep_quality_distribution": quality_counts
        }
    }



from google.adk.agents import Agent

sleep_analysis_agent = Agent(
    name="sleep_analysis_agent",
    model="gemini-2.5-flash",
    description="Analyzes and summarizes user sleep session data.",
    instruction="""
    You are the main Sleep Analysis Agent. Your job is to summarize sleep data using the tool 'analyze_sleep_sessions'.
    Use this tool to process session count, average duration, and sleep quality trends.
    You do not handle greetings, farewells, or unrelated topics.
    Always call the tool to generate reports. Do not generate reports by yourself.
    """,
    tools=[analyze_sleep_sessions]
)