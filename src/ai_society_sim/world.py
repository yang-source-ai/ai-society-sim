import json
from .llm import extract_json


PROTECTED_FIELDS = [
    "year",
    "ai_capability",
    "total_productivity",
    "unemployment_rate",
    "wealth_inequality",
    "average_living_standard",
    "social_trust",
    "worker_power",
    "corporate_power",
    "government_effectiveness",
    "innovation_rate",
    "social_mobility",
    "cooperation_index",
    "public_mood",
    "dominant_narrative",
    "current_policy",
]


class World:
    def __init__(self, initial_state: dict, max_state_fields: int = 20):
        self.state = initial_state.copy()
        self.max_state_fields = max_state_fields
        self.history = [self.state.copy()]
        self.metrics = {
            k: [v] for k, v in self.state.items()
            if isinstance(v, (int, float))
        }

    def prune_state(self, state: dict):
       
        pruned = {}

        for f in PROTECTED_FIELDS:
            if f in state:
                pruned[f] = state[f]
            elif f in self.state:
                pruned[f] = self.state[f]

        extra_numeric = {
            k: v for k, v in state.items()
            if k not in pruned and isinstance(v, (int, float))
        }

        remain_slots = max(0, self.max_state_fields - len(pruned))
        ranked = sorted(
            extra_numeric.items(),
            key=lambda kv: abs(float(kv[1]) - 0.5),
            reverse=True
        )

        for k, v in ranked[:remain_slots]:
            pruned[k] = v

        for k, v in state.items():
            if isinstance(v, str) and k not in pruned:
                pruned[k] = v

        return pruned

    def evolve_technology(self, tech_cfg: dict, year: int, llm, milestone: str | None = None):
        
        old_ai = float(self.state.get("ai_capability", 0.10))
        old_prod = float(self.state.get("total_productivity", 1.0))

        innovation = float(self.state.get("innovation_rate", 0.50))
        corp = float(self.state.get("corporate_power", 0.55))
        coop = float(self.state.get("cooperation_index", 0.40))
        govt = float(self.state.get("government_effectiveness", 0.60))
        trust = float(self.state.get("social_trust", 0.55))

        ai_delta = (
            tech_cfg.get("base_growth_rate", 0.025)
            + innovation * tech_cfg.get("innovation_feedback", 0.35) * 0.06
            + corp * tech_cfg.get("corporate_investment_feedback", 0.22) * 0.04
            + coop * tech_cfg.get("cooperation_feedback", 0.18) * 0.03
            + govt * tech_cfg.get("government_support_feedback", 0.12) * 0.02
            + trust * tech_cfg.get("public_acceptance_feedback", 0.08) * 0.015
        )

        ai_delta = max(0.005, ai_delta)  
        new_ai = min(float(tech_cfg.get("max_capability", 1.0)), old_ai + ai_delta)
        new_ai = round(new_ai, 3)

        
        prod_growth = (
            1.0
            + tech_cfg.get("productivity_base_growth", 0.02)
            + ai_delta * tech_cfg.get("productivity_ai_multiplier", 0.70)
            + innovation * tech_cfg.get("productivity_innovation_feedback", 0.15) * 0.03
            + coop * tech_cfg.get("productivity_cooperation_feedback", 0.08) * 0.02
        )

        new_prod = round(old_prod * prod_growth, 2)

       
        self.state["ai_capability"] = new_ai
        self.state["total_productivity"] = new_prod


        if llm.dry_run or not tech_cfg.get("narrate_shift", True):
            if milestone:
                desc = (
                    f"AI capability rose from {old_ai:.2f} to {new_ai:.2f}. "
                    f"{milestone}"
                )
            else:
                desc = (
                    f"AI capability rose endogenously from {old_ai:.2f} to {new_ai:.2f}, "
                    f"driven by innovation, investment, and institutional coordination."
                )
        else:
            prompt = f"""AI capability evolved endogenously this year.

Previous AI capability: {old_ai:.3f}
New AI capability: {new_ai:.3f}
Previous total productivity: {old_prod:.2f}
New total productivity: {new_prod:.2f}

Drivers:
- innovation_rate: {innovation:.3f}
- corporate_power: {corp:.3f}
- cooperation_index: {coop:.3f}
- government_effectiveness: {govt:.3f}
- social_trust: {trust:.3f}

Optional milestone:
{milestone if milestone else "None"}

Write ONE concise sentence describing what this technological shift means in practice.
Plain text only.
"""
            raw = llm.call(prompt, temperature=0.8, max_tokens=80, mode="narrative")
            desc = raw.strip() if raw else (
                f"AI capability rose from {old_ai:.2f} to {new_ai:.2f}."
            )

        return {
            "old_ai": old_ai,
            "new_ai": new_ai,
            "old_productivity": old_prod,
            "new_productivity": new_prod,
            "description": desc,
        }

    def update(self, actions: dict, deals: list[dict], tech_event: dict, year: int, llm):
        """
        社会更新阶段：
        技术值（ai_capability / total_productivity）已经由 evolve_technology 内生计算好了。
        这里主要让 LLM 更新分配、信任、权力、制度等“社会后果”。
        """
        if llm.dry_run:
            ns = self.state.copy()
            ns["year"] = year
          
            for key in [
                "unemployment_rate",
                "wealth_inequality",
                "average_living_standard",
                "social_trust",
                "worker_power",
                "corporate_power",
                "government_effectiveness",
                "innovation_rate",
                "social_mobility",
                "cooperation_index",
            ]:
                if key in ns and isinstance(ns[key], (int, float)):
                 
                    if key == "average_living_standard":
                        ns[key] = round(min(1.0, float(ns[key]) + 0.01), 3)
                    elif key == "cooperation_index":
                        ns[key] = round(min(1.0, float(ns[key]) + 0.015), 3)
                    else:
                        ns[key] = round(max(0.0, min(1.0, float(ns[key]))), 3)

            ns["public_mood"] = "adaptive but uncertain"
            ns["dominant_narrative"] = "AI is improving productivity, but institutions are still determining who benefits."
            ns["current_policy"] = ns.get("current_policy", "status quo")

            self.state = ns
            self.history.append(ns.copy())
            self._record(ns)
            return ns

        actions_text = "\n".join(f"- {k}: {v}" for k, v in actions.items())
        deals_text = "\n".join(
            f"- {d.get('proposer', '?')} -> {d.get('target', '?')}: {d.get('proposal', '?')}"
            for d in deals
        ) if deals else "No major deals proposed."

        prompt = f"""WORLD STATE UPDATE — Year {year}

CURRENT STATE:
{json.dumps(self.state, ensure_ascii=False, indent=2)}

THIS YEAR'S ENDOGENOUS TECHNOLOGY SHIFT:
- AI capability changed from {tech_event['old_ai']:.3f} to {tech_event['new_ai']:.3f}
- Total productivity changed from {tech_event['old_productivity']:.2f} to {tech_event['new_productivity']:.2f}
- Practical interpretation: {tech_event['description']}

AGENT ACTIONS:
{actions_text}

DEALS / ALLIANCES:
{deals_text}

Your task:
Update the SOCIAL and INSTITUTIONAL consequences of this year.

Important rules:
1. Set "year" to exactly {year}.
2. KEEP these fields:
{", ".join(PROTECTED_FIELDS)}
3. Preserve the already-computed:
   - ai_capability = {tech_event['new_ai']:.3f}
   - total_productivity = {tech_event['new_productivity']:.2f}
4. Update things like:
   - unemployment_rate
   - wealth_inequality
   - average_living_standard
   - social_trust
   - worker_power
   - corporate_power
   - government_effectiveness
   - innovation_rate
   - social_mobility
   - cooperation_index
   - public_mood
   - dominant_narrative
   - current_policy
5. Good adaptation is possible. So are coordination failures.
6. Agent strategy should matter more than external storytelling.
7. You may add at most 3 new numeric fields if something genuinely new emerges.

Output ONLY the updated JSON.
"""

        data = extract_json(llm.call(prompt, temperature=0.8, max_tokens=700, mode="json"))

        if not data:
          
            self.state["year"] = year
            self.state["ai_capability"] = tech_event["new_ai"]
            self.state["total_productivity"] = tech_event["new_productivity"]
            self.history.append(self.state.copy())
            self._record(self.state)
            return self.state

        
        data["year"] = year
        data["ai_capability"] = tech_event["new_ai"]
        data["total_productivity"] = tech_event["new_productivity"]

        for k, v in data.items():
            if isinstance(v, (int, float)):
                if k == "year":
                    data[k] = int(v)
                elif k == "total_productivity":
                    data[k] = round(max(0.1, float(v)), 2)
                else:
                    data[k] = round(max(0.0, min(1.0, float(v))), 3)

        for f in PROTECTED_FIELDS:
            if f not in data:
                data[f] = self.state.get(f)

        self.state = self.prune_state(data)
        self.history.append(self.state.copy())
        self._record(self.state)
        return self.state

    def summarize(self, year: int, actions: dict, llm):
        if llm.dry_run:
            return f"Year {year} saw endogenous AI growth and another round of social adaptation."

        prompt = f"""Write a balanced 2-sentence historian-style summary of Year {year}.

STATE:
{json.dumps(self.state, ensure_ascii=False, indent=2)}

SOME IMPORTANT ACTIONS:
{list(actions.values())[:5]}

Plain text only. No JSON.
"""

        text = llm.call(prompt, temperature=0.8, max_tokens=120, mode="narrative")
        if text and not text.strip().startswith("{"):
            return text.strip()

        return f"Year {year} was another turning point in the AI transition."

    def _record(self, state: dict):
        for k, v in state.items():
            if isinstance(v, (int, float)):
                if k not in self.metrics:
                    self.metrics[k] = [None] * (len(self.history) - 1)
                self.metrics[k].append(v)

        for k in self.metrics:
            while len(self.metrics[k]) < len(self.history):
                self.metrics[k].append(self.metrics[k][-1] if self.metrics[k] else None)