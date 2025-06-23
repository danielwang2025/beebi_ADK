from beebi.data.db_utils import fetch_activity_data

def test_fetch():
    try:
        df = fetch_activity_data(customer_id=10, activity_type="Sleep", since_days=30)
        print("✅ Data fetch successful!")
        print(df.head())
        print(f"\nTotal records: {len(df)}")
    except Exception as e:
        print("❌ Error during data fetch:")
        print(e)

if __name__ == "__main__":
    test_fetch()
