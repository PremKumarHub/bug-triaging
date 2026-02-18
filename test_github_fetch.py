
from src.data_collection.github_collector import fetch_bugs_from_github
import json

def test_fetch():
    print("Testing GitHub Fetch...")
    try:
        issues = fetch_bugs_from_github(total_limit=2, state="open")
        print(f"Successfully fetched {len(issues)} issues.")
        if issues:
            print("First issue title:", issues[0]['title'])
        else:
            print("No issues returned. Check the prints above for API errors.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_fetch()
