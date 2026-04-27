from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


SITE_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")
UPLOADS_DIR = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads"

LOCAL_UPLOAD_RE = re.compile(
    r"static/remote/hot51\.biz\.id/wp-content/uploads/(?P<rel>[\w\-/%.]+?\.(?:png|jpe?g|webp|gif|svg|ico))",
    re.IGNORECASE,
)


def fetch_bytes(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; retry_missing_uploads.py)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def exists(rel: str) -> bool:
    p = UPLOADS_DIR / rel
    return p.exists() and p.stat().st_size > 0


def download(rel: str) -> None:
    # URL-encode but keep slashes
    rel_q = quote(rel, safe="/-_.")
    url = f"https://hot51.biz.id/wp-content/uploads/{rel_q}"
    out = UPLOADS_DIR / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(fetch_bytes(url))


def main() -> int:
    prefix = None
    import sys
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        prefix = sys.argv[1].strip().replace("\\", "/").lstrip("/")

    refs: set[str] = set()
    for html in SITE_DIR.glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        refs |= {m.group("rel") for m in LOCAL_UPLOAD_RE.finditer(text)}

    if prefix:
        refs = {r for r in refs if r.startswith(prefix)}

    missing = [r for r in sorted(refs) if not exists(r)]
    print(f"refs={len(refs)} missing={len(missing)}", flush=True)

    downloaded = 0
    failed: list[str] = []
    for i, rel in enumerate(missing, start=1):
        ok = False
        for attempt in range(1, 4):
            try:
                download(rel)
                downloaded += 1
                ok = True
                break
            except Exception:
                time.sleep(0.5 * attempt)
        if not ok:
            failed.append(rel)

        if i % 100 == 0:
            print(f"progress {i}/{len(missing)} downloaded={downloaded} failed={len(failed)}", flush=True)

    print(f"done missing={len(missing)} downloaded={downloaded} failed={len(failed)}", flush=True)
    if failed:
        print("failed_first_50:", flush=True)
        for r in failed[:50]:
            print(" -", r, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

