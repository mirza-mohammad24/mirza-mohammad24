import base64
import math
import numpy as np
from PIL import Image

def load_font_data_uri(font_path="fonts/ramp.woff2"):
    """
    Reads the pre-subsetted JetBrains Mono woff2 (just the ~64 characters the
    ramp actually uses -- see fonts/README or the subsetting command) and
    returns it as a base64 data URI for embedding directly in the SVG.

    Why this matters: an <img>-loaded SVG can't fetch external resources
    (including fonts), so "JetBrains Mono" in the font-family list silently
    falls back to whatever monospace font the visitor's OS provides. Most
    Linux/Mac defaults (Liberation Mono, DejaVu Sans Mono, Noto Sans Mono)
    happen to share JetBrains Mono's 0.600em advance width, so the grid still
    lines up by coincidence. Windows commonly falls back to Consolas at
    ~0.55em, which renders the whole portrait about 7% narrower than the
    char_w/char_h grid assumes -- rows drift out of alignment with columns.
    Embedding the real font removes the guesswork entirely.

    Returns None (with a warning) if the font file is missing, so the script
    still runs and falls back to system fonts rather than crashing.
    """
    try:
        with open(font_path, "rb") as f:
            font_bytes = f.read()
    except FileNotFoundError:
        print(f"Warning: {font_path} not found -- falling back to system monospace fonts. "
              f"Run the subsetting command in the README to generate it.")
        return None

    b64 = base64.b64encode(font_bytes).decode("ascii")
    return f"data:font/woff2;base64,{b64}"

def generate_terminal_block(image_path="data/photo.png", output_path="avi-ascii.svg",
                             font_path="fonts/ramp.woff2"):
    try:
        img = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print(f"Error: Could not find {image_path}. Make sure your original photo is here.")
        return

    cols = 100
    W, H = img.size

    w_ratio = cols / W
    rows = int((H * w_ratio) * 0.48)

    img = img.resize((cols, rows), Image.Resampling.LANCZOS)

    pixels = np.array(img)

    RAMP = ".`',-~:;!>+=i?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

    char_w = 7.74
    char_h = 15.6

    svg_width = math.ceil(cols * char_w)
    svg_height = math.ceil(rows * char_h)

    ascii_grid = []
    for y in range(rows):
        row_str = ""
        for x in range(cols):
            luminance = int(pixels[y, x])

            ramp_index = math.floor((luminance / 255) * (len(RAMP) - 1))
            ramp_index = max(0, min(ramp_index, len(RAMP) - 1))
            row_str += RAMP[ramp_index]

        ascii_grid.append(row_str)

    font_data_uri = load_font_data_uri(font_path)
    font_face_rule = ""
    if font_data_uri:
        font_face_rule = f'''
        @font-face {{
            font-family: "JetBrains Mono Ramp";
            src: url("{font_data_uri}") format("woff2");
            font-weight: 400;
            font-style: normal;
        }}'''
    # If the embedded font loaded, use it first (guaranteed 0.600em advance,
    # matches char_w exactly on every OS/browser). Otherwise fall back to
    # system fonts as before -- portrait still renders, just at the mercy of
    # whatever monospace the visitor's OS provides.
    font_family = ('"JetBrains Mono Ramp", "JetBrains Mono", "Courier New", monospace'
                   if font_data_uri else '"JetBrains Mono", "Courier New", monospace')

    # Hardcoded permanent GitHub dark-mode terminal block styling
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
    <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
    <style>{font_face_rule}
        .ascii {{
            font-family: {font_family};
            font-size: 12.9px;
            fill: #e6edf3;
            white-space: pre;
        }}
        .cursor {{
            fill: #e6edf3;
        }}
    </style>
    '''

    for i, row in enumerate(ascii_grid):
        row_escaped = row.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        y_pos = (i + 1) * char_h
        begin_time = i * 0.09

        clip_id = f"clip-{i}"

        svg_content += f'''
    <clipPath id="{clip_id}">
        <rect x="0" y="{y_pos - char_h}" width="0" height="{char_h + 2}">
            <animate attributeName="width" from="0" to="{svg_width}" begin="{begin_time}s" dur="0.5s" fill="freeze" />
        </rect>
    </clipPath>
    <text class="ascii" x="0" y="{y_pos}" clip-path="url(#{clip_id})">{row_escaped}</text>
    <rect class="cursor" x="0" y="{y_pos - char_h + 3}" width="{char_w}" height="{char_h - 4}" opacity="0">
        <animate attributeName="x" from="0" to="{svg_width}" begin="{begin_time}s" dur="0.5s" fill="freeze" />
        <animate attributeName="opacity" values="1;0" keyTimes="0;1" begin="{begin_time}s" dur="0.6s" fill="freeze" />
    </rect>
    '''

    svg_content += '</svg>'

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Success! Generated single dark terminal block at {output_path}")

if __name__ == "__main__":
    generate_terminal_block()