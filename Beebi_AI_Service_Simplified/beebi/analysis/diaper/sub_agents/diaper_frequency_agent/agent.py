from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data

def preprocess_diaper_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
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
    return df

def analyze_diaper_frequency(
    days: Optional[int] = None,
    by_user: bool = False,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    diaper_df = preprocess_diaper_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "No diaper change records found. Unable to analyze frequency.",
            "details": None,
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
            "details": None,
            "recommendation": "Please ensure the data contains diaper change information."
        }

    # Group by user if needed
    group_fields = ["CustomerID"] if by_user else []
    recent_df["Date"] = recent_df["StartTime"].dt.date

    freq_stats = recent_df.groupby(group_fields + ["Date"]).size().reset_index(name="ChangeCount")
    if group_fields:
        avg_per_day = freq_stats.groupby(group_fields)["ChangeCount"].mean().reset_index(name="AvgChangePerDay")
        avg_per_day_records = avg_per_day.to_dict(orient="records")
        summary = f"In the last {days if days else 'all'} days, the average number of diaper changes per day is {avg_per_day['AvgChangePerDay'].mean():.1f} (by user)."
    else:
        avg = freq_stats["ChangeCount"].mean()
        avg_per_day_records = [{"AvgChangePerDay": avg}]
        summary = f"In the last {days if days else 'all'} days, the average number of diaper changes per day is {avg:.1f}."

    # Pee/poo type distribution
    pee_stats = recent_df["Pee"].value_counts(dropna=True).to_dict()
    poo_stats = recent_df["Poo"].value_counts(dropna=True).to_dict()

    if by_user:
        summary += " (by user)"

    return {
        "summary": summary,
        "avg_per_day": avg_per_day_records,
        "pee_stats": pee_stats,
        "poo_stats": poo_stats,
        "recommendation": "It is recommended to adjust care plans based on change frequency and pee/poo volume."
    }

from google.adk.agents import Agent

diaper_frequency_agent = Agent(
    name="diaper_frequency_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes diaper change frequency and pee/poo amount trends.",
    instruction="""
    You are a diaper frequency analyst agent.
    Your task is to analyze the frequency of diaper changes (daily, by period, by user) and the distribution of pee/poo amounts (small, medium, big).
    Use the analyze_diaper_frequency tool to generate your report.
    """,
    tools=[analyze_diaper_frequency],
)