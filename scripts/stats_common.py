"""
Shared helpers for the three Part 2 data graphics (stats.svg, streak.svg,
langs.svg). Deliberately duplicated font embedding per file -- see the
project README -- so this module only has render helpers, no state that
would need to survive between files.
"""
import base64
import datetime as dt

# Same visual language as avi-ascii.svg and the heading SVGs: GitHub's
# dark terminal palette. Stats stay dark-only (see README) to match the
# portrait, which hardcodes its own #0d1117 background rect regardless of
# viewer theme -- switching stats to light would look broken sitting next
# to a forced-dark portrait.
BG = "#0d1117"
FG = "#e6edf3"
MUTED = "#7d8590"
RULE = "#30363d"
ACCENT = "#39d353"  # GitHub's contribution-graph green


def load_font_data_uri(font_path):
    try:
        with open(font_path, "rb") as f:
            font_bytes = f.read()
    except FileNotFoundError:
        print(f"Warning: {font_path} not found -- falling back to system "
              f"monospace fonts. Run the subsetting commands in the README.")
        return None
    b64 = base64.b64encode(font_bytes).decode("ascii")
    return f"data:font/woff2;base64,{b64}"


def font_face_block(regular_path="fonts/data-regular.woff2",
                     bold_path="fonts/data-bold.woff2"):
    """Returns (css_rules, family_regular, family_bold)."""
    reg_uri = load_font_data_uri(regular_path)
    bold_uri = load_font_data_uri(bold_path)

    rules = ""
    fam_reg = '"Courier New", monospace'
    fam_bold = '"Courier New", monospace'

    if reg_uri:
        fam_reg = f'"JBM Data", {fam_reg}'
        rules += f'''
        @font-face {{
            font-family: "JBM Data";
            src: url("{reg_uri}") format("woff2");
            font-weight: 400;
            font-style: normal;
        }}'''
    if bold_uri:
        fam_bold = f'"JBM Data Bold", {fam_bold}'
        rules += f'''
        @font-face {{
            font-family: "JBM Data Bold";
            src: url("{bold_uri}") format("woff2");
            font-weight: 700;
            font-style: normal;
        }}'''

    return rules, fam_reg, fam_bold


def esc(text):
    return (str(text).replace('&', '&amp;')
                      .replace('<', '&lt;')
                      .replace('>', '&gt;'))


def fmt_date(iso_date, with_year=True):
    d = dt.date.fromisoformat(iso_date)
    return d.strftime("%b %-d, %Y") if with_year else d.strftime("%b %-d")


def svg_wrap(width, height, body, font_css):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <rect width="100%" height="100%" fill="{BG}" rx="8"/>
    <style>{font_css}
        text {{ white-space: pre; }}
    </style>
{body}
</svg>'''