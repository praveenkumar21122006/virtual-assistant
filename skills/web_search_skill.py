import requests
import re
from .base import BaseSkill
from nlp.entity_extractor import extract_search_query

class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Performs web search via DuckDuckGo instant answer"
    intents = ["web_search"]

    def handle(self, text, intent, entities):
        query = extract_search_query(text)
        if not query:
            return "🌐 What should I search for?"
        try:
            # DuckDuckGo Instant Answer API (no key required)
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            r = requests.get(url, timeout=5, headers={"User-Agent": "VirtualAssistant/1.0"})
            if r.status_code == 200:
                data = r.json()
                abstract = data.get("AbstractText") or data.get("Abstract") or ""
                if abstract:
                    source = data.get("AbstractURL", "")
                    return f"🌐 **Search: {query}**\n\n{abstract[:700]}\n\n🔗 {source}"
                # Try related topics
                topics = data.get("RelatedTopics", [])
                if topics:
                    first = topics[0]
                    if isinstance(first, dict) and "Text" in first:
                        return f"🌐 **{query}** — {first['Text'][:600]}\n🔗 {first.get('FirstURL','')}"
                heading = data.get("Heading", "")
                if heading:
                    return f"🌐 Found: **{heading}** for '{query}'. Try https://duckduckgo.com/?q={query.replace(' ','+')}"
        except Exception as e:
            pass
        # Fallback: provide search links
        q_enc = query.replace(" ", "+")
        return (
            f"🔎 Here's how to search for **{query}**:\n"
            f"- DuckDuckGo: https://duckduckgo.com/?q={q_enc}\n"
            f"- Google: https://www.google.com/search?q={q_enc}\n"
            f"- Wikipedia: https://en.wikipedia.org/wiki/Special:Search?search={q_enc}"
        )
