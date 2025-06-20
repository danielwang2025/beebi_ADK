from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data  

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

    # Extract FeedType from standardized StartCondition
    def extract_feed_type(cond):
        if pd.isna(cond):
            return None
        cond = str(cond).strip().lower()
        if "formula" in cond:
            return "FormulaMilk"
        if "breast" in cond:
            return "BreastMilk"
        return None

    feed_df["FeedType"] = feed_df["StartCondition"].apply(extract_feed_type)

    return feed_df[["StartTime", "StartCondition", "Volume_ml", "FeedType"]]

def analyze_feed_type_ratio(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    if feed_df.empty or "FeedType" not in feed_df.columns:
        return {
            "summary": "No feeding records available for analysis.",
            "breast_milk_ratio": None,
            "formula_milk_ratio": None,
            "recommendation": "Please ensure feeding data is available."
        }

    now = feed_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = feed_df["StartTime"].min()

    recent_df = feed_df[(feed_df["StartTime"] >= start_date) & (feed_df["FeedType"].notnull())].copy()
    if recent_df.empty:
        return {
            "summary": f"No feeding type records found in the last {days if days else 'all'} days.",
            "breast_milk_ratio": None,
            "formula_milk_ratio": None,
            "recommendation": "Ensure feeding records include breast milk or formula milk information."
        }

    # Count and calculate ratio of breast milk and formula milk
    type_counts = recent_df["FeedType"].value_counts()
    total_feeds = type_counts.sum()

    breast_milk_count = type_counts.get("BreastMilk", 0)
    formula_milk_count = type_counts.get("FormulaMilk", 0)

    breast_milk_ratio = breast_milk_count / total_feeds if total_feeds else 0
    formula_milk_ratio = formula_milk_count / total_feeds if total_feeds else 0

    # Trend analysis
    recent_df['Date'] = recent_df['StartTime'].dt.date
    daily_ratio = recent_df.groupby('Date')['FeedType'].apply(
        lambda x: (x == "BreastMilk").sum() / len(x)
    )
    trend = "No significant change in breast milk ratio."
    if len(daily_ratio) >= 2:
        if daily_ratio.iloc[-1] > daily_ratio.iloc[0]:
            trend = "Breast milk ratio shows an increasing trend."
        elif daily_ratio.iloc[-1] < daily_ratio.iloc[0]:
            trend = "Breast milk ratio shows a decreasing trend."

    return {
        "summary": f"In the last {days if days else 'all'} days, the breast milk ratio is approximately {breast_milk_ratio:.0%}, and formula milk ratio is approximately {formula_milk_ratio:.0%}. {trend}",
        "breast_milk_ratio": round(breast_milk_ratio, 2),
        "formula_milk_ratio": round(formula_milk_ratio, 2),
        "recommendation": "Adjust your mixed feeding strategy accordingly based on the ratios."
    }

from google.adk.agents import Agent

feed_type_agent = Agent(
    name="feed_type_agent",
    model="gemini-2.5-flash",
    description="An agent that analyzes the ratio and trends of breast milk versus formula milk usage.",
    instruction="""
    You are a feed type analyst agent.
    Your task is to analyze the proportion and trends of breast milk and formula milk feeding over a specified period.
    Provide insights to guide mixed feeding strategies.
    Use the analyze_feed_type_ratio tool to generate your report.
    """,
    tools=[analyze_feed_type_ratio],
)
