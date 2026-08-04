import base64
import re
import sys

# Approximate per-character advance widths for JetBrains Mono at 1 unit of
# font-size, used only to figure out where to start the hairline rule.
# JetBrains Mono is a true monospace, so every character (that exists in the
# subset) is exactly 0.6 em wide -- no per-glyph lookup needed.
CHAR_ADVANCE_EM = 0.6

def load_font_data_uri(font_path):
    try:
        with open(font_path, "rb") as f:
            font_bytes = f.read()
    except FileNotFoundError:
        print(f"Warning: {font_path} not found -- heading will fall back to "
              f"system monospace fonts. Run the subsetting command in the "
              f"README to generate it.")
        return None
    b64 = base64.b64encode(font_bytes).decode("ascii")
    return f"data:font/woff2;base64,{b64}"

def slugify(text):
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")

def generate_heading_svg(text, out_path, theme, font_data_uri,
                          width=700, height=34, font_size=15,
                          left_pad=0, right_pad=2):
    """
    theme: dict with 'text_color' and 'rule_color'
    Produces a lowercase mono label on the left, with a hairline rule
    running from just past the text to the right edge -- same device as
    a terminal `man` page header or a CLI section divider.
    """
    label = text.lower()
    label_escaped = (label.replace('&', '&amp;')
                          .replace('<', '&lt;')
                          .replace('>', '&gt;'))

    # crude but accurate width estimate since the font is monospace at 0.6em
    text_width_px = len(label) * font_size * CHAR_ADVANCE_EM
    rule_start_x = left_pad + text_width_px + (font_size * 0.9)  # gap ~ 1 char
    rule_end_x = width - right_pad

    font_face_rule = ""
    font_family = '"JetBrains Mono", "Courier New", monospace'
    if font_data_uri:
        font_family = f'"JetBrains Mono Heading", {font_family}'
        font_face_rule = f'''
        @font-face {{
            font-family: "JetBrains Mono Heading";
            src: url("{font_data_uri}") format("woff2");
            font-weight: 400;
            font-style: normal;
        }}'''

    text_y = height / 2 + font_size * 0.32  # rough vertical centering for this font
    rule_y = height / 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{label_escaped}">
    <style>{font_face_rule}
        .heading {{
            font-family: {font_family};
            font-size: {font_size}px;
            fill: {theme['text_color']};
            white-space: pre;
        }}
    </style>
    <text class="heading" x="{left_pad}" y="{text_y}">{label_escaped}</text>'''

    if rule_start_x < rule_end_x:
        svg += f'''
    <line x1="{rule_start_x:.1f}" y1="{rule_y}" x2="{rule_end_x}" y2="{rule_y}" stroke="{theme['rule_color']}" stroke-width="1"/>'''

    svg += "\n</svg>"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)


def generate_heading(text, output_dir="headings", font_path="fonts/headings.woff2", width=700):
    """
    Generates a dark and light variant for one heading and prints the
    <picture> markdown/HTML snippet to embed it, respecting the viewer's
    GitHub color scheme.
    """
    slug = slugify(text)
    font_data_uri = load_font_data_uri(font_path)

    themes = {
        "dark":  {"text_color": "#e6edf3", "rule_color": "#30363d"},
        "light": {"text_color": "#24292f", "rule_color": "#d0d7de"},
    }

    import os
    os.makedirs(output_dir, exist_ok=True)

    paths = {}
    for name, theme in themes.items():
        out_path = f"{output_dir}/{slug}-{name}.svg"
        generate_heading_svg(text, out_path, theme, font_data_uri, width=width)
        paths[name] = out_path

    snippet = (
        '<picture>\n'
        f'  <source media="(prefers-color-scheme: dark)" srcset="{paths["dark"]}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{paths["light"]}">\n'
        f'  <img alt="{text.lower()}" src="{paths["light"]}">\n'
        '</picture>'
    )

    print(f"Generated {paths['dark']} and {paths['light']}")
    print("\nEmbed with:\n")
    print(snippet)
    return paths, snippet


if __name__ == "__main__":
    # Usage: python3 generate_heading.py "section title" [width]
    if len(sys.argv) < 2:
        print('Usage: python3 generate_heading.py "section title" [width]')
        sys.exit(1)
    text = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 700
    generate_heading(text, width=width)