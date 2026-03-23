import json
import re
import time
from openai import OpenAI


SYS_JSON = """You are a socioeconomic simulation engine.
Rules:
1. Agents are rational and strategic, but still human.
2. Cooperation and conflict both happen when incentives justify them.
3. AI productivity can create real gains, but distribution is uncertain.
4. Output ONLY valid JSON. No markdown. No explanation outside JSON.
"""

SYS_NARRATIVE = """You are a historian describing a society going through an AI transition.
Be concise, vivid, and balanced. Output plain text only.
"""


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str, dry_run: bool = True):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.dry_run = dry_run

        
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(self, prompt: str, temperature: float = 0.9, max_tokens: int = 400, mode: str = "json"):
        if self.dry_run:
            return None

        sys_prompt = SYS_JSON if mode == "json" else SYS_NARRATIVE

        for i in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"[LLM retry {i + 1}] {e}")
                time.sleep(2 * (i + 1))
        return None


def extract_json(text: str | None):
    if not text:
        return None

    try:
        text = re.sub(r"```json\s*|```\s*", "", text).strip()

        depth = 0
        start = None
        for i, c in enumerate(text):
            if c == "{":
                if start is None:
                    start = i
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0 and start is not None:
                    return json.loads(text[start:i + 1])

        if start is not None:
            return json.loads(text[start:])

        return json.loads(text)

    except Exception:
        return None