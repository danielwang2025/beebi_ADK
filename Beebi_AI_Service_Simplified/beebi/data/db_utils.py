import os
import pandas as pd
import pymssql


def get_connection():
    server = "beebi.database.windows.net"
    database = "beebi"
    username = "jeromexshi"
    password = "%Jumpswim123"

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
    Always fetch activity data from Azure SQL for a specific customer.
    """
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
