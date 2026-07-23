#!/usr/bin/env python3
"""
Singh Ji AI Ultra v8.0 - Universal Visual Generator (World-Class Edition)
Kisi bhi module ke liye auto infographic/image generate karta hai.

Improvements over v7.0:
- Safe emoji/Unicode handling (falls back cleanly instead of showing boxes)
- Full input validation with descriptive errors (no silent crashes)
- Dynamic layout (works correctly regardless of item count)
- Logging instead of bare print()
- Type hints throughout
- Configurable output DPI/size
- Font auto-detection with graceful degradation

Usage:
    python singhji_visual_v2.py --module goldrate --data '{"city": "Delhi", "22k": 72500, "24k": 79000}'
    python singhji_visual_v2.py --module weather --data '{"city": "Kanpur", "temp": 35, "condition": "Sunny"}'

Output: singhji_<module>_visual.png
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # headless-safe backend — critical for servers (Railway/Oracle)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.font_manager as fm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | singhji_visual | %(message)s",
)
logger = logging.getLogger("singhji_visual")

# ===================== FONT SAFETY =====================
# Emoji / Devanagari glyphs are frequently missing on headless Linux servers.
# Rather than crash or render "tofu" boxes, we detect availability once and
# strip unsupported glyphs so text always renders cleanly.

_EMOJI_SAFE = False
try:
    _available_fonts = {f.name for f in fm.fontManager.ttflist}
    _EMOJI_SAFE = any(
        name in _available_fonts
        for name in ("Noto Color Emoji", "Segoe UI Emoji", "Apple Color Emoji")
    )
except Exception as exc:  # pragma: no cover - defensive
    logger.warning(f"Font detection failed, assuming no emoji support: {exc}")


def safe_text(text: str) -> str:
    """Strip emoji from text if the runtime font can't render them,
    so we get a clean label instead of a missing-glyph box."""
    if _EMOJI_SAFE:
        return text
    return "".join(ch for ch in text if ord(ch) < 0x2100).strip() or text


# ===================== COLOR THEMES =====================
THEMES: Dict[str, Dict[str, str]] = {
    "goldrate": {"primary": "#FFD700", "secondary": "#FFA000", "bg": "#FFF8E1", "accent": "#FF6F00", "title": "Sone Ka Bhav", "icon": "\U0001F4B0"},
    "weather": {"primary": "#2196F3", "secondary": "#03A9F4", "bg": "#E3F2FD", "accent": "#0D47A1", "title": "Mausam Report", "icon": "\U0001F324"},
    "mandi": {"primary": "#4CAF50", "secondary": "#8BC34A", "bg": "#E8F5E9", "accent": "#1B5E20", "title": "Mandi Rates", "icon": "\U0001F96C"},
    "fuel": {"primary": "#795548", "secondary": "#A1887F", "bg": "#EFEBE9", "accent": "#3E2723", "title": "Fuel Price", "icon": "\u26FD"},
    "bachpan": {"primary": "#E91E63", "secondary": "#F48FB1", "bg": "#FCE4EC", "accent": "#880E4F", "title": "Bachpan Ki Yaadein", "icon": "\U0001F388"},
    "schedule": {"primary": "#607D8B", "secondary": "#90A4AE", "bg": "#ECEFF1", "accent": "#263238", "title": "Daily Schedule", "icon": "\U0001F4C5"},
    "news": {"primary": "#F44336", "secondary": "#EF5350", "bg": "#FFEBEE", "accent": "#B71C1C", "title": "Breaking News", "icon": "\U0001F4F0"},
    "horoscope": {"primary": "#9C27B0", "secondary": "#CE93D8", "bg": "#F3E5F5", "accent": "#4A148C", "title": "Aaj Ka Rashifal", "icon": "\U0001F52E"},
    "rozgar": {"primary": "#00BCD4", "secondary": "#4DD0E1", "bg": "#E0F7FA", "accent": "#006064", "title": "Naukri Updates", "icon": "\U0001F4BC"},
    "default": {"primary": "#1a237e", "secondary": "#3949ab", "bg": "#E8EAF6", "accent": "#0d1642", "title": "Singh Ji AI", "icon": "\U0001F680"},
}

VERSION = "8.0"
UPI_ID = "jp200883@sbi"
CANVAS_W, CANVAS_H = 10, 20


# ===================== VALIDATION =====================

class VisualGenerationError(Exception):
    """Raised when input data is invalid or generation fails."""


def validate_inputs(module: str, data: Any) -> Dict[str, Any]:
    if not isinstance(module, str) or not module.strip():
        raise VisualGenerationError("module name khaali ya invalid hai")
    if not isinstance(data, dict):
        raise VisualGenerationError("data ek JSON object (dict) hona chahiye")
    if len(data) == 0:
        raise VisualGenerationError("data khaali hai — kam se kam ek key-value chahiye")
    return data


# ===================== DRAW HELPERS =====================

def draw_header(ax, theme: Dict[str, str], module_name: str, y_pos: float) -> float:
    header = FancyBboxPatch((0.5, y_pos - 1.2), 9, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=theme["primary"], alpha=0.15,
                             edgecolor=theme["primary"], linewidth=3)
    ax.add_patch(header)

    ax.text(5, y_pos - 0.2, "SINGH JI AI", fontsize=28, fontweight="bold",
            ha="center", color=theme["accent"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor=theme["primary"],
                       alpha=0.2, edgecolor=theme["primary"], linewidth=2))

    subtitle = safe_text(f'v{VERSION} | {theme["icon"]} {theme["title"]} | {module_name.upper()}')
    ax.text(5, y_pos - 0.7, subtitle, fontsize=14, ha="center",
            color=theme["accent"], style="italic")

    return y_pos - 1.8


def draw_default_visual(ax, data: Dict[str, Any], theme: Dict[str, str], y_start: float) -> float:
    """Dynamic grid — lays out however many items exist (up to 6),
    instead of assuming a fixed count like the original."""
    y = y_start
    ax.text(5, y, safe_text(f'{theme["icon"]} {theme["title"]}'),
            fontsize=20, fontweight="bold", ha="center", color=theme["accent"])
    y -= 1.5

    items: List[Tuple[str, Any]] = list(data.items())[:6]
    colors = ["#F44336", "#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#00BCD4"]

    cols = 2
    rows = (len(items) + 1) // cols
    row_height = 2.5
    for i, (key, value) in enumerate(items):
        col = i % cols
        row = i // cols
        x = 2.5 if col == 0 else 7.5
        card_y = y - row * row_height - 1

        color = colors[i % len(colors)]
        card = FancyBboxPatch((x - 1.8, card_y - 1), 3.6, 2,
                               boxstyle="round,pad=0.15",
                               facecolor=color, alpha=0.15,
                               edgecolor=color, linewidth=2.5)
        ax.add_patch(card)
        ax.text(x, card_y + 0.3, safe_text(str(key).title()), fontsize=11,
                fontweight="bold", ha="center", color=color)
        ax.text(x, card_y - 0.3, safe_text(str(value)), fontsize=14,
                fontweight="bold", ha="center", color="#333")

    return y - rows * row_height - 1


def draw_goldrate_visual(ax, data: Dict[str, Any], theme: Dict[str, str], y_start: float) -> float:
    y = y_start
    ax.text(5, y, safe_text(f'{theme["icon"]} Aaj Ka Sone Ka Bhav'),
            fontsize=20, fontweight="bold", ha="center", color=theme["accent"])
    y -= 1.2

    city = str(data.get("city", "India"))
    ax.text(5, y, f"Shahar: {city}", fontsize=12, ha="center", color="#666")
    y -= 1.5

    rates = {
        "24 Karat": _safe_number(data.get("24k"), 79000),
        "22 Karat": _safe_number(data.get("22k"), 72500),
        "18 Karat": _safe_number(data.get("18k"), 59500),
    }
    max_rate = max(rates.values()) or 1
    bar_width = 2.5
    x_positions = [2, 5, 8]

    for i, (purity, rate) in enumerate(rates.items()):
        bar_height = max((rate / max_rate) * 4, 0.3)
        bar = FancyBboxPatch((x_positions[i] - bar_width / 2, y - bar_height), bar_width, bar_height,
                              boxstyle="round,pad=0.05",
                              facecolor=theme["primary"], alpha=0.7,
                              edgecolor=theme["accent"], linewidth=2)
        ax.add_patch(bar)
        ax.text(x_positions[i], y - bar_height / 2, f"\u20B9{rate:,.0f}",
                fontsize=14, fontweight="bold", ha="center", va="center", color="white")
        ax.text(x_positions[i], y - bar_height - 0.4, purity,
                fontsize=11, fontweight="bold", ha="center", color=theme["accent"])
        ax.text(x_positions[i], y - bar_height - 0.8, "per 10g",
                fontsize=9, ha="center", color="#888")

    y -= 6
    trend = str(data.get("trend", "stable")).lower()
    trend_color = "#4CAF50" if trend == "up" else "#F44336" if trend == "down" else "#FF9800"
    trend_text = safe_text(
        "\u25B2 Badh Raha Hai" if trend == "up"
        else "\u25BC Ghat Raha Hai" if trend == "down"
        else "Stable"
    )
    trend_box = FancyBboxPatch((3, y - 0.5), 4, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor=trend_color, alpha=0.15,
                                edgecolor=trend_color, linewidth=2)
    ax.add_patch(trend_box)
    ax.text(5, y - 0.1, trend_text, fontsize=12, fontweight="bold", ha="center", color=trend_color)

    return y - 1.5


def draw_weather_visual(ax, data: Dict[str, Any], theme: Dict[str, str], y_start: float) -> float:
    y = y_start
    ax.text(5, y, safe_text(f'{theme["icon"]} Mausam Report'),
            fontsize=20, fontweight="bold", ha="center", color=theme["accent"])
    y -= 1.2

    city = str(data.get("city", "Your City"))
    temp = _safe_number(data.get("temp"), 30)
    condition = str(data.get("condition", "Sunny"))
    humidity = _safe_number(data.get("humidity"), 60)

    circle = Circle((5, y - 2), 1.8, facecolor=theme["primary"],
                     alpha=0.2, edgecolor=theme["primary"], linewidth=4)
    ax.add_patch(circle)
    ax.text(5, y - 1.8, f"{temp:g}\u00b0C", fontsize=36, fontweight="bold",
            ha="center", va="center", color=theme["accent"])
    ax.text(5, y - 3.2, condition, fontsize=14, ha="center", color="#666")

    y -= 5
    stats = [
        ("Shahar", city, "#2196F3"),
        ("Nami", f"{humidity:g}%", "#03A9F4"),
        ("Hawa", str(data.get("wind", "10 km/h")), "#00BCD4"),
    ]
    x_stats = [2, 5, 8]
    for i, (label, value, color) in enumerate(stats):
        box = FancyBboxPatch((x_stats[i] - 1, y - 0.8), 2, 1.2,
                              boxstyle="round,pad=0.1",
                              facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x_stats[i], y - 0.2, value, fontsize=12, fontweight="bold", ha="center", color=color)
        ax.text(x_stats[i], y - 0.6, label, fontsize=10, ha="center", color="#666")

    return y - 2


def _safe_number(value: Any, default: float) -> float:
    """Coerce to float; falls back to default instead of crashing on bad input."""
    try:
        if value is None:
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        logger.warning(f"Invalid numeric value {value!r}, using default {default}")
        return float(default)


VISUAL_FUNCTIONS: Dict[str, Callable] = {
    "goldrate": draw_goldrate_visual,
    "weather": draw_weather_visual,
}


# ===================== MAIN GENERATOR =====================

def generate_visual(module: str, data_dict: Dict[str, Any], output_path: Optional[str] = None,
                     dpi: int = 200) -> str:
    """Generate visual for any module. Raises VisualGenerationError on bad input."""
    data_dict = validate_inputs(module, data_dict)
    module_key = module.strip().lower()
    theme = THEMES.get(module_key, THEMES["default"])

    if output_path is None:
        safe_module = "".join(c for c in module_key if c.isalnum() or c in ("_", "-")) or "module"
        output_path = f"singhji_{safe_module}_visual.png"

    fig = None
    try:
        fig, ax = plt.subplots(figsize=(12, 16))
        ax.set_xlim(0, CANVAS_W)
        ax.set_ylim(0, CANVAS_H)
        ax.axis("off")
        fig.patch.set_facecolor(theme["bg"])

        y_pos = 18.5
        y_pos = draw_header(ax, theme, module_key, y_pos)

        visual_func = VISUAL_FUNCTIONS.get(module_key, draw_default_visual)
        try:
            visual_func(ax, data_dict, theme, y_pos)
        except Exception as exc:
            # A broken module-specific renderer shouldn't kill the whole image —
            # fall back to the generic card layout instead.
            logger.error(f"'{module_key}' renderer failed ({exc}); falling back to default layout")
            draw_default_visual(ax, data_dict, theme, y_pos)

        footer_y = 1.5
        footer = FancyBboxPatch((0.5, footer_y - 0.8), 9, 1,
                                 boxstyle="round,pad=0.1",
                                 facecolor=theme["primary"], alpha=0.1,
                                 edgecolor=theme["primary"], linewidth=2)
        ax.add_patch(footer)
        ax.text(5, footer_y - 0.1, f"Singh Ji AI Ultra v{VERSION} | Made in India",
                fontsize=10, ha="center", color=theme["accent"], style="italic")
        ax.text(5, footer_y - 0.5, f"Generated: Auto | UPI: {UPI_ID}",
                fontsize=8, ha="center", color="#888")

        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                     facecolor=theme["bg"], edgecolor="none")

        logger.info(f"Visual generated: {os.path.abspath(output_path)}")
        return output_path
    finally:
        if fig is not None:
            plt.close(fig)


# ===================== CLI =====================

def main() -> None:
    parser = argparse.ArgumentParser(description="Singh Ji AI Visual Generator")
    parser.add_argument("--module", required=True,
                         help="Module name: goldrate, weather, mandi, fuel, bachpan, schedule, news, etc.")
    parser.add_argument("--data", required=True, help="JSON data string")
    parser.add_argument("--output", default=None, help="Output file path (optional)")
    parser.add_argument("--dpi", type=int, default=200, help="Output image DPI (default 200)")

    args = parser.parse_args()

    try:
        data_dict = json.loads(args.data)
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON: {exc}")
        print('Example: --data \'{"petrol": 96.72, "diesel": 89.62}\'')
        sys.exit(1)

    try:
        generate_visual(args.module, data_dict, args.output, dpi=args.dpi)
    except VisualGenerationError as exc:
        logger.error(str(exc))
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - last resort
        logger.error(f"Unexpected failure: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
