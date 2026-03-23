class Forum:
    ICONS = {
        "worker": "👷",
        "employer": "🏢",
        "politician": "🏛️",
        "union": "✊",
        "academic": "🎓",
        "investor": "💰",
        "journalist": "📰",
        "system": "📢",
        "other": "💬",
    }

    def __init__(self):
        self.posts = []

    def post(self, year: int, role: str, author: str, message: str, reply_to: str | None = None):
        self.posts.append({
            "year": year,
            "role": role,
            "author": author,
            "message": message,
            "reply_to": reply_to,
        })

        icon = self.ICONS.get(role, "💬")
        suffix = f" -> @{reply_to}" if reply_to else ""
        indent = "      " if reply_to else "    "
        print(f"{indent}{icon} [{author}]{suffix}: {message}")

    def recent_text(self, year: int, n: int = 15) -> str:
        rows = [p for p in self.posts if p["year"] == year][-n:]
        if not rows:
            return "(No discussion yet.)"
        return "\n".join(
            f"[{p['author']}]{' @' + p['reply_to'] if p.get('reply_to') else ''}: {p['message']}"
            for p in rows
        )