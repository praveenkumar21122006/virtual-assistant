import re
from typing import Tuple, Dict

# Rule-based intent classifier with confidence scoring
# Falls back to TF-IDF + LogisticRegression if sklearn available

INTENT_PATTERNS = {
    "greeting": [r"\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b"],
    "goodbye": [r"\b(bye|goodbye|see you|farewell|exit|quit)\b"],
    "weather": [r"\b(weather|temperature|forecast|humidity|rain|sunny|cloudy)\b"],
    "time": [r"\b(time|clock|current time)\b"],
    "date": [r"\b(date|today|day is it|calendar)\b"],
    "calculator": [r"(\d+\s*[\+\-\*\/\^%]\s*\d+|calculate|compute|what is \d|solve|math)"],
    "reminder": [r"\b(remind|reminder|alarm|notify).*\b(at|in|on)\b", r"remind me to .+ at\b", r"remind me to .+ in \d+"],
    "todo_add": [r"\b(add|create).*(todo|task)|remind me to\b"],
    "todo_list": [r"\b(list|show|display).*(todo|task|reminder)|what.*todo\b"],
    "todo_complete": [r"\b(complete|done|finish|mark).*(task|todo)|\btodo.*done\b"],
    "todo_clear": [r"\b(clear|delete all|remove all).*(todo|task)"],
    "wikipedia": [r"\b(who is|what is|tell me about|wikipedia|search for|look up)\b"],
    "joke": [r"\b(joke|funny|make me laugh|humor)\b"],
    "help": [r"\b(help|what can you do|capabilities|features|commands)\b"],
    "name_query": [r"\b(your name|who are you|what are you)\b"],
    "set_name": [r"\b(my name is|call me|i am called)\b"],
    "web_search": [r"\b(search|google|browse|find online)\b"],
    "translation": [r"\b(translate|translation)\b"],
    "timer": [r"\b(timer|countdown|set.*\d+.*(second|minute|hour))\b"],
}

# Optional ML classifier
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class IntentClassifier:
    def __init__(self):
        self.patterns = {k: [re.compile(p, re.I) for p in v] for k, v in INTENT_PATTERNS.items()}
        self.ml_model = None
        self.vectorizer = None
        if SKLEARN_AVAILABLE:
            self._train_ml()

    def _train_ml(self):
        # Tiny synthetic training set for ML fallback
        training_data = {
            "greeting": ["hello", "hi there", "hey assistant", "good morning", "greetings"],
            "goodbye": ["bye", "goodbye", "see you later", "exit", "quit"],
            "weather": ["what's the weather like", "weather in London", "is it going to rain", "temperature outside"],
            "time": ["what time is it", "current time", "tell me the time"],
            "date": ["what date is today", "what day is it", "today's date"],
            "calculator": ["calculate 5+5", "what is 12*8", "solve 100/4", "compute 2^10"],
            "todo_add": ["add buy milk to my todo", "create task call mom", "remind me to do homework"],
            "todo_list": ["show my todos", "list my tasks", "what are my todos"],
            "wikipedia": ["who is Albert Einstein", "what is quantum physics", "tell me about Python programming"],
            "joke": ["tell me a joke", "make me laugh", "say something funny"],
            "help": ["help me", "what can you do", "show capabilities"],
            "web_search": ["search for python tutorials", "google AI news"],
        }
        texts, labels = [], []
        for intent, examples in training_data.items():
            for ex in examples:
                texts.append(ex)
                labels.append(intent)
        try:
            self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
            X = self.vectorizer.fit_transform(texts)
            self.ml_model = LogisticRegression(max_iter=500)
            self.ml_model.fit(X, labels)
        except Exception:
            self.ml_model = None

    def classify(self, text: str) -> Tuple[str, float, Dict]:
        text = text.strip()
        if not text:
            return "unknown", 0.0, {}

        # Rule-based first
        scores = {}
        for intent, regex_list in self.patterns.items():
            score = 0
            for rx in regex_list:
                if rx.search(text):
                    score += 1
            if score:
                scores[intent] = score

        if scores:
            best = max(scores, key=lambda k: scores[k])
            # Normalize confidence: 0.85 if matched, higher if multiple patterns
            confidence = min(0.85 + 0.05 * (scores[best]-1), 0.95)
            return best, confidence, scores

        # ML fallback
        if self.ml_model and self.vectorizer:
            try:
                X = self.vectorizer.transform([text])
                probs = self.ml_model.predict_proba(X)[0]
                idx = probs.argmax()
                confidence = float(probs[idx])
                intent = self.ml_model.classes_[idx]
                if confidence > 0.35:
                    return intent, confidence, {"ml": True}
            except Exception:
                pass

        # Default -> treat as general chat / wikipedia / web_search
        # Heuristic: if question word, route to wikipedia
        if re.search(r"\b(what|who|where|when|why|how|explain|define)\b", text, re.I):
            return "wikipedia", 0.45, {}
        return "chat", 0.5, {}
