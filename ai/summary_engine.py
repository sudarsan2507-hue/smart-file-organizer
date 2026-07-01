import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
MAX_CHARS = 2000


class SummaryEngine:
    def __init__(self, model=DEFAULT_MODEL, url=OLLAMA_URL):
        self.model = model
        self.url = url

    def summarize(self, text):
        snippet = text[:MAX_CHARS].strip()
        if not snippet:
            return None

        payload = json.dumps({
            "model": self.model,
            "prompt": f"Summarize the following document in one or two sentences:\n\n{snippet}",
            "stream": False,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip() or None
        except Exception:
            return None
