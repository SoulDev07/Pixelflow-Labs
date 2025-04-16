import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from api_clients import logger

# Download NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK resources: {e}")

def preprocess_text(text):
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

def extract_hashtags(text):
    if not text:
        return []
    # Find all hashtags in the text
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def remove_stopwords(text):
    if not text:
        return ""
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered_text)

def get_top_words(texts, n=10):
    """Get top N words from a list of texts"""
    # Initialize Counter
    word_counts = Counter()
    
    # Get stopwords
    stop_words = set(stopwords.words('english'))
    
    for text in texts:
        if not isinstance(text, str):
            continue
            
        # Tokenize and clean text
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = word_tokenize(text)
        
        # Filter words
        words = [word for word in words 
                if word.isalnum() 
                and len(word) > 2 
                and word not in stop_words]
        
        # Update counter
        word_counts.update(words)
    
    # Return top N words
    return dict(word_counts.most_common(n))

def is_domain_related(text, domain_keywords):
    if not text or not domain_keywords:
        return False
    
    text = text.lower()
    for keyword in domain_keywords:
        if keyword.lower() in text:
            return True
    return False
