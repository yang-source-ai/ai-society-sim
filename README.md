# AI Society Simulator

[中文说明 / Chinese README](README_zh.md)

A free-form multi-agent simulation sandbox for exploring how workers, employers, legislators, unions, investors, and public intellectuals may respond to rapid AI / AGI diffusion.

This project combines:
- LLM-driven agent discussion and decision-making
- rule-guided world evolution
- endogenous technology growth
- automatic visualization of socioeconomic indicators

It is designed to explore questions such as:

- How might AI affect unemployment, inequality, and social trust?
- Under what conditions can rational self-interest lead to cooperation?
- Could AGI productivity gains be distributed in a socially stable way?
- What kinds of institutions might emerge under heavy automation?

---

## Example Output

![Dashboard](assets/dashboard.png)

### What this figure shows
This example run suggests a relatively optimistic adaptation path:
- AI capability and productivity rise rapidly
- unemployment stays low
- living standards improve
- social trust and cooperation strengthen
- inequality remains present, but does not explode

### What this figure does **not** show
- It does **not** predict the future
- It does **not** prove AGI will lead to harmony
- It is a **single run** under a specific prompt setup
- Results are sensitive to prompts, model behavior, and initial conditions

So this dashboard should be read as a **scenario exploration**, not a forecast.

---

## Features

- Multi-agent social simulation
- Free-form discussion between heterogeneous agents
- Endogenous technology growth dynamics
- Optional milestone-based AGI anchor events
- Configurable initial world state
- Support for cloud APIs and local OpenAI-compatible backends
- Automatic dashboard plotting
- Dry-run mode for debugging without API cost

---

## Agent Types

Default agents include:
- workers
- employers
- legislators
- union organizers
- economists
- investors
- journalists

Each agent has:
- a role
- a personality
- a goal
- short-term memory of previous decisions

---

## Project Structure

    ai-society-sim/
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── README_zh.md
    ├── pyproject.toml
    ├── configs/
    │   └── default.yaml
    ├── assets/
    │   └── dashboard.png
    └── src/
        └── ai_society_sim/
            ├── agents.py
            ├── cli.py
            ├── config.py
            ├── forum.py
            ├── llm.py
            ├── simulation.py
            ├── viz.py
            └── world.py

---

## Installation

Clone the repository:

    git clone https://github.com/yang-source-ai/ai-society-sim.git
    cd ai-society-sim

Install in editable mode:

    python -m pip install -e .

---

## Configuration

Create a `.env` file in the project root.

Example (cloud API):

    LLM_BASE_URL=https://api.deepseek.com
    LLM_API_KEY=your_api_key_here
    LLM_MODEL=deepseek-chat
    DRY_RUN=false

Example (local Ollama):

    LLM_BASE_URL=http://localhost:11434/v1
    LLM_API_KEY=ollama
    LLM_MODEL=qwen2.5:7b
    DRY_RUN=false

---

## Running the Simulation

Dry-run mode:

    python -m ai_society_sim.cli --config configs/default.yaml --dry-run

Normal run:

    python -m ai_society_sim.cli --config configs/default.yaml

---

## Outputs

The simulator saves:
- world history as JSON
- forum/discussion logs as JSON
- yearly summaries as JSON
- a dashboard figure as PNG

By default, outputs are written to:

    outputs/

---

## Config File

Main scenario settings are stored in:

    configs/default.yaml

This file controls:
- simulation length
- discussion rounds
- speakers per round
- initial world state
- endogenous technology growth parameters
- optional AGI milestone anchors

---

## Methodology

This project uses a hybrid design:

### 1. Agents
Agents discuss, negotiate, and choose actions through LLM prompts.

### 2. World State
The world tracks macro variables such as:
- unemployment rate
- wealth inequality
- social trust
- worker power
- corporate power
- government effectiveness
- innovation rate
- social mobility
- cooperation index
- total productivity
- AI capability

### 3. Technology Evolution
Technology does not rely entirely on hand-written year-by-year scripts.
Instead, AI capability and productivity evolve mainly through endogenous feedback from:
- innovation
- corporate investment
- cooperation
- institutional support
- public acceptance

### 4. Narrative Summaries
Each year is summarized in natural language to provide a qualitative interpretation of the system dynamics.

---

## Limitations

This is **not** a predictive model of the real world.

It is an experimental simulation framework for exploring possible social trajectories under different assumptions.

Results depend heavily on:
- model alignment
- prompt design
- initial conditions
- backend model behavior
- scenario framing

A single run should be treated as a **possible trajectory**, not a conclusion.

---

## Roadmap

- [x] Modular project structure
- [x] CLI-based execution
- [x] YAML configuration
- [x] Endogenous technology growth
- [x] Dashboard visualization
- [ ] Multi-run Monte Carlo experiments
- [ ] Social network structure between agents
- [ ] Long-term memory / vector memory
- [ ] Scenario comparison reports
- [ ] Interactive web UI

---

## License

MIT

---

## Why this project exists

I built this project to think through a difficult question:

**If AI radically expands productivity, what determines whether society moves toward collapse, adaptation, or something like “great harmony”?**

If you find this interesting, feel free to open an issue, suggest scenarios, or fork the project.
