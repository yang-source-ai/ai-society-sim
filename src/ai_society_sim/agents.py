import json
import random

from .llm import extract_json


DEFAULT_AGENT_DEFS = [
    {
        "name": "Factory_Veteran_Zhang",
        "role": "50-year-old factory worker with 25 years experience",
        "personality": "Cautious but adaptable. Values stability.",
        "goal": "Secure retirement and help family adapt to the AI economy."
    },
    {
        "name": "Driver_Li",
        "role": "35-year-old delivery driver learning digital skills",
        "personality": "Pragmatic and hustling.",
        "goal": "Find a durable place in the next economy."
    },
    {
        "name": "Programmer_Wang",
        "role": "28-year-old software engineer",
        "personality": "Technically optimistic but strategically cautious.",
        "goal": "Stay valuable by becoming an AI-human bridge."
    },
    {
        "name": "Nurse_Chen",
        "role": "40-year-old hospital nurse",
        "personality": "Empathetic, practical, overworked.",
        "goal": "Use AI to reduce drudgery while protecting care quality."
    },
    {
        "name": "Teacher_Liu",
        "role": "45-year-old teacher",
        "personality": "Reflective, skeptical of replacing mentorship.",
        "goal": "Redefine education around human guidance."
    },
    {
        "name": "Graduate_Zhao",
        "role": "23-year-old recent graduate in creative AI tools",
        "personality": "Ambitious and digitally native.",
        "goal": "Build a career in new AI-native industries."
    },
    {
        "name": "TechCEO_Ma",
        "role": "CEO of a major AI company",
        "personality": "Visionary capitalist with a taste for legacy.",
        "goal": "Grow the leading AI company while shaping the rules of the next economy."
    },
    {
        "name": "Factory_Owner_Huang",
        "role": "Owner of a mid-size manufacturer",
        "personality": "Paternal but under competitive pressure.",
        "goal": "Modernize without collapsing workforce trust."
    },
    {
        "name": "Startup_Founder_Sun",
        "role": "Founder of an AI retraining startup",
        "personality": "Mission-driven and opportunistic.",
        "goal": "Make transition infrastructure profitable and scalable."
    },
    {
        "name": "Senator_Lin",
        "role": "Progressive legislator focused on inclusive growth",
        "personality": "Policy-minded, empathetic, reformist.",
        "goal": "Channel AI gains into broad prosperity."
    },
    {
        "name": "Senator_Wu",
        "role": "Conservative legislator focused on growth and order",
        "personality": "Pragmatic, stability-oriented.",
        "goal": "Preserve social order without strangling innovation."
    },
    {
        "name": "Union_Leader_Gao",
        "role": "Union organizer adapting to the AI era",
        "personality": "Strategic, combative, modern.",
        "goal": "Turn worker bargaining into worker ownership and durable protections."
    },
    {
        "name": "Professor_He",
        "role": "Economist studying labor and AI",
        "personality": "Analytical and evidence-driven.",
        "goal": "Produce models and policies that reduce transition pain."
    },
    {
        "name": "Investor_Qian",
        "role": "Impact investor in AI startups",
        "personality": "Bullish and long-term.",
        "goal": "Back firms that profit from inclusive adaptation."
    },
    {
        "name": "Journalist_Xu",
        "role": "Journalist covering AI and labor",
        "personality": "Sharp, skeptical, solutions-focused.",
        "goal": "Expose failure and amplify workable models."
    },
]

MOCK_MSGS = [
    "We should find a transition that works for everyone.",
    "Innovation matters, but distribution matters too.",
    "AI should free people, not discard them.",
    "Show me the ownership structure, not just the slogans.",
    "New industries are appearing faster than expected.",
    "Cooperation is becoming more valuable than pure conflict.",
    "The real question is who captures the gains.",
]

MOCK_ACTIONS = [
    "I propose a worker equity scheme tied to AI productivity gains.",
    "I launch a pilot program for AI-assisted retraining.",
    "I build a coalition around portable benefits.",
    "I invest in human-AI collaboration tools.",
    "I publish a report showing what policies actually help adaptation.",
    "I negotiate a profit-sharing deal between labor and management.",
]


