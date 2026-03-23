from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt


PLOT_KEYS = [
    "unemployment_rate",
    "wealth_inequality",
    "ai_capability",
    "total_productivity",
    "social_trust",
    "cooperation_index",
    "worker_power",
    "corporate_power",
    "average_living_standard",
    "government_effectiveness",
    "innovation_rate",
    "social_mobility",
]


def plot_dashboard(world, output_dir: str):
    available = [(k, world.metrics[k]) for k in PLOT_KEYS if k in world.metrics]
    if not available:
        print("No metrics to plot.")
        return None

    cols = 4
    rows = (len(available) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(20, 5 * rows))
    fig.suptitle("AI Society Simulation Dashboard", fontsize=14, fontweight="bold")

    if rows == 1:
        axes = [axes]
    flat = [ax for row in axes for ax in row]

    colors = [
        "#e74c3c", "#9b59b6", "#3498db", "#2ecc71",
        "#1abc9c", "#f39c12", "#e67e22", "#c0392b",
        "#16a085", "#2980b9", "#8e44ad", "#27ae60"
    ]

    for i, (key, vals) in enumerate(available):
        ax = flat[i]
        y = [0 if v is None else v for v in vals]
        x = list(range(len(y)))
        c = colors[i % len(colors)]

        ax.plot(x, y, linestyle="-", marker="o", color=c, lw=2, markersize=4)
        ax.fill_between(x, y, alpha=0.12, color=c)
        ax.set_title(key.replace("_", " ").title(), fontsize=10)
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        if key != "total_productivity":
            ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.2)

    for j in range(i + 1, len(flat)):
        flat[j].set_visible(False)

    plt.tight_layout()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out = Path(output_dir) / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[Saved figure] {out}")
    plt.show()
    return out