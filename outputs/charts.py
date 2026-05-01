from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt



def save_std_xt_plot(time_grid: List[float], std_xt: List[float], title: str, file_path: Path, label: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(time_grid, std_xt, label=label, linewidth=2)
    plt.xlabel("t")
    plt.ylabel("Std of X(t)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()



def save_overlay_std_xt_plot(
    weekly_time: List[float],
    weekly_std: List[float],
    daily_time: List[float],
    daily_std: List[float],
    title: str,
    file_path: Path,
) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(weekly_time, weekly_std, label="Weekly", linewidth=2)
    plt.plot(daily_time, daily_std, label="Daily", linewidth=2)
    plt.xlabel("t")
    plt.ylabel("Std of X(t)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()



def save_terminal_histogram(values: Iterable[float], title: str, file_path: Path, color: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.hist(list(values), bins=20, color=color, alpha=0.75, edgecolor="black")
    plt.xlabel("Terminal X(T)")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()



def save_comparison_bar_chart(labels: List[str], values: List[float], title: str, ylabel: str, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 5))
    plt.bar(labels, values, color=["steelblue", "darkorange"])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(file_path, dpi=150)
    plt.close()
