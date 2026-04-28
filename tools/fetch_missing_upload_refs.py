"""Scan HTML for localized upload paths; download any that are still missing (bounded)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

SITE_DIR = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
REMOTE_BASE = "https://hot51.biz.id/"
LOCAL_UPLOAD_RE = re.compile(
    r"static/remote/hot51\.biz\.id/wp-content/uploads/(?P<rel>[\w\-/%.]+?\.(?:png|jpe?g|webp|gif|svg|ico))",
    re.IGNORECASE,
)
REMOTE_UPLOAD_RE = re.compile(
    r"https?://hot51\.biz\.id/wp-content/uploads/(?P<rel>[\w\-/%.]+?\.(?:png|jpe?g|webp|gif|svg|ico))",
    re.IGNORECASE,
)


def fetch_bytes(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; fetch_missing_upload_refs.py)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    max_fetch = 800
    if len(sys.argv) > 1:
        max_fetch = int(sys.argv[1])

    prefix: str | None = None
    if len(sys.argv) > 2:
        prefix = sys.argv[2].strip().replace("\\", "/")
        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"

    refs: set[str] = set()
    for html in SITE_DIR.glob("*.html"):
        t = html.read_text(encoding="utf-8", errors="ignore")
        refs |= {m.group("rel") for m in LOCAL_UPLOAD_RE.finditer(t)}
        refs |= {m.group("rel") for m in REMOTE_UPLOAD_RE.finditer(t)}
    refs = {r.replace("%2F", "/") for r in refs}

    if prefix:
        refs = {r for r in refs if r.startswith(prefix)}

    missing: list[str] = []
    for rel in sorted(refs):
        p = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads" / rel
        if not p.exists() or p.stat().st_size == 0:
            missing.append(rel)

    print(
        f"refs={len(refs)} missing={len(missing)} will_fetch={min(len(missing), max_fetch)}"
        + (f" prefix={prefix!r}" if prefix else ""),
        flush=True,
    )
    ok = fail = 0
    for rel in missing[:max_fetch]:
        url = REMOTE_BASE + "wp-content/uploads/" + rel
        out = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads" / rel
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(fetch_bytes(url))
            ok += 1
            if ok % 50 == 0:
                print(f"  fetched {ok}...", flush=True)
        except Exception as e:
            fail += 1
            if fail <= 10:
                print(f"  FAIL {rel}: {e}", flush=True)
    print(f"done ok={ok} fail={fail}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