class Agent:
    def __init__(self, name: str, role: str, personality: str, goal: str):
        self.name = name
        self.role = role
        self.personality = personality
        self.goal = goal
        self.memory = []
        self.category = self._infer_category()

    def _infer_category(self) -> str:
        x = (self.name + " " + self.role).lower()
        mapping = [
            ("worker", "worker"),
            ("driver", "worker"),
            ("nurse", "worker"),
            ("teacher", "worker"),
            ("graduate", "worker"),
            ("engineer", "worker"),
            ("ceo", "employer"),
            ("owner", "employer"),
            ("founder", "employer"),
            ("legislator", "politician"),
            ("senator", "politician"),
            ("union", "union"),
            ("economist", "academic"),
            ("professor", "academic"),
            ("investor", "investor"),
            ("journalist", "journalist"),
        ]
        for key, value in mapping:
            if key in x:
                return value
        return "other"

    def discuss(self, state: dict, forum_ctx: str, year: int, forum, llm):
        if llm.dry_run:
            msg = random.choice(MOCK_MSGS)
            forum.post(year, self.category, self.name, msg)
            return msg

        mem = "\n".join(self.memory[-3:]) or "(No memory)"
        prompt = f"""You are {self.name}.
Role: {self.role}
Personality: {self.personality}
Goal: {self.goal}

WORLD STATE:
{json.dumps(state, ensure_ascii=False, indent=2)}

YOUR MEMORY:
{mem}

CURRENT FORUM:
{forum_ctx}

Speak strategically in under 25 words.
You may cooperate, criticize, negotiate, or reframe the debate.
Output JSON:
{{"message": "your post", "reply_to": null}}"""

        data = extract_json(llm.call(prompt, temperature=1.0, max_tokens=100, mode="json"))
        if data and "message" in data:
            forum.post(year, self.category, self.name, data["message"], data.get("reply_to"))
            return data["message"]

        fallback = "We need a better transition strategy."
        forum.post(year, self.category, self.name, fallback)
        return fallback

    def decide(self, state: dict, forum_ctx: str, year: int, llm):
        if llm.dry_run:
            action = random.choice(MOCK_ACTIONS)
            self._remember(year, action)
            return action

        mem = "\n".join(self.memory[-5:]) or "(No memory)"
        prompt = f"""You are {self.name}.
Role: {self.role}
Personality: {self.personality}
Goal: {self.goal}

WORLD STATE:
{json.dumps(state, ensure_ascii=False, indent=2)}

YOUR MEMORY:
{mem}

FORUM CONTEXT:
{forum_ctx}

Decide ONE concrete strategic action for this year.
You are rational, self-interested, and capable of cooperation when it helps you.
Under 50 words.
Output JSON:
{{"action": "your action", "reasoning": "why this serves your interests"}}"""

        data = extract_json(llm.call(prompt, temperature=0.9, max_tokens=150, mode="json"))
        if data and "action" in data:
            action = data["action"]
            self._remember(year, action)
            return action

        fallback = "I reposition myself for the next phase of the AI transition."
        self._remember(year, fallback)
        return fallback

    def propose_deal(self, state: dict, other_name: str, forum_ctx: str, year: int, llm):
        if llm.dry_run:
            return {
                "proposal": "Let's cooperate on a worker-adaptation and productivity-sharing plan.",
                "target": other_name
            }

        prompt = f"""You are {self.name} ({self.role}).
Goal: {self.goal}

You want to propose a mutually beneficial deal to {other_name}.

WORLD STATE:
{json.dumps(state, ensure_ascii=False, indent=2)}

RECENT FORUM:
{forum_ctx}

Propose a concise win-win deal in under 25 words.
Output JSON:
{{"proposal": "your proposal", "target": "{other_name}"}}"""

        data = extract_json(llm.call(prompt, temperature=0.9, max_tokens=100, mode="json"))
        if data and "proposal" in data:
            return data
        return {"proposal": "Let's explore a shared-interest compromise.", "target": other_name}

    def _remember(self, year: int, text: str):
        self.memory.append(f"Year {year}: {text}")
        if len(self.memory) > 8:
            self.memory.pop(0)