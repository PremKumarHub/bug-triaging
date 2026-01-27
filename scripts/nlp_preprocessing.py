import json
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# =====================================================
# NLTK SETUP (Auto-Download safe check)
# =====================================================
def download_nltk_resources():
    resources = ["stopwords", "wordnet", "omw-1.4", "punkt", "averaged_perceptron_tagger"]
    for res in resources:
        try:
            nltk.data.find(f"tokenizers/{res}") if res == "punkt" else nltk.data.find(f"corpora/{res}")
        except LookupError:
            nltk.download(res, quiet=True)

download_nltk_resources()

# =====================================================
# FILE PATHS
# =====================================================
INPUT_FILE = "data/processed/bug_reports_structurally_cleaned.json"
OUTPUT_FILE = "data/processed/bug_reports_nlp_ready.json"

# =====================================================
# STOPWORDS (DOMAIN-SAFE)
# =====================================================
STOP_WORDS = set(stopwords.words("english"))
# Words to KEEP because they indicate the nature of the bug
DOMAIN_KEEP = {
    "not", "no", "never", "none",
    "error", "fail", "failed", "failure", 
    "bug", "crash", "issue", "exception",
    "slow", "lag", "freeze", "frozen"
}
STOP_WORDS -= DOMAIN_KEEP

lemmatizer = WordNetLemmatizer()

# =====================================================
# PROTECTION RULES & REGEX
# =====================================================

# 1. Tech Terms
LANGUAGE_MAP = {
    "c++": "lang_cpp",
    "c#": "lang_csharp", 
    "f#": "lang_fsharp",
    ".net": "framework_dotnet"
}

PRODUCT_MAP = {
    "vs code": "product_vscode",
    "visual studio code": "product_vscode",
    "node.js": "tech_nodejs",
    "vue.js": "tech_vuejs"
}

# 2. Versions: Matches 1.10.1, v2.0, 2024.1
VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+)+\b")

# 3. Hotkeys: Matches "ctrl+s", "ctrl+shift+p", "cmd+k"
# Updated to handle multiple modifiers and numbers
HOTKEY_RE = re.compile(r"\b(?:ctrl|alt|shift|cmd|meta)(?:\+[a-z0-9]+)+\b", re.IGNORECASE)

# 4. Token Pattern: Alphanumeric + Underscore (to keep protected tokens)
TOKEN_RE = re.compile(r"[a-z0-9_]+")

# Helper for Smart Lemmatization
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'): return wordnet.ADJ
    elif treebank_tag.startswith('V'): return wordnet.VERB
    elif treebank_tag.startswith('N'): return wordnet.NOUN
    elif treebank_tag.startswith('R'): return wordnet.ADV
    else: return wordnet.NOUN

# =====================================================
# NLP FUNCTION
# =====================================================
def nlp_process(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # ---- 1. Protect Strings (Order matters!) ----
    for k, v in PRODUCT_MAP.items():
        text = text.replace(k, v)
        
    for k, v in LANGUAGE_MAP.items():
        text = text.replace(k, v)

    # ---- 2. Protect Patterns (Regex) ----
    # Normalize versions: 1.10.1 -> version_1_10_1
    text = VERSION_RE.sub(lambda m: f"version_{m.group(0).replace('.', '_').replace('v', '')}", text)
    
    # Normalize hotkeys: ctrl+shift+p -> hotkey_ctrl_shift_p
    text = HOTKEY_RE.sub(lambda m: f"hotkey_{m.group(0).replace('+', '_')}", text)

    # ---- 3. Tokenize & Tag ----
    # We use NLTK's word_tokenize first to handle sentence structure better than regex
    tokens = word_tokenize(text)
    
    # Get POS Tags (Essential for converting 'running' -> 'run')
    pos_tags = nltk.pos_tag(tokens)

    processed_tokens = []

    for word, tag in pos_tags:
        # Clean the word (remove leftover punctuation)
        clean_word = "".join(TOKEN_RE.findall(word))
        
        if not clean_word: 
            continue
            
        # ---- 4. Stopword Removal ----
        if clean_word in STOP_WORDS:
            continue

        # ---- 5. Smart Lemmatization ----
        wn_tag = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(clean_word, pos=wn_tag)
        
        # Length check (keep single letters only if they are numbers)
        if len(lemma) > 1 or lemma.isdigit():
            processed_tokens.append(lemma)

    return " ".join(processed_tokens)

# =====================================================
# EXECUTION
# =====================================================
print("Loading data...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Processing {len(data)} records...")

for i, issue in enumerate(data):
    # Progress check for large files
    if (i+1) % 500 == 0: print(f"   ... {i+1} processed")
    
    issue["nlp_title"] = nlp_process(issue.get("title", ""))
    issue["nlp_body"] = nlp_process(issue.get("body", ""))
    issue["combined_text"] = f"{issue['nlp_title']} {issue['nlp_body']}".strip()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Perfected NLP preprocessing completed.")
print("Output saved to:", OUTPUT_FILE)