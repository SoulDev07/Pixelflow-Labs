from textblob import TextBlob
from transformers import pipeline
from api_clients import logger

# Initialize sentiment analysis pipeline
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    logger.error(f"Failed to load transformer model: {e}")
    sentiment_analyzer = None

def analyze_sentiment_textblob(text):
    if not text:
        return {"polarity": 0, "subjectivity": 0}
    analysis = TextBlob(text)
    return {
        "polarity": analysis.sentiment.polarity,
        "subjectivity": analysis.sentiment.subjectivity
    }

def analyze_sentiment_transformers(text):
    if not sentiment_analyzer or not text:
        return {"label": "NEUTRAL", "score": 0.5}
    try:
        result = sentiment_analyzer(text[:512])[0]  # Limit text length for the model
        return result
    except Exception as e:
        logger.error(f"Transformer sentiment analysis error: {e}")
        return {"label": "NEUTRAL", "score": 0.5}

def get_aggregate_sentiment(texts):
    if not texts:
        return {
            "textblob": {"avg_polarity": 0, "avg_subjectivity": 0},
            "transformer": {"positive_percentage": 50, "avg_confidence": 0.5}
        }
    
    # TextBlob sentiment
    polarities = []
    subjectivities = []
    
    # Transformer sentiment
    positive_count = 0
    confidence_scores = []
    
    for text in texts:
        if text:
            # TextBlob analysis
            tb_sentiment = analyze_sentiment_textblob(text)
            polarities.append(tb_sentiment["polarity"])
            subjectivities.append(tb_sentiment["subjectivity"])
            
            # Transformer analysis
            if sentiment_analyzer:
                tf_sentiment = analyze_sentiment_transformers(text)
                if tf_sentiment["label"] == "POSITIVE":
                    positive_count += 1
                confidence_scores.append(tf_sentiment["score"])
    
    total = len(texts) if texts else 1
    
    return {
        "textblob": {
            "avg_polarity": sum(polarities) / len(polarities) if polarities else 0,
            "avg_subjectivity": sum(subjectivities) / len(subjectivities) if subjectivities else 0
        },
        "transformer": {
            "positive_percentage": (positive_count / total) * 100 if total > 0 else 50,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        }
    }
