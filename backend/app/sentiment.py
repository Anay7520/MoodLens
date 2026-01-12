from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis")

def sentiment_analysis(text: str):
    result = sentiment_analyzer(text)
    return result
