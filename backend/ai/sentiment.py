from transformers import pipeline

class SentimentAI:
    def __init__(self):
        # Using a free-tier compatible model from HuggingFace
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

    def analyze_text(self, text: str):
        result = self.sentiment_pipeline(text)
        # Returns [{'label': 'positive', 'score': 0.99}]
        return result[0]

    def aggregate_sentiment(self, articles: list):
        scores = []
        for article in articles:
            res = self.analyze_text(article)
            score = res["score"] if res["label"] == "positive" else -res["score"] if res["label"] == "negative" else 0
            scores.append(score)
        return sum(scores) / len(scores) if scores else 0
