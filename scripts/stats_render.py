from stats_common import svg_wrap, esc, fmt_date

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
    <polyline points="{area}" fill="{theme['fg']}" fill-opacity="0.1" stroke="none"/>
    <polyline points="{line}" fill="none" stroke="{theme['fg']}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="{theme['bg']}" stroke="{theme['fg']}" stroke-width="2"/>
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