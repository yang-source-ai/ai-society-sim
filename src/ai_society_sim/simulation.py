import random
from dataclasses import dataclass

from .agents import Agent, DEFAULT_AGENT_DEFS
from .forum import Forum
from .world import World
from .llm import LLMClient


@dataclass
class SimulationResult:
    world: World
    forum: Forum
    agents: list[Agent]
    summaries: list[dict]


def _pick_speakers(agents: list[Agent], speakers_per_round: int):
    by_cat = {}
    for a in agents:
        by_cat.setdefault(a.category, []).append(a)

    speakers = []
    cats = list(by_cat.keys())
    random.shuffle(cats)

    for cat in cats:
        pool = by_cat[cat]
        take = min(2, len(pool))
        speakers.extend(random.sample(pool, take))
        if len(speakers) >= speakers_per_round:
            break

    return speakers[:speakers_per_round]


def run_simulation(settings) -> SimulationResult:
    print("[SIM] run_simulation entered")

    llm = LLMClient(
        api_key=settings.api_key,
        base_url=settings.base_url,
        model=settings.model,
        dry_run=settings.dry_run,
    )

    agents = [Agent(**d) for d in DEFAULT_AGENT_DEFS]
    forum = Forum()
    world = World(settings.initial_state, max_state_fields=settings.max_state_fields)
    summaries = []

    print("=" * 72)
    print(" AI SOCIETY SIMULATOR")
    print(f" agents={len(agents)} years={settings.years} "
          f"rounds/year={settings.discussion_rounds} speakers/round={settings.speakers_per_round}")
    print(f" model={settings.model} base_url={settings.base_url}")
    print(f" dry_run={settings.dry_run}")
    print("=" * 72)

    for year in range(1, settings.years + 1):
        print(f"\n{'=' * 72}")
        print(f" YEAR {year}")
        print(f"{'=' * 72}")

        milestone = settings.ai_timeline.get(year, None)

        tech_event = world.evolve_technology(
            tech_cfg=settings.technology,
            year=year,
            llm=llm,
            milestone=milestone,
        )

        forum.post(
            year,
            "system",
            "NEWS",
            f"Year {year}: {tech_event['description']}"
        )

        print("\n--- Endogenous Technology Update ---")
        print(f"  AI capability: {tech_event['old_ai']:.3f} -> {tech_event['new_ai']:.3f}")
        print(f"  Productivity : {tech_event['old_productivity']:.2f} -> {tech_event['new_productivity']:.2f}")

        print("\n--- Discussion ---")
        for rd in range(settings.discussion_rounds):
            print(f"\n  [Round {rd + 1}]")
            forum_ctx = forum.recent_text(year)
            speakers = _pick_speakers(agents, settings.speakers_per_round)
            for sp in speakers:
                sp.discuss(world.state, forum_ctx, year, forum, llm)

        print("\n--- Deal Proposals ---")
        deals = []
        cross_pairs = [
            (a, b) for a in agents for b in agents
            if a != b and a.category != b.category
        ]
        random.shuffle(cross_pairs)

        for a, b in cross_pairs[:3]:
            proposal = a.propose_deal(
                world.state,
                b.name,
                forum.recent_text(year),
                year,
                llm
            )
            proposal["proposer"] = a.name
            deals.append(proposal)

            forum.post(
                year,
                a.category,
                a.name,
                f"Proposal to {b.name}: {proposal['proposal']}",
                reply_to=b.name
            )

        print("\n--- Decisions ---")
        actions = {}
        ctx = forum.recent_text(year)
        for agent in agents:
            action = agent.decide(world.state, ctx, year, llm)
            actions[agent.name] = action
            print(f"  - {agent.name}: {action}")

        print("\n--- World Update ---")
        new_state = world.update(actions, deals, tech_event, year, llm)

        summary = world.summarize(year, actions, llm)
        summaries.append({"year": year, "summary": summary})

        print(f"\n[State: {len(new_state)} fields]")
        for k, v in sorted(new_state.items()):
            print(f"  {k:28s} {v}")

        print(f"\n[Summary] {summary}")

    return SimulationResult(world=world, forum=forum, agents=agents, summaries=summaries)