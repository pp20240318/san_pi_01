from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")

# Word variants to replace in visible text.
REPLACEMENTS = {
    "HOT51": "Baby91",
    "Hot51": "Baby91",
    "hot51": "Baby91",
}

# Quick heuristic: if an attribute value looks like a path/url, don't change it.
PATHISH_RE = re.compile(r"(?:https?://|//|/|\\.|static/|wp-content/|wp-includes/)", re.IGNORECASE)

# Tags whose inner content should never be modified.
SKIP_BLOCK_RE = re.compile(r"(?is)<(script|style|noscript)\b.*?>.*?</\1\s*>")

# Replace only text between tags (roughly visible text).
BETWEEN_TAGS_RE = re.compile(r">(?!\s*<)([^<]+)<")

# Replace only in visible attributes.
VISIBLE_ATTR_RE = re.compile(r"""(?is)\b(title|alt|aria-label|placeholder)\s*=\s*(["'])(.*?)\2""")


def replace_words(s: str) -> tuple[str, int]:
    count = 0
    out = s
    for old, new in REPLACEMENTS.items():
        if old in out:
            c = out.count(old)
            out = out.replace(old, new)
            count += c
    return out, count


def process_html(content: str) -> tuple[str, int]:
    total = 0

    # 1) Mask script/style/noscript blocks.
    blocks: list[str] = []

    def mask(m: re.Match[str]) -> str:
        blocks.append(m.group(0))
        return f"__SKIP_BLOCK_{len(blocks) - 1}__"

    masked = SKIP_BLOCK_RE.sub(mask, content)

    # 2) Replace visible attributes (but not path-ish values).
    def sub_attr(m: re.Match[str]) -> str:
        nonlocal total
        name = m.group(1)
        quote = m.group(2)
        val = m.group(3)
        if PATHISH_RE.search(val):
            return m.group(0)
        new_val, c = replace_words(val)
        total += c
        return f'{name}={quote}{new_val}{quote}'

    masked2 = VISIBLE_ATTR_RE.sub(sub_attr, masked)

    # 3) Replace text between tags.
    def sub_text(m: re.Match[str]) -> str:
        nonlocal total
        text = m.group(1)
        new_text, c = replace_words(text)
        total += c
        return f">{new_text}<"

    masked3 = BETWEEN_TAGS_RE.sub(sub_text, masked2)

    # 4) Unmask blocks.
    out = masked3
    for idx, block in enumerate(blocks):
        out = out.replace(f"__SKIP_BLOCK_{idx}__", block)

    return out, total


def main() -> None:
    html_files = list(ROOT.glob("*.html"))
    changed_files = 0
    replaced_total = 0

    for f in html_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        new_content, c = process_html(content)
        if c and new_content != content:
            f.write_text(new_content, encoding="utf-8")
            changed_files += 1
            replaced_total += c

    print(f"changed_files={changed_files} replaced_occurrences={replaced_total} scanned_files={len(html_files)}")


if __name__ == "__main__":
    main()

