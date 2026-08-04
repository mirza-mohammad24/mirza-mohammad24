"""
Renders the three Part 2 SVGs: hero total + weekly sparkline, streak, and
top languages. Columns for daily data would be honest; weekly sums are
aggregates, so a filled line is fine here (see README, "pick the right
chart type").
"""
from stats_common import svg_wrap, esc, fmt_date, FG, MUTED, RULE, ACCENT


def render_hero(total, weekly_totals, font_css, fam_reg, fam_bold):
    width, height = 700, 200
    pad = 24
    chart_top = 90
    chart_h = 70
    chart_w = width - 2 * pad

    body = f'''
    <text x="{pad}" y="56" font-family='{fam_bold}' font-size="42" fill="{FG}">{total:,}</text>
    <text x="{pad}" y="76" font-family='{fam_reg}' font-size="13" fill="{MUTED}">contributions in the last year</text>
'''

    n = len(weekly_totals)
    if n > 1:
        max_v = max(weekly_totals) or 1
        step = chart_w / (n - 1)

        def pt(i, v):
            x = pad + i * step
            y = chart_top + chart_h - (v / max_v) * chart_h
            return x, y

        pts = [pt(i, v) for i, v in enumerate(weekly_totals)]
        line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        area = f"{pad},{chart_top + chart_h} " + line + f" {pad + (n-1)*step:.1f},{chart_top + chart_h}"

        body += f'''
    <polyline points="{area}" fill="{ACCENT}" fill-opacity="0.12" stroke="none"/>
    <polyline points="{line}" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    <line x1="{pad}" y1="{chart_top + chart_h}" x2="{width - pad}" y2="{chart_top + chart_h}" stroke="{RULE}" stroke-width="1"/>
    <text x="{pad}" y="{chart_top + chart_h + 18}" font-family='{fam_reg}' font-size="11" fill="{MUTED}">52 weeks ago</text>
    <text x="{width - pad}" y="{chart_top + chart_h + 18}" font-family='{fam_reg}' font-size="11" fill="{MUTED}" text-anchor="end">this week</text>
'''
    return svg_wrap(width, height, body, font_css)


def render_streak(current, current_range, longest, longest_range,
                   font_css, fam_reg, fam_bold):
    width, height = 700, 130
    col_w = width / 2

    def block(x, label, days, date_range):
        range_str = ""
        if date_range:
            range_str = f'''
    <text x="{x}" y="98" font-family='{fam_reg}' font-size="12" fill="{MUTED}">{esc(date_range)}</text>'''
        return f'''
    <text x="{x}" y="56" font-family='{fam_bold}' font-size="42" fill="{FG}">{days}</text>
    <text x="{x}" y="76" font-family='{fam_reg}' font-size="13" fill="{MUTED}">{esc(label)}</text>{range_str}'''

    body = block(24, "day current streak", current, current_range)
    body += block(col_w + 24, "day longest streak", longest, longest_range)
    body += f'\n    <line x1="{col_w}" y1="20" x2="{col_w}" y2="{height - 20}" stroke="{RULE}" stroke-width="1"/>'
    return svg_wrap(width, height, body, font_css)


def render_langs(langs, font_css, fam_reg, fam_bold):
    """langs: list of dicts with name, color, pct, repo_count, sorted desc by bytes."""
    width = 700
    row_h = 28
    pad = 24
    top = 20
    height = top + len(langs) * row_h + 16
    bar_x = 200
    bar_w = width - bar_x - pad - 50
    bar_h = 8

    body = ""
    for i, lang in enumerate(langs):
        y = top + i * row_h
        color = lang.get("color") or MUTED
        fill_w = max(2, bar_w * (lang["pct"] / 100.0))
        body += f'''
    <circle cx="{pad + 4}" cy="{y - 4}" r="4" fill="{color}"/>
    <text x="{pad + 16}" y="{y}" font-family='{fam_reg}' font-size="13" fill="{FG}">{esc(lang["name"])}</text>
    <rect x="{bar_x}" y="{y - 12}" width="{bar_w}" height="{bar_h}" rx="4" fill="{RULE}"/>
    <rect x="{bar_x}" y="{y - 12}" width="{fill_w:.1f}" height="{bar_h}" rx="4" fill="{color}"/>
    <text x="{width - pad}" y="{y}" font-family='{fam_reg}' font-size="12" fill="{MUTED}" text-anchor="end">{lang["pct"]:.1f}%</text>'''

    return svg_wrap(width, height, body, font_css)