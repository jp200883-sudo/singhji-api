#!/usr/bin/env python3
"""
Singh Ji AI Ultra v7.0 - Universal Visual Generator
Kisi bhi module ke liye auto infographic/image generate karta hai

Usage:
    python singhji_visual.py --module goldrate --data '{"city": "Delhi", "22k": 72500, "24k": 79000}'
    python singhji_visual.py --module weather --data '{"city": "Kanpur", "temp": 35, "condition": "Sunny"}'
    python singhji_visual.py --module mandi --data '{"aloo": 20, "pyaz": 30, "tamatar": 40}'
    python singhji_visual.py --module fuel --data '{"petrol": 96.72, "diesel": 89.62}'
    python singhji_visual.py --module bachpan --data '{"topic": "school", "memory": "PT period"}'
    python singhji_visual.py --module schedule --data '{"water": "6-9 AM", "power": "2-4 PM"}'

Output: singhji_<module>_visual.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Wedge
import json
import sys
import os
import argparse

# ===================== COLOR THEMES =====================
THEMES = {
    "goldrate": {
        "primary": "#FFD700",
        "secondary": "#FFA000",
        "bg": "#FFF8E1",
        "accent": "#FF6F00",
        "title": "Sone Ka Bhav",
        "icon": "💰"
    },
    "weather": {
        "primary": "#2196F3",
        "secondary": "#03A9F4",
        "bg": "#E3F2FD",
        "accent": "#0D47A1",
        "title": "Mausam Report",
        "icon": "🌤️"
    },
    "mandi": {
        "primary": "#4CAF50",
        "secondary": "#8BC34A",
        "bg": "#E8F5E9",
        "accent": "#1B5E20",
        "title": "Mandi Rates",
        "icon": "🥬"
    },
    "fuel": {
        "primary": "#795548",
        "secondary": "#A1887F",
        "bg": "#EFEBE9",
        "accent": "#3E2723",
        "title": "Fuel Price",
        "icon": "⛽"
    },
    "bachpan": {
        "primary": "#E91E63",
        "secondary": "#F48FB1",
        "bg": "#FCE4EC",
        "accent": "#880E4F",
        "title": "Bachpan Ki Yaadein",
        "icon": "🎈"
    },
    "schedule": {
        "primary": "#607D8B",
        "secondary": "#90A4AE",
        "bg": "#ECEFF1",
        "accent": "#263238",
        "title": "Daily Schedule",
        "icon": "📅"
    },
    "news": {
        "primary": "#F44336",
        "secondary": "#EF5350",
        "bg": "#FFEBEE",
        "accent": "#B71C1C",
        "title": "Breaking News",
        "icon": "📰"
    },
    "horoscope": {
        "primary": "#9C27B0",
        "secondary": "#CE93D8",
        "bg": "#F3E5F5",
        "accent": "#4A148C",
        "title": "Aaj Ka Rashifal",
        "icon": "🔮"
    },
    "rozgar": {
        "primary": "#00BCD4",
        "secondary": "#4DD0E1",
        "bg": "#E0F7FA",
        "accent": "#006064",
        "title": "Naukri Updates",
        "icon": "💼"
    },
    "default": {
        "primary": "#1a237e",
        "secondary": "#3949ab",
        "bg": "#E8EAF6",
        "accent": "#0d1642",
        "title": "Singh Ji AI",
        "icon": "🚀"
    }
}

# ===================== VISUAL GENERATORS =====================

def draw_header(ax, theme, module_name, y_pos):
    """Draw Singh Ji header"""
    # Main header box
    header = FancyBboxPatch((0.5, y_pos-1.2), 9, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=theme["primary"], alpha=0.15, 
                            edgecolor=theme["primary"], linewidth=3)
    ax.add_patch(header)

    # Singh Ji branding
    ax.text(5, y_pos-0.2, 'SINGH JI AI', fontsize=28, fontweight='bold', 
            ha='center', color=theme["accent"],
            bbox=dict(boxstyle='round,pad=0.4', facecolor=theme["primary"], 
                     alpha=0.2, edgecolor=theme["primary"], linewidth=2))

    ax.text(5, y_pos-0.7, f'v7.0 | {theme["icon"]} {theme["title"]} | {module_name.upper()}', 
            fontsize=14, ha='center', color=theme["accent"], style='italic')

    return y_pos - 1.8

def draw_goldrate_visual(ax, data, theme, y_start):
    """Gold rate specific visual"""
    y = y_start

    # Title
    ax.text(5, y, f'{theme["icon"]} Aaj Ka Sone Ka Bhav', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    city = data.get("city", "India")
    ax.text(5, y, f'Shahar: {city}', fontsize=12, ha='center', color='#666')
    y -= 1.5

    # Gold bars visualization
    rates = {
        "24 Karat": data.get("24k", 79000),
        "22 Karat": data.get("22k", 72500),
        "18 Karat": data.get("18k", 59500)
    }

    max_rate = max(rates.values())
    bar_width = 2.5
    x_positions = [2, 5, 8]

    for i, (purity, rate) in enumerate(rates.items()):
        bar_height = (rate / max_rate) * 4

        # Bar
        bar = FancyBboxPatch((x_positions[i]-bar_width/2, y-bar_height), bar_width, bar_height,
                             boxstyle="round,pad=0.05", 
                             facecolor=theme["primary"], alpha=0.7, 
                             edgecolor=theme["accent"], linewidth=2)
        ax.add_patch(bar)

        # Rate text
        ax.text(x_positions[i], y-bar_height/2, f'₹{rate:,}', 
                fontsize=14, fontweight='bold', ha='center', va='center', color='white')

        # Purity label
        ax.text(x_positions[i], y-bar_height-0.4, purity, 
                fontsize=11, fontweight='bold', ha='center', color=theme["accent"])

        # Per 10g
        ax.text(x_positions[i], y-bar_height-0.8, 'per 10g', 
                fontsize=9, ha='center', color='#888')

    y -= 6

    # Trend indicator
    trend = data.get("trend", "stable")
    trend_color = "#4CAF50" if trend == "up" else "#F44336" if trend == "down" else "#FF9800"
    trend_text = "▲ Badh Raha Hai" if trend == "up" else "▼ Ghat Raha Hai" if trend == "down" else "➡️ Stable"

    trend_box = FancyBboxPatch((3, y-0.5), 4, 0.8,
                               boxstyle="round,pad=0.1", 
                               facecolor=trend_color, alpha=0.15, 
                               edgecolor=trend_color, linewidth=2)
    ax.add_patch(trend_box)
    ax.text(5, y-0.1, trend_text, fontsize=12, fontweight='bold', 
            ha='center', color=trend_color)

    return y - 1.5

def draw_weather_visual(ax, data, theme, y_start):
    """Weather specific visual"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} Mausam Report', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    city = data.get("city", "Your City")
    temp = data.get("temp", 30)
    condition = data.get("condition", "Sunny")
    humidity = data.get("humidity", 60)

    # Big temperature circle
    circle = Circle((5, y-2), 1.8, facecolor=theme["primary"], 
                   alpha=0.2, edgecolor=theme["primary"], linewidth=4)
    ax.add_patch(circle)
    ax.text(5, y-1.8, f'{temp}°C', fontsize=36, fontweight='bold', 
            ha='center', va='center', color=theme["accent"])
    ax.text(5, y-3.2, condition, fontsize=14, ha='center', color='#666')

    y -= 5

    # Stats boxes
    stats = [
        ("Shahar", city, "#2196F3"),
        ("Nami", f'{humidity}%', "#03A9F4"),
        ("Hawa", data.get("wind", "10 km/h"), "#00BCD4")
    ]

    x_stats = [2, 5, 8]
    for i, (label, value, color) in enumerate(stats):
        box = FancyBboxPatch((x_stats[i]-1, y-0.8), 2, 1.2,
                             boxstyle="round,pad=0.1", 
                             facecolor=color, alpha=0.15, 
                             edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x_stats[i], y-0.2, value, fontsize=12, fontweight='bold', 
                ha='center', color=color)
        ax.text(x_stats[i], y-0.6, label, fontsize=10, ha='center', color='#666')

    return y - 2

