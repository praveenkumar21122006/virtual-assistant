from datetime import datetime
from .base import BaseSkill

class DateTimeSkill(BaseSkill):
    name = "datetime"
    description = "Provides current time and date"
    intents = ["time", "date"]

    def handle(self, text, intent, entities):
        now = datetime.now()
        if intent == "time":
            return f"🕒 Current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."
        elif intent == "date":
            return f"📅 Today is {now.strftime('%A, %B %d, %Y')}. Time is {now.strftime('%I:%M %p')}."
        return f"⏰ It's {now.strftime('%c')}."
