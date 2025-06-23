from beebi.analysis.sleep.sleep import analyze_sleep_sessions

if __name__ == "__main__":
    result = analyze_sleep_sessions(days=7, customer_id=10)
    print("Sleep Analysis Result:")
    print(result)
