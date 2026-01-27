import json
import re
import os

INPUT_FILE = "data/processed/bug_reports_cleaned.json"
OUTPUT_FILE = "data/processed/bug_reports_cleaned.json"

# =====================================================
# ROBUST CLEANING FUNCTION
# =====================================================
def clean_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return ""

    # 1. Remove collapsible blocks (Logs, System Info)
    text = re.sub(r"<details[\s\S]*?</details>", " ", text, flags=re.IGNORECASE)

    # 2. Remove broken or partial image tags
    text = re.sub(r"<img[^>]*>", " ", text, flags=re.IGNORECASE)

    # 3. Remove Markdown images ![alt](url)
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)

    # 4. Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    
    # 5. Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # 6. Normalize case
    text = text.lower()

    # --- NEW ADDITION: Remove Emoji Shortcodes (:bug:, :warning:) ---
    # We look for words between colons.
    # We require at least one letter [a-z] to avoid deleting timestamps like 14:58:46.
    # Matches: :bug:, :smile_cat:, :v1:
    # Ignores: :58:, :30:
    text = re.sub(r":[a-z0-9_\-]*[a-z][a-z0-9_\-]*:", " ", text)

    # 7. Remove boilerplate phrases
    boilerplate_phrases = [
        "add issue description here",
        "please search existing issues",
        "does this issue occur when all extensions are disabled",
        "type: bug",
        "type: feature request",
        "steps to reproduce:", 
    ]

    for phrase in boilerplate_phrases:
        text = text.replace(phrase.lower(), " ")

    # 8. Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text

# =====================================================
# APPLY CLEANING
# =====================================================
if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} not found.")
    exit()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

modified_count = 0

for issue in data:
    original_title = issue.get("title", "")
    original_body = issue.get("body", "")

    cleaned_title = clean_text(original_title)
    cleaned_body = clean_text(original_body)

    if cleaned_title != original_title or cleaned_body != original_body:
        modified_count += 1

    issue["title"] = cleaned_title
    issue["body"] = cleaned_body

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("CLEANING REPORT")
print("--------------------------------")
print(f"Records modified: {modified_count}")
print("Cleaning completed successfully")