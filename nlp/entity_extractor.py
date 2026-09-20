import re
from datetime import datetime, timedelta
import dateutil.parser as dparser

def extract_numbers(text):
    return re.findall(r"-?\d+\.?\d*", text)

def extract_calculation(text):
    # extract math expression like "12 * 8" or "calculate 5+5"
    # allow words: plus, minus, times, divided, power, etc.
    t = text.lower()
    t = t.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("x", "*")
    t = t.replace("divided by", "/").replace("divide", "/").replace("multiplied by", "*")
    t = t.replace("power", "^").replace("mod", "%")
    # find expression pattern
    m = re.search(r"([-+]?\d*\.?\d+\s*[\+\-\*\/\^%]\s*[-+]?\d*\.?\d+(?:\s*[\+\-\*\/\^%]\s*[-+]?\d*\.?\d+)*)", t)
    if m:
        return m.group(1).strip()
    # also try "what is 5 plus 5"
    m2 = re.search(r"(?:what is|calculate|compute|solve)\s+(.+)", t)
    if m2:
        candidate = m2.group(1)
        # keep only math chars
        if re.search(r"\d", candidate):
            # sanitize
            filtered = re.sub(r"[^0-9\.\+\-\*\/\^%\(\) ]", "", candidate)
            if filtered.strip():
                return filtered.strip()
    return None

def extract_todo_task(text):
    # patterns: add [task] to todo, remind me to [task], create task [task]
    patterns = [
        r"add\s+(.+?)\s+to (?:my )?todo",
        r"add todo\s+(.+)",
        r"create (?:a )?task\s+(.+)",
        r"remind me to\s+(.+)",
        r"todo[:\s]+(.+)",
        r"add\s+(.+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            task = m.group(1).strip()
            # clean up trailing punctuation
            task = re.sub(r"^(to do|task)\s*", "", task, flags=re.I)
            if len(task) > 2 and len(task) < 200:
                return task
    return None

def extract_search_query(text):
    patterns = [
        r"(?:search for|search|google|look up|wikipedia|tell me about|who is|what is)\s+(.+)",
        r"find online\s+(.+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            q = m.group(1).strip(" ?.")
            if q:
                return q
    return text.strip()

def extract_name(text):
    m = re.search(r"(?:my name is|call me|i am called)\s+([A-Za-z]+)", text, re.I)
    if m:
        return m.group(1).strip()
    return None

def extract_location(text):
    m = re.search(r"(?:weather|temperature|forecast).*?(?:in|for|at)\s+([A-Za-z\s]+)", text, re.I)
    if m:
        loc = m.group(1).strip()
        loc = re.sub(r"[?.!].*", "", loc).strip()
        return loc
    m2 = re.search(r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", text)
    if m2:
        return m2.group(1)
    return None

def extract_reminder_details(text):
    # "remind me to call mom at 5pm" -> (task, time_str)
    m = re.search(r"remind me to\s+(.+?)\s+at\s+(.+)", text, re.I)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m2 = re.search(r"remind me to\s+(.+?)\s+in\s+(\d+\s*(?:minute|hour|second)s?)", text, re.I)
    if m2:
        return m2.group(1).strip(), f"in {m2.group(2)}"
    return None, None
