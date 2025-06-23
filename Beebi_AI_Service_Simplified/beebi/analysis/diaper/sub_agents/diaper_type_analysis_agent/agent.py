from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data  # Use database utility to fetch data

def preprocess_diaper_type_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Diaper", since_days=since_days)
    if df.empty:
        return df
    df["StartTime"] = pd.to_datetime(df["StartTime"])

    # Extract pee and poo types
    def extract_condition(cond, kind):
        if pd.isna(cond):
            return None
        cond = str(cond).lower()
        match = re.search(rf"{kind}:(small|medium|big)", cond)
        return match.group(1) if match else None

    df["PeeType"] = df["EndCondition"].apply(lambda x: extract_condition(x, "pee"))
    df["PooType"] = df["EndCondition"].apply(lambda x: extract_condition(x, "poo"))
    return df

def analyze_diaper_type(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    diaper_df = preprocess_diaper_type_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "No diaper content records found. Unable to analyze pee/poo types.",
            "pee_stats": None,
            "poo_stats": None,
            "recommendation": "Please ensure there is diaper content data."
        }

    now = diaper_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = diaper_df["StartTime"].min()

    recent_df = diaper_df[diaper_df["StartTime"] >= start_date].copy()
    if recent_df.empty:
        return {
            "summary": f"No diaper content records in the last {days if days else 'all'} days.",
            "pee_stats": None,
            "poo_stats": None,
            "recommendation": "Please ensure there is diaper content information in the data."
        }

    # Count distribution of pee/poo types
    pee_stats = recent_df["PeeType"].value_counts(dropna=True).to_dict()
    poo_stats = recent_df["PooType"].value_counts(dropna=True).to_dict()

    summary = (
        f"In the last {days if days else 'all'} days, "
        f"there are {sum(pee_stats.values())} records with pee, "
        f"and {sum(poo_stats.values())} records with poo."
    )

    return {
        "summary": summary,
        "pee_stats": pee_stats,
        "poo_stats": poo_stats,
        "recommendation": "Pay attention to the distribution of pee/poo types and detect abnormalities in time."
    }

from google.adk.agents import Agent

diaper_type_analysis_agent = Agent(
    name="diaper_type_analysis_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes diaper content types: whether there is pee or poo, and their levels (small/medium/big).",
    instruction="""
    You are a diaper type analysis agent.
    Your task is to analyze whether each diaper change contains pee or poo, and their respective levels (small, medium, big).
    Use the analyze_diaper_type tool to generate your report.
    """,
    tools=[analyze_diaper_type],
)