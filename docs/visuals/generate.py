"""Rebuild documentation figures from algorithm examples and recorded measurements.

Run from any directory with Python 3.11+ and matplotlib installed.
This script reads the committed benchmark JSON; it does not rerun benchmarks.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAVY, TEAL, MUTED = "#19364d", "#007f79", "#526575"
PALE, GRID, ORANGE = "#e7f5f2", "#dce5ea", "#b66432"
BASELINE = "#687c91"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "text.color": NAVY, "axes.labelcolor": NAVY,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "svg.fonttype": "none", "svg.hashsalt": "selected-cpp-visuals-v1",
    "figure.facecolor": "white", "savefig.facecolor": "white",
})


def save(fig, name):
    for suffix in ("svg", "png"):
        metadata = {"Date": None} if suffix == "svg" else {}
        destination = HERE / f"{name}.{suffix}"
        fig.savefig(destination, dpi=160, metadata=metadata)
        if suffix == "svg":
            # Matplotlib adds harmless trailing spaces inside path data; remove
            # them so regenerated vector assets have clean, readable diffs.
            lines = destination.read_text(encoding="utf-8").splitlines()
            destination.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")
    plt.close(fig)


def canvas(title, subtitle, height=6.2):
    fig = plt.figure(figsize=(10, height))
    ax = fig.add_axes((0, 0, 1, 1), xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ax.text(.05, .94, title, fontsize=22, weight="bold", va="top")
    ax.text(.05, .872, subtitle, fontsize=12.4, va="top", color=MUTED)
    return fig, ax


def box(ax, x, y, width, height, fill="white", edge=GRID):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                              boxstyle="round,pad=0.008,rounding_size=0.012",
                              facecolor=fill, edgecolor=edge, linewidth=1.1))


def cycle_diagram():
    fig, ax = canvas("Reach a cycle without repeating DFS",
                     "Reverse sink elimination keeps cycle vertices and every vertex that can reach them.")
    positions = {"A": (.15, .60), "B": (.39, .69), "C": (.66, .69),
                 "D": (.39, .46), "E": (.66, .46)}
    edges = [("A", "B"), ("B", "C"), ("C", "B"), ("A", "D"), ("D", "E")]
    for source, target in edges:
        curved = source in "BC" and target in "BC"
        ax.add_patch(FancyArrowPatch(positions[source], positions[target],
                     arrowstyle="-|>", mutation_scale=20, linewidth=2,
                     shrinkA=24, shrinkB=25, color=TEAL if target in "BC" else ORANGE,
                     connectionstyle="arc3,rad=-0.22" if curved else "arc3,rad=0"))
    for name, (x, y) in positions.items():
        retained = name in "ABC"
        ax.add_patch(Circle((x, y), .038, facecolor=PALE if retained else "#fff2e9",
                            edgecolor=TEAL if retained else ORANGE, linewidth=2))
        ax.text(x, y, name, fontsize=17, weight="bold", ha="center", va="center")
    ax.text(.15, .51, "still has B", ha="center", fontsize=11.5, color=TEAL)
    ax.text(.78, .70, "A, B, C survive", color=TEAL, weight="bold", fontsize=12)
    ax.text(.78, .655, "A reaches B ↔ C", color=MUTED, fontsize=11.5)
    ax.text(.78, .465, "D, E are removed", color=ORANGE, weight="bold", fontsize=12)
    ax.text(.78, .42, "Neither reaches a cycle", color=MUTED, fontsize=11)
    steps = [
        ("1  Remove E", "E has no outgoing edges.\nIts predecessor D becomes a sink."),
        ("2  Remove D", "A loses the edge to D.\nIts edge to B keeps it alive."),
        ("3  Answer queries", "Survivor → safe\nRemoved or unknown → trapped"),
    ]
    for i, (heading, body) in enumerate(steps):
        x = .05 + i * .305
        box(ax, x, .17, .285, .19, fill=PALE if i == 2 else "#f7f9fb")
        ax.text(x + .016, .325, heading, fontsize=13, weight="bold", va="top")
        ax.text(x + .016, .265, body, fontsize=10.5, linespacing=1.65, va="top")
    ax.text(.05, .10, "One graph pass: O(V + E) preprocessing  •  Expected O(1) per named query",
            fontsize=12, weight="bold", color=TEAL)
    ax.text(.05, .052, "Survivors have a surviving successor: following successors in a finite graph must repeat a vertex.",
            fontsize=10.5, color=MUTED)
    save(fig, "cycle-reachability")


def lcs_diagram():
    first, second = "ABCBDAB", "BDCABA"
    values = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    for i, a in enumerate(first, 1):
        for j, b in enumerate(second, 1):
            values[i][j] = values[i - 1][j - 1] + 1 if a == b else max(values[i - 1][j], values[i][j - 1])
    assert values[-1][-1] == 4
    fig, ax = canvas("LCS: keep the dependencies, discard the history",
                     'Example: "ABCBDAB" and "BDCABA" have longest common subsequence length 4.', 7)
    left, top, width, height = .105, .775, .056, .054
    for j, char in enumerate("∅" + second):
        ax.text(left + (j + .5) * width, top + .023, char, ha="center", fontsize=13, weight="bold")
    for i, row in enumerate(values):
        y = top - (i + 1) * height
        ax.text(left - .025, y + height / 2, ("∅" + first)[i], ha="center", va="center",
                fontsize=13, weight="bold")
        for j, value in enumerate(row):
            active = i >= len(first) - 1
            face = PALE if active else "#f1f4f6"
            ax.add_patch(Rectangle((left + j * width, y), width, height,
                         facecolor=face, edgecolor="white", linewidth=2))
            ax.text(left + (j + .5) * width, y + height / 2, str(value), ha="center", va="center",
                    color=TEAL if active else "#84919b", fontsize=13,
                    weight="bold" if active else "normal")
    ax.text(.105, .302, "Only the last two rows are live here.", color=TEAL, fontsize=11.3, weight="bold")
    box(ax, .56, .34, .38, .435, fill="#f7f9fb")
    ax.text(.583, .737, "Three dependencies per cell", fontsize=14, weight="bold", va="top")
    ax.text(.583, .68, "When the last characters match", color=MUTED, fontsize=11.5)
    ax.text(.583, .633, "current[j] = previous[j−1] + 1", fontsize=12, color=TEAL, weight="bold")
    ax.text(.583, .587, "Otherwise", color=MUTED, fontsize=11.5)
    ax.text(.583, .54, "current[j] = max(previous[j],\n                            current[j−1])",
            fontsize=11.5, color=TEAL, weight="bold", linespacing=1.5, va="top")
    ax.text(.583, .4, "Then swap the row buffers.", fontsize=12, weight="bold")
    box(ax, .05, .13, .89, .11, fill=PALE)
    ax.text(.073, .198, "O(nm) time", fontsize=14, weight="bold", va="center")
    ax.text(.30, .198, "O(min(n, m)) DP storage", fontsize=14, weight="bold", va="center")
    ax.text(.073, .158, "Place the shorter string in columns; keep two arrays of min(n, m) + 1 integers.",
            fontsize=11.5, va="center", color=MUTED)
    ax.text(.05, .066, "Returns the length only. Input strings use additional O(n + m) storage; reconstruction needs another design.",
            fontsize=10.3, color=MUTED)
    save(fig, "rolling-row-lcs")


def benchmark_plot():
    data_path = ROOT / "benchmarks" / "windows-gcc-2026-10-02.json"
    report = json.loads(data_path.read_text(encoding="utf-8"))
    records = report["records"]
    # Refuse to silently plot stale or incomparable sources/units.
    for filename, digest in report["source_sha256"].items():
        assert hashlib.sha256((ROOT / "solutions" / filename).read_bytes()).hexdigest() == digest, filename
    for record in records:
        assert len(record["samples"]) == report["repeats"] == 3
        assert median(s["seconds"] for s in record["samples"]) == record["median_seconds"]
        assert all(s["memory_method"] == "Windows PeakWorkingSetSize, bytes" for s in record["samples"])
        partner = next(r for r in records if r["solution"] == record["solution"] and
                       r["size"] == record["size"] and r["version"] != record["version"])
        assert partner["input_sha256"] == record["input_sha256"]
        assert len({s["output_sha256"] for r in (record, partner) for s in r["samples"]}) == 1
    fig, axes = plt.subplots(2, 2, figsize=(10, 8.3))
    fig.subplots_adjust(left=.085, right=.965, bottom=.19, top=.785, hspace=.62, wspace=.3)
    fig.text(.05, .95, "The algorithm change, measured", fontsize=22, weight="bold", va="top")
    fig.text(.05, .90, "All recorded workloads • medians joined by lines; dots show every one of the three runs",
             fontsize=11.7, color=MUTED, va="top")
    fig.text(.05, .855, "●  Baseline c45d1b3", color=BASELINE, fontsize=12, weight="bold")
    fig.text(.33, .855, "●  Current implementation", color=TEAL, fontsize=12, weight="bold")
    for col, (solution, key, subtitle) in enumerate([
        ("directed_cycle_reachability", "vertices", "Cycle reachability · 5,000 queries"),
        ("longest_common_subsequence", "first_length", "LCS · two equal-length strings"),
    ]):
        for row, (metric, unit, label) in enumerate([
            ("seconds", 1, "Wall time (seconds)"),
            ("peak_memory_bytes", 1024**2, "Peak working set (MiB)"),
        ]):
            ax = axes[row, col]
            for version, color in (("baseline", BASELINE), ("current", TEAL)):
                group = sorted((r for r in records if r["solution"] == solution and r["version"] == version),
                               key=lambda r: r["size"][key])
                x = [r["size"][key] for r in group]
                y = [median(s[metric] / unit for s in r["samples"]) for r in group]
                ax.plot(x, y, color=color, linewidth=2.2, marker="o", markersize=5, zorder=3)
                for rec in group:
                    ax.scatter([rec["size"][key]] * 3,
                               [s[metric] / unit for s in rec["samples"]],
                               s=40, facecolors="none", edgecolors=color, linewidths=1, alpha=.65, zorder=4)
                plot_max = max(s[metric] / unit for r in records if r["solution"] == solution for s in r["samples"])
                offset = 9 if version == "baseline" or y[-1] < plot_max * .15 else -16
                ax.annotate(f"{y[-1]:.3f}" if row == 0 else f"{y[-1]:.2f}",
                            (x[-1], y[-1]), xytext=(-4, offset), textcoords="offset points",
                            ha="right", color=color, weight="bold", fontsize=10.5)
            ax.set_title(subtitle if row == 0 else "Memory, measured separately", loc="left", fontsize=12.5, weight="bold", pad=10)
            ax.set_ylabel(label, fontsize=10.8)
            ax.set_xlabel("Graph vertices" if col == 0 else "Characters in each string", fontsize=10.8)
            ax.set_xticks(x, [f"{n:,}" for n in x])
            ax.tick_params(labelsize=10)
            ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.18)
            ax.set_xlim(min(x) * .75, max(x) * 1.06)
            ax.grid(axis="y", color=GRID, linewidth=.8)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            for spine in ("left", "bottom"):
                ax.spines[spine].set_color(GRID)
    fig.text(.05, .104, "Windows 11 · GCC 12.2.0 · -O2 · seed 20261002 · recorded 2 October 2026", fontsize=10.5, color=MUTED)
    fig.text(.05, .068, "Time includes startup and I/O. Memory is whole-process peak working set. Axes have independent scales.", fontsize=10, color=MUTED)
    fig.text(.05, .035, "A local comparison on specific inputs, not a universal speed claim. Source: benchmarks/windows-gcc-2026-10-02.json", fontsize=9.6, color=MUTED)
    save(fig, "benchmark-comparison")


if __name__ == "__main__":
    cycle_diagram()
    lcs_diagram()
    benchmark_plot()
    print("Generated three SVG/PNG figure pairs; benchmark source hashes, units and matching outputs verified.")
