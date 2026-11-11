#!/usr/bin/env python3
"""Render animated SVG cards for GitHub profile README."""

import json
import os
import base64
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
FONTS = ROOT / "fonts"
STATIC = os.environ.get("STATIC", "0") == "1"

# Brand colors (Zeety)
BLUE = "#0077ff"
BLUE_DARK = "#0066dd"
BLUE_WASH = "#eff5ff"
DARK = "#0f1d33"
DARK2 = "#16273e"
MUTED = "#4a5a70"
LINE = "#dde4ec"
BG = "#ffffff"
SURFACE = "#f7f9fb"

# Tile colors
TILE_BLUE = "#0077ff"
TILE_GREEN = "#1fb866"
TILE_PURPLE = "#7c3aed"

CARDS.mkdir(exist_ok=True)


def load_font_css():
    """Embed Geist font as base64 if available, otherwise use system fallback."""
    css = ""
    geist_regular = FONTS / "GeistVF.woff2"
    geist_mono = FONTS / "GeistMonoVF.woff2"

    if geist_regular.exists():
        b64 = base64.b64encode(geist_regular.read_bytes()).decode()
        css += f"@font-face{{font-family:'Geist';src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:100 900}}"
    if geist_mono.exists():
        b64 = base64.b64encode(geist_mono.read_bytes()).decode()
        css += f"@font-face{{font-family:'Geist Mono';src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:100 900}}"

    return css


def font_stack():
    return "'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


def font_mono():
    return "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"


def load_contributions():
    with open(DATA) as f:
        data = json.load(f)
    col = data["data"]["user"]["contributionsCollection"]
    cal = col["contributionCalendar"]
    weeks = cal["weeks"]
    total = cal["totalContributions"]

    monthly = defaultdict(int)
    daily = {}
    streak = 0
    current_streak = 0
    best_day = ("", 0)

    for week in weeks:
        for day in week["contributionDays"]:
            d = day["date"]
            c = day["contributionCount"]
            monthly[d[:7]] += c
            daily[d] = c
            if c > 0:
                current_streak += 1
                streak = max(streak, current_streak)
            else:
                current_streak = 0
            if c > best_day[1]:
                best_day = (d, c)

    active_days = sum(1 for c in daily.values() if c > 0)

    return {
        "total": total,
        "monthly": dict(sorted(monthly.items())),
        "daily": daily,
        "weeks": weeks,
        "streak": streak,
        "active_days": active_days,
        "best_day": best_day,
        "commits": col["totalCommitContributions"],
        "prs": col["totalPullRequestContributions"],
        "issues": col["totalIssueContributions"],
    }


def anim(delay_s, props=""):
    if STATIC:
        return ""
    return f"animation-delay:{delay_s}s;{props}"


def reduced_motion_block():
    return """
    @media(prefers-reduced-motion:reduce){
      *{animation:none!important;opacity:1!important;transform:none!important}
      .fade-in,.slide-up,.grow-bar,.pop-in{opacity:1!important;transform:none!important}
    }"""


# ─── HERO CARD ───

