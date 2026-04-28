"""Map WordPress content-hashed wp-includes script URLs to stable static/js/ files (file:// safe)."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")

REPLACERS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"static/remote/hot51\.biz\.id/wp-includes/js/jquery/jquery\.min\.[a-f0-9]+\.js(?:\?[^\"\'\s>]*)?",
            re.IGNORECASE,
        ),
        "static/js/jquery.min.js",
    ),
    (
        re.compile(
            r"static/remote/hot51\.biz\.id/wp-includes/js/jquery/jquery-migrate\.min\.[a-f0-9]+\.js(?:\?[^\"\'\s>]*)?",
            re.IGNORECASE,
        ),
        "static/js/jquery-migrate.min.js",
    ),
    (
        re.compile(
            r"static/remote/hot51\.biz\.id/wp-includes/js/hoverIntent\.min\.[a-f0-9]+\.js(?:\?[^\"\'\s>]*)?",
            re.IGNORECASE,
        ),
        "static/js/hoverIntent.min.js",
    ),
]


def patch(text: str) -> tuple[str, int]:
    n = 0
    t = text
    for pat, rep in REPLACERS:
        t2, c = pat.subn(rep, t)
        t = t2
        n += c
    return t, n


def main() -> int:
    files = sorted(SITE.glob("*.html"))
    upd = ch = 0
    for f in files:
        old = f.read_text(encoding="utf-8", errors="ignore")
        new, n = patch(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            upd += 1
            ch += n
    print(f"files={len(files)} updated={upd} replacements={ch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
