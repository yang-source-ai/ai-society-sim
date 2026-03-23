import argparse
import json
from pathlib import Path
from datetime import datetime

from .config import load_settings
from .simulation import run_simulation
from .viz import plot_dashboard


def main():
    parser = argparse.ArgumentParser(description="AI Society Simulator")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config")
    parser.add_argument("--years", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--base-url", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    settings = load_settings(args.config)

    if args.years is not None:
        settings.years = args.years
    if args.dry_run:
        settings.dry_run = True
    if args.model:
        settings.model = args.model
    if args.base_url:
        settings.base_url = args.base_url
    if args.output_dir:
        settings.output_dir = args.output_dir

    result = run_simulation(settings)

    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    history_path = out_dir / f"history_{ts}.json"
    forum_path = out_dir / f"forum_{ts}.json"
    summary_path = out_dir / f"summaries_{ts}.json"

    history_path.write_text(
        json.dumps(result.world.history, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    forum_path.write_text(
        json.dumps(result.forum.posts, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    summary_path.write_text(
        json.dumps(result.summaries, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[Saved] {history_path}")
    print(f"[Saved] {forum_path}")
    print(f"[Saved] {summary_path}")

    if not args.no_plot:
        plot_dashboard(result.world, settings.output_dir)
        
if __name__ == "__main__":
    main()