def draw_mandi_visual(ax, data, theme, y_start):
    """Mandi rates visual"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} Aaj Ki Mandi Rates', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    ax.text(5, y, 'Sabzi Mandi - ₹ per kg', fontsize=11, ha='center', color='#888')
    y -= 1.5

    items = list(data.items())[:6]  # Max 6 items

    for i, (item, price) in enumerate(items):
        row_y = y - (i * 1.3)

        # Item box
        item_box = FancyBboxPatch((1, row_y-0.4), 3, 0.9,
                                  boxstyle="round,pad=0.05", 
                                  facecolor=theme["primary"], alpha=0.15, 
                                  edgecolor=theme["primary"], linewidth=1.5)
        ax.add_patch(item_box)
        ax.text(2.5, row_y, item.title(), fontsize=12, fontweight='bold', 
                ha='center', va='center', color=theme["accent"])

        # Price box
        price_box = FancyBboxPatch((5.5, row_y-0.4), 3, 0.9,
                                   boxstyle="round,pad=0.05", 
                                   facecolor=theme["secondary"], alpha=0.3, 
                                   edgecolor=theme["accent"], linewidth=1.5)
        ax.add_patch(price_box)
        ax.text(7, row_y, f'₹{price}', fontsize=14, fontweight='bold', 
                ha='center', va='center', color=theme["accent"])

    return y - (len(items) * 1.3) - 1

def draw_fuel_visual(ax, data, theme, y_start):
    """Fuel price visual"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} Aaj Ka Fuel Rate', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    city = data.get("city", "Delhi")
    ax.text(5, y, f'Shahar: {city}', fontsize=12, ha='center', color='#666')
    y -= 1.8

    fuels = [
        ("Petrol", data.get("petrol", 96.72), "#F44336"),
        ("Diesel", data.get("diesel", 89.62), "#FF9800"),
        ("CNG", data.get("cng", 76.59), "#4CAF50")
    ]

    x_pos = [2.5, 5, 7.5]
    for i, (fuel, price, color) in enumerate(fuels):
        # Fuel pump shape
        pump = FancyBboxPatch((x_pos[i]-0.8, y-2.5), 1.6, 3,
                              boxstyle="round,pad=0.1", 
                              facecolor=color, alpha=0.2, 
                              edgecolor=color, linewidth=3)
        ax.add_patch(pump)

        ax.text(x_pos[i], y-0.5, fuel, fontsize=12, fontweight='bold', 
                ha='center', color=color)
        ax.text(x_pos[i], y-1.5, f'₹{price}', fontsize=18, fontweight='bold', 
                ha='center', color=color)
        ax.text(x_pos[i], y-2.1, 'per litre', fontsize=9, ha='center', color='#888')

    return y - 3.5

