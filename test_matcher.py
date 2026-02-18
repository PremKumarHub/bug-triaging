
from src.utils.developer_matcher import DeveloperMatcher

def test_matcher():
    devs = [
        {"id": 1, "username": "alice_s", "full_name": "Alice Smith", "email": "alice@company.com"},
        {"id": 2, "username": "bob-dev", "full_name": "Bob Jones", "email": "bjones@company.com"},
        {"id": 3, "username": "charlie", "full_name": "Charlie Chaplin", "email": "cchap@company.com"}
    ]
    matcher = DeveloperMatcher(devs)
    
    test_cases = [
        "Alice-Smith",       # Rule 1: Normalize names (hyphens)
        "alice_s",           # Role 2b: Match username
        "bjones",            # Rule 2c: Match email prefix
        "BOB JONES",         # Rule 3: Case-insensitive
        "Charlie C",         # Fuzzy Match
        "UnknownUser",       # NO_ASSIGNEE_FOUND
        "none"               # NO_ASSIGNEE_FOUND
    ]
    
    print("\nStarting Developer Matcher Verification...")
    for case in test_cases:
        res = matcher.match(case)
        print(f"Input: {case:<15} -> Result: {res['status']:<20} Match: {res['matched_developer_name']} Score: {res['similarity_score']:.2f}")

if __name__ == "__main__":
    test_matcher()
