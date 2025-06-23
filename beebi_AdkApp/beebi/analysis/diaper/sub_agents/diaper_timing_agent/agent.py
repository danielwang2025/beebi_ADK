from typing import Optional, Dict, Any
import pandas as pd

from beebi.data.db_utils import fetch_activity_data

def preprocess_diaper_timing_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Diaper", since_days=since_days)
    if df.empty:
        return df
    df["StartTime"] = pd.to_datetime(df["StartTime"])
    return df

def analyze_diaper_timing(
    days: Optional[int] = None,
    bins: Optional[int] = 6,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze the time-of-day distribution of diaper changes. `bins` is the number of time periods in a day (e.g., 6 means every 4 hours).
    """
    diaper_df = preprocess_diaper_timing_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "No diaper change records found. Unable to analyze timing distribution.",
            "timing_distribution": None,
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
            "timing_distribution": None,
            "recommendation": "Please ensure the data contains diaper change information."
        }

    # Extract hour
    recent_df["Hour"] = recent_df["StartTime"].dt.hour + recent_df["StartTime"].dt.minute / 60

    # Bin by time period
    bin_edges = [24 * i / bins for i in range(bins + 1)]
    bin_labels = [f"{int(bin_edges[i]):02d}:00-{int(bin_edges[i+1]):02d}:00" for i in range(bins)]
    recent_df["TimePeriod"] = pd.cut(recent_df["Hour"], bins=bin_edges, labels=bin_labels, right=False, include_lowest=True)

    timing_distribution = recent_df["TimePeriod"].value_counts().sort_index().to_dict()

    # Check for concentration
    max_period = max(timing_distribution, key=timing_distribution.get)
    max_count = timing_distribution[max_period]
    total = sum(timing_distribution.values())
    concentration = max_count / total if total else 0

    if concentration > 0.4:
        pattern = f"Change times are mainly concentrated in {max_period}."
    else:
        pattern = "Change times are relatively evenly distributed."

    summary = (
        f"In the last {days if days else 'all'} days, the distribution of diaper change times is as follows: {timing_distribution}. {pattern}"
    )

    return {
        "summary": summary,
        "timing_distribution": timing_distribution,
        "recommendation": "Pay attention to whether there is a concentration or irregularity in change times, and arrange care accordingly."
    }

from google.adk.agents import Agent

diaper_timing_agent = Agent(
    name="diaper_timing_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes the time-of-day distribution of diaper changes and detects patterns.",
    instruction="""
    You are a diaper timing analysis agent.
    Your task is to analyze the distribution of diaper changes throughout the day (e.g., whether they are concentrated in certain periods or regular).
    Use the analyze_diaper_timing tool to generate your report.
    """,
    tools=[analyze_diaper_timing],
)