import random
import requests
from .base import BaseSkill

FALLBACK_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything! 😄",
    "I told my computer I needed a break, and it said 'No problem, I'll go to sleep.' 💻",
    "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
    "Parallel lines have so much in common... it's a shame they'll never meet. 📏",
    "Why don't eggs tell jokes? They'd crack each other up! 🥚",
    "I would tell you a UDP joke, but you might not get it. 🌐",
]

class JokeSkill(BaseSkill):
    name = "joke"
    description = "Tells jokes"
    intents = ["joke"]

    def handle(self, text, intent, entities):
        try:
            r = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=3)
            if r.status_code == 200:
                j = r.json()
                return f"😂 {j.get('setup','')} \n{j.get('punchline','')}"
        except Exception:
            pass
        return random.choice(FALLBACK_JOKES)
