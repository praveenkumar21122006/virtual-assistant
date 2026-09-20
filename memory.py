import json
import os
from datetime import datetime
from collections import deque

class Memory:
    """Conversation memory + persistent storage for todos, reminders, preferences."""
    def __init__(self, filepath="memory.json", max_history=20):
        self.filepath = filepath
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.data = {
            "todos": [],
            "reminders": [],
            "preferences": {},
            "user_name": None,
            "conversations": []
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
                    # restore history from conversations
                    for c in loaded.get("conversations", [])[-self.max_history:]:
                        self.history.append(c)
            except Exception:
                pass

    def save(self):
        try:
            self.data["conversations"] = list(self.history)
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[Memory] Save failed: {e}")

    def add_exchange(self, user_input, assistant_response, intent=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "intent": intent
        }
        self.history.append(entry)
        self.save()

    def get_history(self, n=5):
        return list(self.history)[-n:]

    def set_user_name(self, name):
        self.data["user_name"] = name
        self.save()

    def get_user_name(self):
        return self.data["user_name"]

    # Todo helpers
    def add_todo(self, task):
        self.data["todos"].append({"task": task, "done": False, "created": datetime.now().isoformat()})
        self.save()

    def list_todos(self):
        return self.data["todos"]

    def complete_todo(self, index):
        if 0 <= index < len(self.data["todos"]):
            self.data["todos"][index]["done"] = True
            self.save()
            return True
        return False

    def remove_todo(self, index):
        if 0 <= index < len(self.data["todos"]):
            self.data["todos"].pop(index)
            self.save()
            return True
        return False

    def clear_todos(self):
        self.data["todos"] = []
        self.save()

    # Reminder helpers
    def add_reminder(self, text, when_str):
        self.data["reminders"].append({"text": text, "when": when_str, "created": datetime.now().isoformat()})
        self.save()

    def list_reminders(self):
        return self.data["reminders"]
