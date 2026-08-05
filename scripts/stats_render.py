from stats_common import svg_wrap, esc, fmt_date
import datetime as dt

def render_hero(total, active_days, best_week, weekly_totals, font_css, fam_reg, fam_bold, theme):
    width, height = 700, 200
    pad = 24
    chart_top = 100
    chart_h = 70
    chart_w = width - 2 * pad

    body = f'''
    <text x="{pad}" y="56" font-family='{fam_bold}' font-size="42" fill="{theme['fg']}">{total:,}</text>
    <text x="{pad}" y="76" font-family='{fam_reg}' font-size="13" fill="{theme['muted']}">contributions in the last year</text>
    
    <text x="{width - pad}" y="42" font-family='{fam_bold}' font-size="22" fill="{theme['fg']}" text-anchor="end">{active_days}</text>
    <text x="{width - pad}" y="58" font-family='{fam_reg}' font-size="13" fill="{theme['muted']}" text-anchor="end">active days</text>
    
    <text x="{width - pad}" y="86" font-family='{fam_bold}' font-size="22" fill="{theme['fg']}" text-anchor="end">{best_week}</text>
    <text x="{width - pad}" y="102" font-family='{fam_reg}' font-size="13" fill="{theme['muted']}" text-anchor="end">best week</text>
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
    <polyline points="{area}" fill="{theme['accent']}" fill-opacity="0.12" stroke="none"/>
    <polyline points="{line}" fill="none" stroke="{theme['accent']}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="{theme['bg']}" stroke="{theme['accent']}" stroke-width="2"/>
'''
    return svg_wrap(width, height, body, font_css, theme)

def render_streak(current, current_range, longest, longest_range, font_css, fam_reg, fam_bold, theme):
    width, height = 700, 130
    col_w = width / 2

    def block(x, label, days, date_range):
        range_str = ""
        if date_range:
            range_str = f'''
    <text x="{x}" y="98" font-family='{fam_reg}' font-size="12" fill="{theme['muted']}">{esc(date_range)}</text>'''
        return f'''
    <text x="{x}" y="56" font-family='{fam_bold}' font-size="42" fill="{theme['fg']}">{days}</text>
    <text x="{x}" y="76" font-family='{fam_reg}' font-size="13" fill="{theme['muted']}">{esc(label)}</text>{range_str}'''

    body = block(24, "current streak", current, current_range)
    body += block(col_w + 24, "longest streak", longest, longest_range)
    body += f'\n    <line x1="{col_w}" y1="20" x2="{col_w}" y2="{height - 20}" stroke="{theme["rule"]}" stroke-width="1"/>'
    return svg_wrap(width, height, body, font_css, theme)


def render_langs(langs, font_css, fam_reg, fam_bold, theme):
    width = 700
    row_h = 28
    pad = 24
    top = 55
    height = top + len(langs) * row_h + 20
    
    col1_x = pad
    bar1_x = col1_x + 95
    bar1_w = 150
    
    col2_x = 350
    bar2_x = col2_x + 95
    bar2_w = 150
    bar_h = 8

    body = f'''
    <text x="{col1_x}" y="30" font-family='{fam_reg}' font-size="11" fill="{theme['muted']}" text-transform="uppercase">BY BYTES</text>
    <text x="{col2_x}" y="30" font-family='{fam_reg}' font-size="11" fill="{theme['muted']}" text-transform="uppercase">BY REPOS</text>
'''

    langs_by_bytes = langs 
    langs_by_repos = sorted(langs, key=lambda x: x["repo_count"], reverse=True)

    for i, lang in enumerate(langs_by_bytes):
        y = top + i * row_h
        color = lang.get("color") or theme['muted']
        fill_w = max(2, bar1_w * (lang["pct"] / 100.0))
        body += f'''
    <text x="{col1_x}" y="{y}" font-family='{fam_reg}' font-size="13" fill="{theme['fg']}">{esc(lang["name"].lower())}</text>
    <rect x="{bar1_x}" y="{y - 12}" width="{bar1_w}" height="{bar_h}" rx="4" fill="{theme['rule']}"/>
    <rect x="{bar1_x}" y="{y - 12}" width="{fill_w:.1f}" height="{bar_h}" rx="4" fill="{color}"/>
    <text x="{bar1_x + bar1_w + 12}" y="{y}" font-family='{fam_reg}' font-size="12" fill="{theme['muted']}">{lang["pct"]:.0f}%</text>'''

    max_repos = langs_by_repos[0]["repo_count"] if langs_by_repos else 1
    for i, lang in enumerate(langs_by_repos):
        y = top + i * row_h
        color = lang.get("color") or theme['muted']
        fill_w = max(2, bar2_w * (lang["repo_count"] / max_repos))
        body += f'''
    <text x="{col2_x}" y="{y}" font-family='{fam_reg}' font-size="13" fill="{theme['fg']}">{esc(lang["name"].lower())}</text>
    <rect x="{bar2_x}" y="{y - 12}" width="{bar2_w}" height="{bar_h}" rx="4" fill="{theme['rule']}"/>
    <rect x="{bar2_x}" y="{y - 12}" width="{fill_w:.1f}" height="{bar_h}" rx="4" fill="{color}"/>
    <text x="{bar2_x + bar2_w + 12}" y="{y}" font-family='{fam_reg}' font-size="12" fill="{theme['muted']}">{lang["repo_count"]}</text>'''

    return svg_wrap(width, height, body, font_css, theme)

def render_heatmap(weeks, font_css, fam_reg, fam_bold, theme):
    width, height = 820, 150
    pad_x, pad_y = 24, 30
    box_size, gap = 11, 4

    body = f'''
    <style>
        @keyframes dropIn {{
            0% {{ opacity: 0; transform: translateY(-4px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        .day {{
            opacity: 0;
            animation: dropIn 0.35s ease-out forwards;
        }}
    </style>
'''

    last_month = -1
    for w_idx, week in enumerate(weeks):
        x = pad_x + w_idx * (box_size + gap)
        
        # Determine when to print the month label at the top
        if week["contributionDays"]:
            first_day = dt.date.fromisoformat(week["contributionDays"][0]["date"])
            if first_day.month != last_month:
                body += f'<text x="{x}" y="{pad_y - 8}" font-family="{fam_reg}" font-size="10" fill="{theme["muted"]}">{first_day.strftime("%b")}</text>\n'
                last_month = first_day.month

        for day in week["contributionDays"]:
            # Calculate row alignment (0 = Sunday, 6 = Saturday)
            d_obj = dt.date.fromisoformat(day["date"])
            weekday = (d_obj.weekday() + 1) % 7 
            y = pad_y + weekday * (box_size + gap)
            
            count = day["contributionCount"]
            if count == 0: level = 0
            elif count < 3: level = 1
            elif count < 6: level = 2
            elif count < 10: level = 3
            else: level = 4

            color = theme["heatmap"][level]
            
            # The math that creates the diagonal sweeping animation
            delay = (w_idx * 0.02) + (weekday * 0.02)
            
            body += f'<rect class="day" x="{x}" y="{y}" width="{box_size}" height="{box_size}" rx="2" fill="{color}" style="animation-delay: {delay:.2f}s" />\n'

    return svg_wrap(width, height, body, font_css, theme)