# AI Society Simulator

A free-form multi-agent simulation framework for exploring how workers, employers, politicians, unions, investors, and public intellectuals may respond to rapid AI / AGI diffusion.

## Features

- LLM-driven agents
- Free-form discussion and decision making
- World-state evolution via LLM
- Configurable AI timeline
- Supports cloud APIs and local models (Ollama / vLLM / LM Studio)
- CLI interface
- Automatic dashboard plotting

## Quick Start

```bash
git clone https://github.com/yourname/ai-society-sim
cd ai-society-sim
pip install -e .
cp .env.example .env
# fill in your API key or local model config
ai-society-sim --config configs/default.yaml