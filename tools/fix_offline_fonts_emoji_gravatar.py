"""Point inline font URLs to static/font, strip ?ver for file://, localize gravatar mm, strip emoji js query."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")

# Google-hosted Lato/Dancing fonts were saved under static/font during earlier clone.
FONT_PREFIX_OLD = (
    "static/remote/hot51.biz.id/wp-content/fonts/lato/",
    "static/remote/hot51.biz.id/wp-content/fonts/dancing-script/",
)
FONT_PREFIX_NEW = "static/font/"

ICONS_BASE = "static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/css/icons/"

GRAV_MM_LOCAL = "static/images/gravatar-mm-180.png"

GRAV_RE = re.compile(
    r"https://secure\.gravatar\.com/avatar/[0-9a-f]+\?[^\"'\s>]*",
    re.IGNORECASE,
)

EMOJI_JS_RE = re.compile(
    r"static/remote/hot51\.biz\.id/wp-includes/js/wp-emoji-release\.min\.js\?ver=[0-9.]+",
    re.IGNORECASE,
)


def patch_text(text: str) -> tuple[str, int]:
    n = 0
    t = text
    for old in FONT_PREFIX_OLD:
        if old in t:
            c = t.count(old)
            t = t.replace(old, FONT_PREFIX_NEW)
            n += c

    # fl-icons: drop remote path + ?ver (file:// cannot resolve query on local files)
    pairs = [
        (
            ICONS_BASE + "fl-icons.eot?v=3.20.5",
            "static/font/fl-icons.eot",
        ),
        (
            ICONS_BASE + "fl-icons.eot#iefix?v=3.20.5",
            "static/font/fl-icons.eot?#iefix",
        ),
        (
            ICONS_BASE + "fl-icons.woff2?v=3.20.5",
            "static/font/fl-icons.woff2",
        ),
        (
            ICONS_BASE + "fl-icons.ttf?v=3.20.5",
            "static/font/fl-icons.ttf",
        ),
        (
            ICONS_BASE + "fl-icons.woff?v=3.20.5",
            "static/font/fl-icons.woff",
        ),
        (
            ICONS_BASE + "fl-icons.svg?v=3.20.5#fl-icons",
            "static/font/fl-icons.svg#fl-icons",
        ),
    ]
    for old, new in pairs:
        if old in t:
            c = t.count(old)
            t = t.replace(old, new)
            n += c

    # Emoji loader JSON + any loose script refs
    t2, ne = EMOJI_JS_RE.subn(
        "static/remote/hot51.biz.id/wp-includes/js/wp-emoji-release.min.js",
        t,
    )
    t = t2
    n += ne

    # Gravatar (default mm silhouette) -> local PNG
    t3, ng = GRAV_RE.subn(GRAV_MM_LOCAL, t)
    t = t3
    n += ng

    return t, n


def main() -> int:
    files = sorted(SITE.glob("*.html"))
    updated = ch = 0
    for f in files:
        old = f.read_text(encoding="utf-8", errors="ignore")
        new, n = patch_text(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            updated += 1
            ch += n
    print(f"html_files={len(files)} updated_files={updated} replacements={ch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
