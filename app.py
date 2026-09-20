#!/usr/bin/env python3
"""
Virtual Assistant - CLI + Web Server
Usage:
  python app.py              # CLI chat loop
  python app.py --web        # Start Flask web UI on http://localhost:5000
  python app.py --api        # Start API-only server
"""
import argparse
import sys
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from assistant import VirtualAssistant
from config import Config

app = Flask(__name__)
CORS(app)
assistant = VirtualAssistant()

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{name}} - AI Virtual Assistant</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0f1117;color:#e6e6e6;display:flex;flex-direction:column;height:100vh}
header{background:#1a1d27;padding:16px 24px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #2a2e40}
header .dot{width:10px;height:10px;background:#4ade80;border-radius:50%;box-shadow:0 0 8px #4ade80;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
header h1{font-size:18px;font-weight:600}
header span{font-size:12px;color:#9ca3af;margin-left:auto}
#chat{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px;max-width:900px;width:100%;margin:0 auto}
.msg{max-width:78%;padding:14px 18px;border-radius:18px;line-height:1.5;font-size:14px;white-space:pre-wrap;word-wrap:break-word}
.user{align-self:flex-end;background:#3b82f6;color:white;border-bottom-right-radius:6px}
.bot{align-self:flex-start;background:#1e2330;border:1px solid #2a2e40;border-bottom-left-radius:6px}
.bot.system{background:#1a2332;border-color:#1e3a5f}
.meta{font-size:11px;color:#6b7280;margin-top:6px}
#inputBar{display:flex;gap:10px;padding:16px;max-width:900px;width:100%;margin:0 auto;background:#0f1117;border-top:1px solid #1e2330}
#inputBar input{flex:1;padding:14px 18px;border-radius:24px;border:1px solid #2a2e40;background:#1a1d27;color:#fff;outline:none;font-size:14px}
#inputBar input:focus{border-color:#3b82f6}
#inputBar button{padding:12px 22px;border-radius:24px;border:none;background:#3b82f6;color:white;font-weight:600;cursor:pointer}
#inputBar button:hover{background:#2563eb}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.chip{padding:6px 12px;background:#1e2330;border:1px solid #2a2e40;border-radius:20px;font-size:12px;cursor:pointer}
.chip:hover{border-color:#3b82f6}
.typing{font-size:12px;color:#9ca3af;font-style:italic}
a{color:#60a5fa}
</style>
</head>
<body>
<header>
<div class="dot"></div>
<h1>🤖 {{name}} <small style="font-weight:400;color:#9ca3af">AI Virtual Assistant</small></h1>
<span id="status">Ready • Local memory + Wikipedia + Skills</span>
</header>
<div id="chat"></div>
<div style="max-width:900px;width:100%;margin:0 auto;padding:0 16px">
<div class="chips">
<span class="chip" onclick="sendChip('help')">help</span>
<span class="chip" onclick="sendChip('what time is it?')">time</span>
<span class="chip" onclick="sendChip('weather in Tokyo')">weather in Tokyo</span>
<span class="chip" onclick="sendChip('calculate 245 * 18')">calculate</span>
<span class="chip" onclick="sendChip('tell me a joke')">joke</span>
<span class="chip" onclick="sendChip('who is Ada Lovelace?')">who is Ada Lovelace?</span>
<span class="chip" onclick="sendChip('add buy groceries to my todo')">add todo</span>
<span class="chip" onclick="sendChip('list my todos')">list todos</span>
</div>
</div>
<div id="inputBar">
<input id="text" placeholder="Ask anything... e.g., 'who is Alan Turing?' or 'remind me to call mom at 5pm'" autocomplete="off" onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">Send ➤</button>
</div>
<script>
const chat=document.getElementById('chat');
const input=document.getElementById('text');
function addMsg(text, cls, meta){
  const d=document.createElement('div');
  d.className='msg '+cls;
  // minimal markdown: bold
  let html=text.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>').replace(/\n/g,'<br>').replace(/(https?:\/\/[^\s<]+)/g,'<a href="$1" target="_blank">$1</a>');
  d.innerHTML=html;
  if(meta){ let m=document.createElement('div'); m.className='meta'; m.textContent=meta; d.appendChild(m); }
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}
addMsg("Hello! I'm **{{name}}**, your AI virtual assistant.\\n\\nI can understand natural language, manage todos & reminders, do calculations, fetch weather, search Wikipedia/web, tell jokes, and more.\\n\\nTry typing **'help'** or click a chip above!", 'bot system');
async function send(){
  const q=input.value.trim(); if(!q) return;
  addMsg(q,'user'); input.value='';
  let typing=document.createElement('div'); typing.className='typing'; typing.textContent='{{name}} is thinking...'; chat.appendChild(typing); chat.scrollTop=chat.scrollHeight;
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q})});
    const j=await r.json();
    typing.remove();
    addMsg(j.response,'bot', `intent: ${j.intent} • confidence: ${j.confidence}`);
  }catch(e){ typing.remove(); addMsg('⚠️ Server error: '+e,'bot'); }
}
function sendChip(t){ input.value=t; send(); }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, name=Config.ASSISTANT_NAME)

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True) or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty message"}), 400
    result = assistant.process(msg)
    return jsonify(result)

@app.route("/api/todos", methods=["GET"])
def todos_api():
    return jsonify(assistant.get_todos())

@app.route("/api/history", methods=["GET"])
def history_api():
    return jsonify(assistant.get_history())

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "assistant": Config.ASSISTANT_NAME, "llm_enabled": assistant.llm_enabled})

def cli_loop():
    print(f"\n🤖 {Config.ASSISTANT_NAME} - AI Virtual Assistant (CLI)")
    print("   Type 'help' for capabilities, 'bye' to exit.\n")
    va = assistant
    while True:
        try:
            q = input("You › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "bye", "goodbye"):
            print(f"{Config.ASSISTANT_NAME} › Goodbye! 👋")
            break
        res = va.process(q)
        print(f"{Config.ASSISTANT_NAME} [{res['intent']} {res['confidence']}] › {res['response']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Start web UI")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--port", type=int, default=Config.PORT)
    parser.add_argument("--host", type=str, default=Config.HOST)
    args = parser.parse_args()
    if args.web or args.api:
        print(f"🚀 Starting {Config.ASSISTANT_NAME} on http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=Config.DEBUG)
    else:
        cli_loop()
