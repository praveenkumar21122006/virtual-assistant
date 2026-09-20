from .base import BaseSkill
from nlp.entity_extractor import extract_todo_task

class TodoSkill(BaseSkill):
    name = "todo"
    description = "Manages todo list"
    intents = ["todo_add", "todo_list", "todo_complete", "todo_clear"]

    def __init__(self, memory):
        self.memory = memory

    def handle(self, text, intent, entities):
        if intent == "todo_add":
            task = extract_todo_task(text)
            if not task:
                return "📝 What task should I add? Say 'add buy milk to my todo'."
            self.memory.add_todo(task)
            return f"✅ Added to your todos: **{task}**"

        elif intent == "todo_list":
            todos = self.memory.list_todos()
            if not todos:
                return "📭 Your todo list is empty. Add one with 'add [task] to my todo'."
            lines = ["📋 **Your Todos:**"]
            for i, t in enumerate(todos, 1):
                status = "✓" if t["done"] else "○"
                style = "~~" if t["done"] else ""
                lines.append(f"{i}. {status} {style}{t['task']}{style}")
            return "\n".join(lines)

        elif intent == "todo_complete":
            # try to parse index: "complete task 1" or "mark todo 2 as done"
            import re
            m = re.search(r"(\d+)", text)
            if m:
                idx = int(m.group(1)) - 1
                if self.memory.complete_todo(idx):
                    return f"✅ Marked task {idx+1} as done!"
                else:
                    return "❌ Invalid task number."
            # try to match by name
            todos = self.memory.list_todos()
            for i, t in enumerate(todos):
                if t["task"].lower() in text.lower() and not t["done"]:
                    self.memory.complete_todo(i)
                    return f"✅ Completed: {t['task']}"
            return "❓ Which task? Say 'complete task 1' or 'complete buy milk'."

        elif intent == "todo_clear":
            self.memory.clear_todos()
            return "🗑️ Cleared all todos."

        return "Todo skill error."
