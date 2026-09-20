import requests
from .base import BaseSkill
from nlp.entity_extractor import extract_search_query

class WikipediaSkill(BaseSkill):
    name = "wikipedia"
    description = "Fetches summaries from Wikipedia"
    intents = ["wikipedia", "chat"]

    def handle(self, text, intent, entities):
        query = extract_search_query(text)
        if not query or len(query) < 2:
            return "🔍 What would you like to know about?"
        # Try Wikipedia REST API
        try:
            # Search first to get correct title
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&namespace=0&format=json"
            r = requests.get(search_url, timeout=5, headers={"User-Agent": "VirtualAssistant/1.0"})
            if r.status_code == 200:
                data = r.json()
                if len(data) > 1 and data[1]:
                    title = data[1][0]
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
                    r2 = requests.get(summary_url, timeout=5, headers={"User-Agent": "VirtualAssistant/1.0"})
                    if r2.status_code == 200:
                        j = r2.json()
                        extract = j.get("extract", "")
                        url = j.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}")
                        if extract:
                            if len(extract) > 600:
                                extract = extract[:600] + "..."
                            return f"📚 **{j.get('title', title)}**\n\n{extract}\n\n🔗 {url}"
        except Exception as e:
            pass
        # Fallback to wikipedia package if installed
        try:
            import wikipedia
            wikipedia.set_lang("en")
            page = wikipedia.summary(query, sentences=2, auto_suggest=True)
            return f"📚 **{query.title()}**\n\n{page}\n\n🔗 https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
        except Exception:
            pass
        return f"❓ I couldn't find Wikipedia info for '{query}'. Try rephrasing or use 'search {query}' for web results."
