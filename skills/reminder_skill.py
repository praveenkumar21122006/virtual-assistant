from datetime import datetime
from .base import BaseSkill
from nlp.entity_extractor import extract_reminder_details

class ReminderSkill(BaseSkill):
    name = "reminder"
    description = "Sets reminders"
    intents = ["reminder", "timer"]

    def __init__(self, memory):
        self.memory = memory

    def handle(self, text, intent, entities):
        task, when = extract_reminder_details(text)
        if task and when:
            self.memory.add_reminder(task, when)
            return f"⏰ Reminder set: **'{task}'** at **{when}**.\nI'll keep it in memory. (Persistent reminders stored in memory.json)"
        if intent == "timer":
            import re
            m = re.search(r"(\d+)\s*(second|minute|hour)", text, re.I)
            if m:
                val, unit = m.groups()
                self.memory.add_reminder(f"Timer {val} {unit}", f"in {val} {unit}")
                return f"⏱️ Timer set for {val} {unit}."
        # if no details, treat as general reminder add using todo logic
        if "remind me to" in text.lower():
            # try to salvage task without time
            task = text.lower().split("remind me to")[-1].strip(" .")
            if task:
                self.memory.add_reminder(task, "soon")
                return f"⏰ Noted reminder: **{task}**. When? Say 'remind me to {task} at 5pm'."
        reminders = self.memory.list_reminders()
        if reminders:
            lines = ["🔔 **Your Reminders:**"]
            for i, r in enumerate(reminders, 1):
                lines.append(f"{i}. {r['text']} — {r['when']}")
            return "\n".join(lines)
        return "⏰ I can set reminders. Try: 'remind me to call mom at 5pm' or 'remind me to drink water in 30 minutes'."
