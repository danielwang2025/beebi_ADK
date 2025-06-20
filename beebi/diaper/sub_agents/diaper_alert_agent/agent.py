from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data

def preprocess_diaper_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    """
    Fetch raw diaper data from the database for the specified number of days and customer_id.
    """
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Diaper", since_days=since_days)
    if df.empty:
        return df
    df["StartTime"] = pd.to_datetime(df["StartTime"])

    # Extract pee and poo volume/type
    def extract_condition(cond, kind):
        if pd.isna(cond):
            return None
        cond = str(cond).lower()
        match = re.search(rf"{kind}:(small|medium|big)", cond)
        return match.group(1) if match else None

    df["Pee"] = df["EndCondition"].apply(lambda x: extract_condition(x, "pee"))
    df["Poo"] = df["EndCondition"].apply(lambda x: extract_condition(x, "poo"))
    df = df.sort_values("StartTime")
    return df

def analyze_diaper_alert(
    days: Optional[int] = None,
    max_interval_hours: float = 5.0,
    big_poo_threshold: int = 2,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Identify abnormal excretion frequency or type, such as consecutive big poos or long intervals without a change.
    """
    diaper_df = preprocess_diaper_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "No diaper change records found. Unable to perform alert analysis.",
            "alerts": [],
            "recommendation": "Please ensure there is diaper data available."
        }

    now = diaper_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = diaper_df["StartTime"].min()
    recent_df = diaper_df[diaper_df["StartTime"] >= start_date].copy()
    if recent_df.empty:
        return {
            "summary": f"No diaper change records in the last {days if days else 'all'} days.",
            "alerts": [],
            "recommendation": "Please ensure the data contains diaper change information."
        }

    alerts = []

    # Check for consecutive big poos
    poo_types = recent_df["Poo"].tolist()
    count = 0
    for i, val in enumerate(poo_types):
        if val == "big":
            count += 1
            if count >= big_poo_threshold:
                alerts.append(f"Detected {count} consecutive big poos (at change #{i+1}).")
        else:
            count = 0

    # Check for long intervals between changes
    recent_df = recent_df.sort_values("StartTime")
    recent_df["NextStartTime"] = recent_df["StartTime"].shift(-1)
    recent_df["Interval"] = (recent_df["NextStartTime"] - recent_df["StartTime"]).dt.total_seconds() / 3600
    long_intervals = recent_df[recent_df["Interval"] > max_interval_hours]
    for idx, row in long_intervals.iterrows():
        alerts.append(
            f"Interval from {row['StartTime']} to {row['NextStartTime']} exceeds {max_interval_hours} hours (actual {row['Interval']:.1f} hours)."
        )

    summary = (
        "No abnormalities detected." if not alerts
        else f"{len(alerts)} alert(s) found."
    )

    return {
        "summary": summary,
        "alerts": alerts,
        "recommendation": "Please pay attention to the alerts and adjust care plans as needed."
    }

from google.adk.agents import Agent

diaper_alert_agent = Agent(
    name="diaper_alert_agent",
    model="gemini-2.5-flash",
    description="An agent that detects abnormal diaper change patterns, such as consecutive big poos or excessive intervals between changes.",
    instruction="""
    You are a diaper alert agent.
    Your task is to identify abnormal excretion patterns, such as consecutive big poos or excessive time intervals without a change, to help with parent reminders.
    Use the analyze_diaper_alert tool to generate your report.
    """,
    tools=[analyze_diaper_alert],
)