def draw_bachpan_visual(ax, data, theme, y_start):
    """Bachpan memories visual"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} Bachpan Ki Yaadein', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    topic = data.get("topic", "school").title()
    memory = data.get("memory", "Wo din yaad hai...")

    # Memory card
    card = FancyBboxPatch((1, y-4), 8, 4.5,
                          boxstyle="round,pad=0.2", 
                          facecolor=theme["bg"], 
                          edgecolor=theme["primary"], linewidth=3)
    ax.add_patch(card)

    ax.text(5, y-0.8, f'Topic: {topic}', fontsize=14, fontweight='bold', 
            ha='center', color=theme["accent"])

    # Memory text with wrapping
    words = memory.split()
    lines = []
    current_line = []
    for word in words:
        if len(' '.join(current_line + [word])) < 35:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    line_y = y - 1.8
    for line in lines[:4]:  # Max 4 lines
        ax.text(5, line_y, line, fontsize=12, ha='center', color='#444')
        line_y -= 0.6

    ax.text(5, y-3.8, '"Wo bachpan ke din..."', fontsize=10, 
            ha='center', color='#888', style='italic')

    return y - 5.2

def draw_schedule_visual(ax, data, theme, y_start):
    """Daily schedule visual"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} Aaj Ka Schedule', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.2

    today = data.get("today", "Daily")
    ax.text(5, y, f'Din: {today}', fontsize=12, ha='center', color='#666')
    y -= 1.5

    items = list(data.items())[:5]
    colors = ["#4CAF50", "#FF9800", "#2196F3", "#F44336", "#9C27B0"]

    for i, (service, timing) in enumerate(items):
        row_y = y - (i * 1.2)
        color = colors[i % len(colors)]

        # Time badge
        time_badge = FancyBboxPatch((0.8, row_y-0.35), 1.8, 0.6,
                                    boxstyle="round,pad=0.05", 
                                    facecolor=color, alpha=0.8, 
                                    edgecolor='black', linewidth=1)
        ax.add_patch(time_badge)
        ax.text(1.7, row_y-0.05, timing, fontsize=10, fontweight='bold', 
                ha='center', va='center', color='white')

        # Service name
        service_box = FancyBboxPatch((3, row_y-0.35), 6, 0.6,
                                     boxstyle="round,pad=0.05", 
                                     facecolor=color, alpha=0.15, 
                                     edgecolor=color, linewidth=1.5)
        ax.add_patch(service_box)
        ax.text(6, row_y-0.05, service.title(), fontsize=11, fontweight='bold', 
                ha='center', va='center', color=color)

    return y - (len(items) * 1.2) - 1

