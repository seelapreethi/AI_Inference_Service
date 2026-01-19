import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Simple dataset
texts = [
    "I love this movie",
    "This film was amazing",
    "Worst movie ever",
    "I hated this movie",
    "It was okay, not great",
    "The movie was fine"
]

labels = ["positive", "positive", "negative", "negative", "neutral", "neutral"]

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

texts = [preprocess(t) for t in texts]

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

joblib.dump(model, "models/sentiment_model.pkl")
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")

print("Model and vectorizer saved successfully.")
