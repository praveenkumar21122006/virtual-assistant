import re
import requests
from config import Config
from memory import Memory
from nlp.intent_classifier import IntentClassifier
from nlp.entity_extractor import extract_name
from skills.datetime_skill import DateTimeSkill
from skills.calculator_skill import CalculatorSkill
from skills.todo_skill import TodoSkill
from skills.weather_skill import WeatherSkill
from skills.wikipedia_skill import WikipediaSkill
from skills.joke_skill import JokeSkill
from skills.reminder_skill import ReminderSkill
from skills.web_search_skill import WebSearchSkill
from skills.smalltalk_skill import SmallTalkSkill

class VirtualAssistant:
    """Core assistant orchestrating NLU + skills + optional LLM."""

    def __init__(self, memory_file=None):
        self.memory = Memory(filepath=memory_file or Config.MEMORY_FILE)
        self.classifier = IntentClassifier()
        # init skills
        self.skills = {}
        self._register_skills()
        self.llm_enabled = bool(Config.OPENAI_API_KEY)

    def _register_skills(self):
        dt = DateTimeSkill()
        calc = CalculatorSkill()
        todo = TodoSkill(self.memory)
        weather = WeatherSkill()
        wiki = WikipediaSkill()
        joke = JokeSkill()
        reminder = ReminderSkill(self.memory)
        web = WebSearchSkill()
        smalltalk = SmallTalkSkill(self.memory)

        for s in [smalltalk, dt, calc, todo, weather, wiki, joke, reminder, web]:
            for intent in s.intents:
                self.skills[intent] = s
        # fallback chat uses wikipedia
        self.skills["chat"] = wiki
        self.wiki_skill = wiki

    def _call_llm(self, text: str) -> str | None:
        """Optional OpenAI enhancement. Returns None if not configured/failed."""
        if not self.llm_enabled:
            return None
        try:
            headers = {"Authorization": f"Bearer {Config.OPENAI_API_KEY}", "Content-Type": "application/json"}
            hist = self.memory.get_history(4)
            messages = [{"role": "system", "content": f"You are {Config.ASSISTANT_NAME}, a helpful AI virtual assistant. Be concise, friendly, and useful. User name is {self.memory.get_user_name() or 'unknown'}."}]
            for h in hist:
                messages.append({"role": "user", "content": h["user"]})
                messages.append({"role": "assistant", "content": h["assistant"]})
            messages.append({"role": "user", "content": text})
            payload = {"model": Config.OPENAI_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 400}
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[LLM] error: {e}")
        return None

    def process(self, text: str) -> dict:
        """Process user input -> response dict."""
        text = text.strip()
        if not text:
            return {"intent": "unknown", "confidence": 0, "response": "Say something! Try 'help'."}

        # check for name setting early via regex to improve recall
        if re.search(r"\b(my name is|call me)\b", text, re.I):
            intent, conf, scores = "set_name", 0.9, {}
        else:
            intent, conf, scores = self.classifier.classify(text)

        # try LLM first for open-ended chat if enabled and intent is chat/wikipedia with low confidence
        llm_response = None
        if intent in ("chat", "wikipedia") and self.llm_enabled and conf < 0.6:
            llm_response = self._call_llm(text)
            if llm_response:
                self.memory.add_exchange(text, llm_response, intent="llm_chat")
                return {"intent": "llm_chat", "confidence": 0.9, "response": llm_response, "llm": True}

        skill = self.skills.get(intent)
        if skill:
            try:
                resp = skill.handle(text, intent, entities={})
            except Exception as e:
                resp = f"⚠️ Skill '{skill.name}' error: {e}"
        else:
            # generic fallback: try LLM then wikipedia
            if self.llm_enabled:
                llm_response = self._call_llm(text)
                if llm_response:
                    resp = llm_response
                    intent = "llm_chat"
                else:
                    resp = self.wiki_skill.handle(text, "wikipedia", {})
            else:
                resp = self.wiki_skill.handle(text, "wikipedia", {})

        self.memory.add_exchange(text, resp, intent=intent)
        return {"intent": intent, "confidence": round(conf, 2), "response": resp}

    def get_todos(self):
        return self.memory.list_todos()

    def get_reminders(self):
        return self.memory.list_reminders()

    def get_history(self, n=10):
        return self.memory.get_history(n)
