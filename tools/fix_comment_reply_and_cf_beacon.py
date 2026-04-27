"""Offline fixes: comment-reply path for file://, remove Cloudflare RUM beacon."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")

# Full <script ... cloudflareinsights ...></script> (single line as saved from WP)
BEACON_SCRIPT = re.compile(
    r"<script[^>]*cloudflareinsights\.com/beacon\.min\.js[^>]*>\s*</script>\s*",
    re.IGNORECASE,
)

COMMENT_REPLY_SRC_DQ = re.compile(
    r'src="static/remote/hot51\.biz\.id/wp-includes/js/comment-reply\.min\.js(?:\?[^"]*)?"',
    re.IGNORECASE,
)
COMMENT_REPLY_SRC_SQ = re.compile(
    r"src='static/remote/hot51\.biz\.id/wp-includes/js/comment-reply\.min\.js(?:\?[^']*)?'",
    re.IGNORECASE,
)


def patch_html(text: str) -> tuple[str, int, int]:
    n_beacon = 0
    n_reply = 0
    t, n_beacon = BEACON_SCRIPT.subn("", text)
    t2, n1 = COMMENT_REPLY_SRC_DQ.subn('src="static/js/comment-reply.min.js"', t)
    n_reply += n1
    t3, n2 = COMMENT_REPLY_SRC_SQ.subn("src='static/js/comment-reply.min.js'", t2)
    n_reply += n2
    return t3, n_beacon, n_reply


def main() -> int:
    files = sorted(SITE.glob("*.html"))
    total_beacon = total_reply = updated = 0
    for f in files:
        old = f.read_text(encoding="utf-8", errors="ignore")
        new, nb, nr = patch_html(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            updated += 1
            total_beacon += nb
            total_reply += nr
    print(f"html_files={len(files)} updated_files={updated} beacons_removed={total_beacon} comment_reply_fixed={total_reply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
