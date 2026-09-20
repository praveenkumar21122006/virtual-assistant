import random
from .base import BaseSkill
from config import Config

RESPONSES = {
    "greeting": [
        "Hello! 👋 I'm {name}, your AI virtual assistant. How can I help you today?",
        "Hey there! ✨ {name} at your service. What would you like to do?",
        "Hi! 😊 Ready to assist you — try 'help' to see what I can do.",
    ],
    "goodbye": [
        "Goodbye! 👋 Have a great day!",
        "See you soon! ✨ Come back anytime.",
        "Bye! Take care! 😊",
    ],
    "name_query": [
        "I'm {name} — an AI-powered virtual assistant built to understand your queries, perform tasks, and provide information. 🤖",
        "They call me {name}! I can manage todos, answer questions, do calculations, check weather, and more. Try 'help'.",
    ],
    "help": [
        """🤖 **I'm {name} — Here's what I can do:**

**🗣️ Understand & Respond:**
- Natural language queries (Wikipedia, web search, general chat)

**📌 Tasks:**
- `add [task] to my todo` / `list my todos` / `complete task 1`
- `remind me to [task] at [time]` / `timer 5 minutes`
- `calculate 12*8 + 5` / `what is 100/4?`

**ℹ️ Information:**
- `what's the weather in Paris?` (live with API key, mock otherwise)
- `what time is it?` / `what date is today?`
- `who is Alan Turing?` / `tell me about quantum computing`
- `search for Python tutorials`
- `tell me a joke`

**⚙️ System:**
- `my name is Alex` — I'll remember you
- `help` — this menu
- `bye` / `exit` — quit

_All data is stored locally in memory.json. Add OPENAI_API_KEY / WEATHER_API_KEY in .env for enhanced AI & live weather._"""
    ],
}

class SmallTalkSkill(BaseSkill):
    name = "smalltalk"
    description = "Handles greetings, help, identity"
    intents = ["greeting", "goodbye", "name_query", "help", "set_name"]

    def __init__(self, memory):
        self.memory = memory

    def handle(self, text, intent, entities):
        from nlp.entity_extractor import extract_name
        name = Config.ASSISTANT_NAME

        if intent == "set_name":
            user_name = extract_name(text)
            if user_name:
                self.memory.set_user_name(user_name)
                return f"Nice to meet you, **{user_name}**! I'll remember your name. 😊"
            return "What's your name? Say 'my name is ...'"

        if intent in RESPONSES:
            template = random.choice(RESPONSES[intent])
            msg = template.format(name=name)
            if self.memory.get_user_name() and intent == "greeting":
                msg += f" Welcome back, **{self.memory.get_user_name()}**!"
            return msg
        return random.choice(RESPONSES["greeting"]).format(name=name)
