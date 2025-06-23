import os
import pandas as pd
import pymssql
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "/workspaces/beebi_ADK/beebi/data/db_utils.py"

def get_connection():
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DB")
    username = os.getenv("AZURE_SQL_USER")
    password = os.getenv("AZURE_SQL_PASSWORD")
    return pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        port=1433
    )

def fetch_activity_data(
    customer_id=10,
    activity_type=None,
    since_days=365
) -> pd.DataFrame:
    """
    Fetch activity data for a specific customer over a recent period (default 365 days),
    prioritizing local CSV file. If CSV not found, fallback to database extraction.
    """
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, parse_dates=["StartTime", "EndTime"])

        # Apply consistent filtering logic
        df = df[df["CustomerID"] == customer_id]
        df = df[df["StartTime"] >= pd.Timestamp.now() - pd.Timedelta(days=since_days)]
        if activity_type:
            df = df[df["Type"] == activity_type]
        df = df.sort_values(by="StartTime")
        return df

    # Fallback: fetch from database
    conn = get_connection()
    query = """
        SELECT ActivityID, CustomerID, Type, StartTime, EndTime, Duration,
               StartCondition, StartLocation, EndCondition, Notes
        FROM dbo.Activity
        WHERE CustomerID = %s AND StartTime >= DATEADD(day, -%s, GETDATE())
    """
    params = [customer_id, since_days]
    if activity_type:
        query += " AND Type = %s"
        params.append(activity_type)
    query += " ORDER BY StartTime ASC"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