def draw_default_visual(ax, data, theme, y_start):
    """Default visual for any module"""
    y = y_start

    ax.text(5, y, f'{theme["icon"]} {theme["title"]}', 
            fontsize=20, fontweight='bold', ha='center', color=theme["accent"])
    y -= 1.5

    # Data cards
    items = list(data.items())[:6]
    colors = ["#F44336", "#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#00BCD4"]

    positions = [(2.5, y-1.5), (7.5, y-1.5), (2.5, y-4), (7.5, y-4), (2.5, y-6.5), (7.5, y-6.5)]

    for i, (key, value) in enumerate(items):
        if i >= len(positions):
            break
        x, card_y = positions[i]
        color = colors[i % len(colors)]

        card = FancyBboxPatch((x-1.8, card_y-1), 3.6, 2,
                              boxstyle="round,pad=0.15", 
                              facecolor=color, alpha=0.15, 
                              edgecolor=color, linewidth=2.5)
        ax.add_patch(card)

        ax.text(x, card_y+0.3, str(key).title(), fontsize=11, fontweight='bold', 
                ha='center', color=color)
        ax.text(x, card_y-0.3, str(value), fontsize=14, fontweight='bold', 
                ha='center', color='#333')

    return y - 8

# ===================== MAIN GENERATOR =====================

def generate_visual(module, data_dict, output_path=None):
    """Generate visual for any module"""

    theme = THEMES.get(module, THEMES["default"])

    if output_path is None:
        output_path = f"singhji_{module}_visual.png"

    fig, ax = plt.subplots(figsize=(12, 16))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis('off')
    fig.patch.set_facecolor(theme["bg"])

    # Header
    y_pos = 18.5
    y_pos = draw_header(ax, theme, module, y_pos)

    # Module-specific visual
    visual_functions = {
        "goldrate": draw_goldrate_visual,
        "weather": draw_weather_visual,
        "mandi": draw_mandi_visual,
        "fuel": draw_fuel_visual,
        "bachpan": draw_bachpan_visual,
        "schedule": draw_schedule_visual,
    }

    visual_func = visual_functions.get(module, draw_default_visual)
    y_pos = visual_func(ax, data_dict, theme, y_pos)

    # Footer
    footer_y = 1.5
    footer = FancyBboxPatch((0.5, footer_y-0.8), 9, 1,
                            boxstyle="round,pad=0.1", 
                            facecolor=theme["primary"], alpha=0.1, 
                            edgecolor=theme["primary"], linewidth=2)
    ax.add_patch(footer)

    ax.text(5, footer_y-0.1, 'Singh Ji AI Ultra v7.0 | Made in India', 
            fontsize=10, ha='center', color=theme["accent"], style='italic')
    ax.text(5, footer_y-0.5, f'Generated: Auto | UPI: jp200883@sbi', 
            fontsize=8, ha='center', color='#888')

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                facecolor=theme["bg"], edgecolor='none')
    plt.close()

    print(f"✅ Visual generated: {os.path.abspath(output_path)}")
    return output_path


# ===================== CLI =====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Singh Ji AI Visual Generator')
    parser.add_argument('--module', required=True, 
                       help='Module name: goldrate, weather, mandi, fuel, bachpan, schedule, news, etc.')
    parser.add_argument('--data', required=True, 
                       help='JSON data string')
    parser.add_argument('--output', default=None, 
                       help='Output file path (optional)')

    args = parser.parse_args()

    try:
        data_dict = json.loads(args.data)
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON data. Use single quotes around JSON.")
        print("Example: --data '{\"petrol\": 96.72, \"diesel\": 89.62}'")
        sys.exit(1)

    generate_visual(args.module, data_dict, args.output)
