"""Point remote WordPress GA bootstrap URLs to local noop; strip direct gtag/js links."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
NOOP = "static/js/gtag-offline.js"

# WP serves hashed GA under /?local_ga_js=HEX
LOCAL_GA = re.compile(
    r'src=(["\'])https?://hot51\.biz\.id/\?local_ga_js=[a-f0-9]+\1',
    re.IGNORECASE,
)

GTM_GTAG = re.compile(
    r'src=(["\'])https?://www\.googletagmanager\.com/gtag/js[^"\']*\1',
    re.IGNORECASE,
)


def patch(text: str) -> tuple[str, int]:
    n = 0
    t, n1 = LOCAL_GA.subn(lambda m: f'src={m.group(1)}{NOOP}{m.group(1)}', text)
    n += n1
    t2, n2 = GTM_GTAG.subn(lambda m: f'src={m.group(1)}{NOOP}{m.group(1)}', t)
    n += n2
    return t2, n


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
