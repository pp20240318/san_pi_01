from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
HOT_RE = re.compile(r"(HOT51|Hot51|hot51)")

# Rough URL-attribute detection; this is a sanity check only.
URL_ATTR_RE = re.compile(
    r"""\b(?:href|src|srcset|content|action|data-src|poster)\s*=\s*(["'])(?:(?!\1).)*(HOT51|Hot51|hot51)(?:(?!\1).)*\1""",
    re.IGNORECASE | re.DOTALL,
)


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def main() -> None:
    url_hits = []
    text_hits = []
    for f in ROOT.glob("*.html"):
        s = f.read_text(encoding="utf-8", errors="ignore")
        if URL_ATTR_RE.search(s):
            url_hits.append(f.name)
        if HOT_RE.search(strip_tags(s)):
            text_hits.append(f.name)

    print(f"files_with_hot51_in_url_attrs={len(url_hits)}")
    print(f"files_with_hot51_in_stripped_text={len(text_hits)}")
    for name in url_hits[:40]:
        print(f"url_attr_hit: {name}")
    for name in text_hits[:40]:
        print(f"text_hit: {name}")


if __name__ == "__main__":
    main()

