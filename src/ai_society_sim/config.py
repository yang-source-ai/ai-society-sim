from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import os

import yaml
from dotenv import load_dotenv


DEFAULT_INITIAL_STATE = {
    "year": 0,
    "ai_capability": 0.10,
    "total_productivity": 1.0,
    "unemployment_rate": 0.06,
    "wealth_inequality": 0.38,
    "average_living_standard": 0.65,
    "social_trust": 0.55,
    "worker_power": 0.45,
    "corporate_power": 0.55,
    "government_effectiveness": 0.60,
    "innovation_rate": 0.50,
    "social_mobility": 0.50,
    "cooperation_index": 0.40,
    "public_mood": "cautiously optimistic about technology",
    "dominant_narrative": "AI will create more jobs than it destroys",
    "current_policy": "status quo",
}

DEFAULT_TECHNOLOGY = {
    "mode": "hybrid",  # endogenous / hybrid / timeline
    "base_growth_rate": 0.025,
    "innovation_feedback": 0.35,
    "corporate_investment_feedback": 0.22,
    "cooperation_feedback": 0.18,
    "government_support_feedback": 0.12,
    "public_acceptance_feedback": 0.08,
    "productivity_base_growth": 0.02,
    "productivity_ai_multiplier": 0.70,
    "productivity_innovation_feedback": 0.15,
    "productivity_cooperation_feedback": 0.08,
    "max_capability": 1.0,
    "narrate_shift": True,
}

DEFAULT_AI_TIMELINE = {
    10: "Near-AGI systems become a serious governance and labor issue.",
    15: "AGI-level productivity makes distribution the central political question.",
}


def _parse_bool(v: str | None, default: bool = True) -> bool:
    if v is None:
        return default
    return v.lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class Settings:

    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    dry_run: bool = True


    years: int = 15
    discussion_rounds: int = 2
    speakers_per_round: int = 5
    max_state_fields: int = 20
    output_dir: str = "outputs"

    initial_state: dict[str, Any] = field(default_factory=lambda: DEFAULT_INITIAL_STATE.copy())
    technology: dict[str, Any] = field(default_factory=lambda: DEFAULT_TECHNOLOGY.copy())
    ai_timeline: dict[int, str] = field(default_factory=lambda: DEFAULT_AI_TIMELINE.copy())


def load_settings(config_path: str | None = None) -> Settings:
    load_dotenv()

    settings = Settings(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"),
        model=os.getenv("MODEL_NAME", "deepseek-chat"),
        dry_run=_parse_bool(os.getenv("DRY_RUN", "true"), True),
    )

    if config_path:
        path = Path(config_path)
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

            for key in [
                "years",
                "discussion_rounds",
                "speakers_per_round",
                "max_state_fields",
                "output_dir",
            ]:
                if key in data:
                    setattr(settings, key, data[key])

            if "initial_state" in data and isinstance(data["initial_state"], dict):
                merged = DEFAULT_INITIAL_STATE.copy()
                merged.update(data["initial_state"])
                settings.initial_state = merged

            if "technology" in data and isinstance(data["technology"], dict):
                merged = DEFAULT_TECHNOLOGY.copy()
                merged.update(data["technology"])
                settings.technology = merged

            if "ai_timeline" in data and isinstance(data["ai_timeline"], dict):
                settings.ai_timeline = {int(k): str(v) for k, v in data["ai_timeline"].items()}

    return settings