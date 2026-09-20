# 🤖 AI-Powered Virtual Assistant — Nova

An AI virtual assistant that **understands natural language**, **performs tasks**, and **provides information** — with a modern web UI + CLI, modular skills, conversation memory, and optional LLM integration.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Flask](https://img.shields.io/badge/flask-3.x-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

### 🧠 Understand & Respond
- **Intent classification**: hybrid rule-based + TF-IDF/LogisticRegression (`nlp/intent_classifier.py:1`)
- **Entity extraction** for calculations, locations, tasks, search queries (`nlp/entity_extractor.py:1`)
- **Conversation memory** with persistent `memory.json` (`memory.py:1`)
- **Optional OpenAI LLM** fallback for open-ended chat when `OPENAI_API_KEY` is set (`assistant.py:52`)

### ✅ Perform Tasks
| Skill | Example |
|-------|---------|
| **Todo** | `add buy milk to my todo` → `list my todos` → `complete task 1` |
| **Reminders** | `remind me to call mom at 5pm` / `remind me to drink water in 30 minutes` |
| **Calculator** | `calculate 245 * 18 + 7` / `what is 100 / 4?` |
| **Timer** | `timer 5 minutes` |

### ℹ️ Provide Information
| Skill | Example |
|-------|---------|
| **Weather** | `weather in Paris?` (mock or live via OpenWeatherMap) |
| **Date/Time** | `what time is it?` / `today?` |
| **Wikipedia** | `who is Alan Turing?` / `tell me about quantum computing` |
| **Web Search** | `search for Python async tutorials` (DuckDuckGo) |
| **Jokes** | `tell me a joke` |
| **Help/Smalltalk** | `help` / `my name is Alex` |

---

## 🏗️ Architecture

```
virtual-assistant/
├── app.py                 # CLI + Flask web server & REST API
├── assistant.py           # Orchestrator: NLU → Skills → LLM fallback
├── config.py              # Env-based config
├── memory.py              # Persistent conversation + todo/reminder store
├── nlp/
│   ├── intent_classifier.py  # Rule + ML classifier
│   └── entity_extractor.py   # Regex extractors
├── skills/
│   ├── base.py            # Abstract BaseSkill
│   ├── smalltalk_skill.py # Greetings, help, name
│   ├── datetime_skill.py
│   ├── calculator_skill.py
│   ├── todo_skill.py
│   ├── weather_skill.py
│   ├── wikipedia_skill.py
│   ├── web_search_skill.py
│   ├── joke_skill.py
│   └── reminder_skill.py
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
# 1. Install deps (optional: create venv first)
pip install -r requirements.txt

# 2. Run CLI
python app.py

# 3. Or launch Web UI at http://localhost:5000
python app.py --web
# custom host/port
python app.py --web --port 8000 --host 127.0.0.1
```

### Environment (.env)
Copy `.env.example` → `.env`:
```ini
ASSISTANT_NAME=Nova
OPENAI_API_KEY=sk-...          # optional: enables LLM for chat fallback
WEATHER_API_KEY=...            # optional: OpenWeatherMap for live weather
PORT=5000
```

---

## 🌐 REST API

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/` | GET | — | Web UI |
| `/api/chat` | POST | `{"message":"hello"}` | → `{"intent","confidence","response"}` |
| `/api/todos` | GET | — | List todos |
| `/api/history` | GET | — | Conversation history |
| `/api/health` | GET | — | Status + LLM flag |

**Example:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"calculate 12*8"}'
# {"intent":"calculator","confidence":0.95,"response":"🧮 12*8 = **96**"}
```

---

## 🧪 Try It

```
You › help
You › my name is Priya
You › add finish project report to my todo
You › list my todos
You › calculate 18 * 34
You › weather in Tokyo
You › who is Grace Hopper?
You › tell me a joke
You › remind me to call mom at 7pm
```

---

## 🔧 Extending

Add a new skill in 3 steps:

1. Create `skills/my_skill.py` inheriting `BaseSkill` (`skills/base.py:1`)
2. Implement `handle(self, text, intent, entities) -> str`
3. Register in `assistant.py:19` (`_register_skills`)

---

## 📝 Notes

- **No API keys required** to run locally — weather & Wikipedia use mock/fallback + free APIs.
- **Safe calculator** uses restricted `eval` (`skills/calculator_skill.py:15`).
- **Voice** (STT/TTS) deps are in `requirements.txt` (`SpeechRecognition`, `pyttsx3`) but disabled by default; set `ENABLE_VOICE=true` and extend `app.py` to enable.
