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

def detect_sleep_anomalies(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    try:
        sleep_df = preprocess_sleep_data(days=days, customer_id=customer_id)
        if sleep_df.empty:
            return {
                "status": "success",
                "report": {
                    "days_with_sleep_duration_jumps": [],
                    "missed_nap_days": [],
                    "note": "No sleep data found in the specified time range."
                }
            }

        # Extract date and hour
        sleep_df["Date"] = sleep_df["StartTime"].dt.date
        sleep_df["StartHour"] = sleep_df["StartTime"].dt.hour

        # Step 1: Daily total sleep duration (minutes)
        daily_sleep = sleep_df.groupby("Date")["Duration"].sum().reset_index()
        daily_sleep["SleepChange"] = daily_sleep["Duration"].diff()

        # Mark dates with change > 90 minutes
        large_changes = daily_sleep[abs(daily_sleep["SleepChange"]) > 90]
        large_change_days = large_changes["Date"].astype(str).tolist()

        # Step 2: Nap detection (12pm–6pm and Duration ≤ 120min)
        sleep_df["IsNap"] = sleep_df["StartHour"].between(12, 17, inclusive="both") & (sleep_df["Duration"] <= 120)

        # Count number of naps per day
        nap_counts = sleep_df[sleep_df["IsNap"]].groupby("Date").size()
        nap_avg = nap_counts.mean() if not nap_counts.empty else 0

        # Find days with nap count much lower than average
        threshold = max(1, nap_avg * 0.5)
        missed_nap_days = nap_counts[nap_counts < threshold].index.astype(str).tolist()

        return {
            "status": "success",
            "report": {
                "days_with_sleep_duration_jumps": large_change_days,
                "missed_nap_days": missed_nap_days
            }
        }

    except Exception as e:
        import traceback
        print("Sleep anomaly detection error:", e)
        traceback.print_exc()
        return {"status": "error", "error_message": str(e)}



from google.adk.agents import Agent

sleep_anomaly_agent = Agent(
    name="sleep_anomaly_agent",
    model="gemini-2.5-flash",
    description="Detects sleep anomalies such as sudden changes in duration and missed naps.",
    instruction=(
        "You are a Sleep Anomaly Detection Agent. "
        "Use the 'detect_sleep_anomalies' tool to find days with large changes in sleep duration and missed naps "
        "based on historical nap patterns. Only use the tool to analyze; do not guess or summarize manually."
    ),
    tools=[detect_sleep_anomalies]
)