def render_hero(contrib):
    w, h = 840, 220
    delay_base = 0.0

    name_lines = [
        ("Matheus", 0.1),
        ("Trajano", 0.3),
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    {load_font_css()}
    * {{ margin:0; padding:0 }}
    .bg {{ fill:{BG} }}
    .name {{ font-family:{font_stack()}; font-weight:800; font-size:52px; fill:{DARK} }}
    .sub {{ font-family:{font_stack()}; font-weight:400; font-size:16px; fill:{MUTED} }}
    .role {{ font-family:{font_stack()}; font-weight:500; font-size:18px; fill:{DARK2} }}
    .accent {{ fill:{BLUE} }}
    .dot {{ fill:{TILE_GREEN} }}

    .fade-in {{ opacity:0; animation: fadeIn 0.6s ease forwards }}
    .slide-up {{ opacity:0; transform:translateY(20px); animation: slideUp 0.6s ease forwards }}

    @keyframes fadeIn {{ to {{ opacity:1 }} }}
    @keyframes slideUp {{ to {{ opacity:1; transform:translateY(0) }} }}
    @keyframes shimmer {{
      0% {{ opacity:0.3 }}
      50% {{ opacity:1 }}
      100% {{ opacity:0.3 }}
    }}
    @keyframes shine {{
      0% {{ offset-distance:0% }}
      100% {{ offset-distance:100% }}
    }}
    {reduced_motion_block()}
  </style>
  <rect class="bg" width="{w}" height="{h}" rx="12"/>
  <line x1="40" y1="{h-1}" x2="{w-40}" y2="{h-1}" stroke="{LINE}" stroke-width="1"/>

  <!-- Name -->
  <text class="name fade-in" x="40" y="72" style="{anim(0.1)}">Matheus</text>
  <text class="name accent fade-in" x="40" y="130" style="{anim(0.3)}">Trajano</text>

  <!-- Blue shine on last name -->
  <defs>
    <linearGradient id="shine-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.6"/>
      <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="name-clip">
      <text x="40" y="130" style="font-family:{font_stack()};font-weight:800;font-size:52px">Trajano</text>
    </clipPath>
  </defs>
  {"" if STATIC else f'''<rect x="-100" y="100" width="100" height="40" fill="url(#shine-grad)" clip-path="url(#name-clip)">
    <animate attributeName="x" from="-100" to="{w}" dur="3s" begin="2s" repeatCount="indefinite"/>
  </rect>'''}

  <!-- Role -->
  <text class="role slide-up" x="40" y="165" style="{anim(0.5)}">Founder &amp; Developer at <tspan fill="{BLUE}">Zeety.ia</tspan></text>
  <circle class="dot" cx="40" cy="190" r="4" style="{'animation:shimmer 2s ease infinite;animation-delay:1s' if not STATIC else ''}"/>
  <text class="sub slide-up" x="52" y="195" style="{anim(0.6)}">Building CRMs and AI Agents to scale businesses</text>
</svg>"""
    (CARDS / "hero.svg").write_text(svg)


# ─── TILE CARDS ───

def render_tile(name, number, label, color, icon_path, link, delay_base, filename):
    w, h = 268, 160

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    {load_font_css()}
    .bg {{ fill:{BG}; stroke:{LINE}; stroke-width:1 }}
    .num {{ font-family:{font_stack()}; font-weight:800; font-size:42px; fill:{color} }}
    .label {{ font-family:{font_stack()}; font-weight:600; font-size:14px; fill:{DARK}; text-transform:uppercase; letter-spacing:1.5px }}
    .sub {{ font-family:{font_stack()}; font-weight:400; font-size:13px; fill:{MUTED} }}
    .arrow {{ fill:none; stroke:{color}; stroke-width:2; stroke-linecap:round }}

    .pop-in {{ opacity:0; transform:translateY(30px) rotate(-3deg); animation:popIn 0.7s cubic-bezier(0.34,1.56,0.64,1) forwards }}
    .count-up {{ font-family:{font_stack()}; font-weight:800; font-size:42px; fill:{color} }}

    @keyframes popIn {{ to {{ opacity:1; transform:translateY(0) rotate(0deg) }} }}
    @keyframes ringPulse {{
      0% {{ r:8; opacity:0.6 }}
      100% {{ r:24; opacity:0 }}
    }}
    @keyframes nudge {{
      0%,100% {{ transform:translateX(0) }}
      50% {{ transform:translateX(4px) }}
    }}
    {reduced_motion_block()}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12"/>

  <g class="pop-in" style="{anim(delay_base)}">
    <!-- Ring pulse -->
    {"" if STATIC else f'<circle cx="{w-30}" cy="30" fill="none" stroke="{color}" stroke-width="1.5"><animate attributeName="r" from="8" to="24" dur="2s" begin="{delay_base+0.8}s" repeatCount="indefinite"/><animate attributeName="opacity" from="0.6" to="0" dur="2s" begin="{delay_base+0.8}s" repeatCount="indefinite"/></circle>'}
    <circle cx="{w-30}" cy="30" r="6" fill="{color}" opacity="0.15"/>

    <!-- Label -->
    <text class="label" x="24" y="36">{name}</text>

    <!-- Number with count-up -->
    <text class="num" x="24" y="90">{number}</text>

    <!-- Subtitle -->
    <text class="sub" x="24" y="115">{label}</text>

    <!-- Arrow -->
    <g style="{'animation:nudge 2s ease infinite;animation-delay:'+str(delay_base+1)+'s' if not STATIC else ''}">
      <line class="arrow" x1="24" y1="140" x2="44" y2="140"/>
      <polyline class="arrow" points="38,134 44,140 38,146"/>
    </g>
  </g>
</svg>"""
    (CARDS / filename).write_text(svg)


# ─── ACTIVITY CHART ───

def render_activity(contrib):
    monthly = contrib["monthly"]
    months = list(monthly.items())
    # Skip months with 0 contributions at the start
    while months and months[0][1] == 0:
        months.pop(0)

    if not months:
        return

    w = 840
    bar_area_h = 140
    h = 260
    max_val = max(v for _, v in months)
    bar_w = min(40, (w - 80) // len(months) - 8)
    gap = (w - 80 - bar_w * len(months)) / max(len(months) - 1, 1)

    bars_svg = ""
    labels_svg = ""
    best_month = max(months, key=lambda x: x[1])

    for i, (m, v) in enumerate(months):
        x = 40 + i * (bar_w + gap)
        bar_h = (v / max_val) * bar_area_h if max_val > 0 else 0
        y = 40 + bar_area_h - bar_h
        is_best = m == best_month[0]
        color = BLUE if is_best else SURFACE
        text_color = BLUE if is_best else MUTED
        delay = 0.8 + i * 0.06

        month_label = datetime.strptime(m, "%Y-%m").strftime("%b")

        if STATIC:
            bars_svg += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{color}"/>'
        else:
            bars_svg += f'<rect x="{x}" y="{40 + bar_area_h}" width="{bar_w}" height="0" rx="4" fill="{color}"><animate attributeName="height" from="0" to="{bar_h}" dur="0.5s" begin="{delay}s" fill="freeze"/><animate attributeName="y" from="{40 + bar_area_h}" to="{y}" dur="0.5s" begin="{delay}s" fill="freeze"/></rect>'

        labels_svg += f'<text x="{x + bar_w/2}" y="{40 + bar_area_h + 20}" text-anchor="middle" style="font-family:{font_stack()};font-size:11px;fill:{text_color}">{month_label}</text>'

        if is_best:
            num_y = y - 8
            if STATIC:
                bars_svg += f'<text x="{x + bar_w/2}" y="{num_y}" text-anchor="middle" style="font-family:{font_stack()};font-weight:700;font-size:14px;fill:{BLUE}">{v}</text>'
            else:
                bars_svg += f'<text x="{x + bar_w/2}" y="{num_y}" text-anchor="middle" style="font-family:{font_stack()};font-weight:700;font-size:14px;fill:{BLUE};opacity:0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay+0.5}s" fill="freeze"/>{v}</text>'

    stats_y = 40 + bar_area_h + 50
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    {load_font_css()}
    .bg {{ fill:{BG} }}
    .title {{ font-family:{font_stack()}; font-weight:700; font-size:13px; fill:{DARK}; text-transform:uppercase; letter-spacing:1.5px }}
    .stat-num {{ font-family:{font_stack()}; font-weight:800; font-size:20px; fill:{DARK} }}
    .stat-label {{ font-family:{font_stack()}; font-weight:400; font-size:12px; fill:{MUTED} }}
    .fade-in {{ opacity:0; animation:fadeIn 0.5s ease forwards }}
    @keyframes fadeIn {{ to {{ opacity:1 }} }}
    {reduced_motion_block()}
  </style>
  <rect class="bg" width="{w}" height="{h}" rx="12"/>
  <line x1="40" y1="{h-1}" x2="{w-40}" y2="{h-1}" stroke="{LINE}" stroke-width="1"/>

  <text class="title fade-in" x="40" y="28" style="{anim(0.6)}">Contributions · Last 12 Months</text>

  {bars_svg}
  {labels_svg}

  <!-- Stats row -->
  <g class="fade-in" style="{anim(1.6)}">
    <text class="stat-num" x="40" y="{stats_y}">{contrib['total']}</text>
    <text class="stat-label" x="40" y="{stats_y+18}">total</text>

    <text class="stat-num" x="180" y="{stats_y}">{contrib['streak']}</text>
    <text class="stat-label" x="180" y="{stats_y+18}">best streak</text>

    <text class="stat-num" x="320" y="{stats_y}">{contrib['active_days']}</text>
    <text class="stat-label" x="320" y="{stats_y+18}">active days</text>

    <text class="stat-num" x="480" y="{stats_y}" fill="{BLUE}">{contrib['best_day'][1]}</text>
    <text class="stat-label" x="480" y="{stats_y+18}">busiest day</text>
  </g>
</svg>"""
    (CARDS / "activity.svg").write_text(svg)


# ─── CONTRIBUTION GRAPH ───

def render_graph(contrib):
    weeks = contrib["weeks"]
    cell = 11
    gap = 2
    cols = len(weeks)
    w = cols * (cell + gap) + 60
    h = 7 * (cell + gap) + 60

    max_c = max(
        d["contributionCount"]
        for wk in weeks
        for d in wk["contributionDays"]
    )

    def color_for(c):
        if c == 0:
            return SURFACE
        ratio = c / max_c if max_c > 0 else 0
        if ratio < 0.25:
            return "#b6d8ff"
        if ratio < 0.5:
            return "#6bb3ff"
        if ratio < 0.75:
            return "#2b93ff"
        return BLUE

    cells = ""
    for wi, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day = d["weekday"]
            c = d["contributionCount"]
            x = 40 + wi * (cell + gap)
            y = 20 + day * (cell + gap)
            col = color_for(c)
            delay = 1.8 + wi * 0.01

            if STATIC:
                cells += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{col}"/>'
            else:
                cells += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{col}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.15s" begin="{delay}s" fill="freeze"/></rect>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    {load_font_css()}
    .bg {{ fill:{BG} }}
    .label {{ font-family:{font_stack()}; font-size:10px; fill:{MUTED} }}
    {reduced_motion_block()}
  </style>
  <rect class="bg" width="{w}" height="{h}" rx="12"/>
  {cells}

  <!-- Day labels -->
  <text class="label" x="20" y="{20 + 1*(cell+gap) + 9}" text-anchor="end">M</text>
  <text class="label" x="20" y="{20 + 3*(cell+gap) + 9}" text-anchor="end">W</text>
  <text class="label" x="20" y="{20 + 5*(cell+gap) + 9}" text-anchor="end">F</text>
</svg>"""
    (CARDS / "graph.svg").write_text(svg)


# ─── STACK CARD ───

def render_stack():
    w, h = 840, 120
    techs = [
        ("React", BLUE),
        ("TypeScript", "#3178c6"),
        ("Python", "#3572A5"),
        ("Node.js", "#339933"),
        ("React Native", "#61dafb"),
        ("PostgreSQL", "#336791"),
        ("Supabase", "#3ecf8e"),
        ("Docker", "#2496ed"),
    ]

    pills = ""
    x = 40
    for i, (name, color) in enumerate(techs):
        pw = len(name) * 8.5 + 24
        delay = 2.2 + i * 0.08
        if STATIC:
            pills += f'''<g>
        <rect x="{x}" y="50" width="{pw}" height="32" rx="16" fill="{color}" opacity="0.08"/>
        <circle cx="{x+14}" cy="66" r="4" fill="{color}"/>
        <text x="{x+24}" y="71" style="font-family:{font_stack()};font-weight:500;font-size:13px;fill:{DARK}">{name}</text>
      </g>'''
        else:
            pills += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay}s" fill="freeze"/>
        <rect x="{x}" y="50" width="{pw}" height="32" rx="16" fill="{color}" opacity="0.08"/>
        <circle cx="{x+14}" cy="66" r="4" fill="{color}"/>
        <text x="{x+24}" y="71" style="font-family:{font_stack()};font-weight:500;font-size:13px;fill:{DARK}">{name}</text>
      </g>'''
        x += pw + 10

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <style>
    {load_font_css()}
    .bg {{ fill:{BG} }}
    .title {{ font-family:{font_stack()}; font-weight:700; font-size:13px; fill:{DARK}; text-transform:uppercase; letter-spacing:1.5px }}
    .fade-in {{ opacity:0; animation:fadeIn 0.5s ease forwards }}
    @keyframes fadeIn {{ to {{ opacity:1 }} }}
    {reduced_motion_block()}
  </style>
  <rect class="bg" width="{w}" height="{h}" rx="12"/>
  <text class="title fade-in" x="40" y="30" style="{anim(2.0)}">Stack</text>
  {pills}
</svg>"""
    (CARDS / "stack.svg").write_text(svg)


def main():
    contrib = load_contributions()
    print(f"Total contributions: {contrib['total']}")
    print(f"Streak: {contrib['streak']}, Active days: {contrib['active_days']}")
    print(f"Best day: {contrib['best_day']}")

    render_hero(contrib)
    print("✓ hero.svg")

    render_tile("AI AGENTS", contrib["commits"], "commits this year", TILE_BLUE, "", "https://zeety.com.br", 0.8, "tile-agents.svg")
    render_tile("CRM", contrib["prs"], "pull requests", TILE_GREEN, "", "https://zeety.com.br", 1.0, "tile-crm.svg")
    render_tile("AUTOMATION", contrib["active_days"], "active days", TILE_PURPLE, "", "https://zeety.com.br", 1.2, "tile-auto.svg")
    print("✓ tiles")

    render_activity(contrib)
    print("✓ activity.svg")

    render_graph(contrib)
    print("✓ graph.svg")

    render_stack()
    print("✓ stack.svg")

    print("\nAll cards rendered to cards/")


if __name__ == "__main__":
    main()
