from src.preprocessing.nlp_preprocessor import download_nltk_resources
import nltk
try:
    download_nltk_resources()
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger_eng')
    print("NLTK resources verified.")
except Exception as e:
    print(f"Error verifying NLTK resources: {e}")
