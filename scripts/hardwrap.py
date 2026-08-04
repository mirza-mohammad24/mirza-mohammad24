import sys
import textwrap

LINE_LENGTH = 76  

def hardwrap_paragraph(text, width=LINE_LENGTH):
    text = " ".join(text.split())  # collapse existing whitespace/newlines
    lines = textwrap.wrap(text, width=width, break_long_words=False)
    return "<br>\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # wrap a file's contents
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        # wrap stdin, e.g.: echo "some long paragraph..." | python3 hardwrap.py
        text = sys.stdin.read()

    print(hardwrap_paragraph(text))