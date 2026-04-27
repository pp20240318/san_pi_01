from __future__ import annotations

import re
from pathlib import Path
from urllib.request import Request, urlopen


SITE_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")
REMOTE_BASE = "https://hot51.biz.id/"

# Capture both already-localized and still-remote uploads URLs
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
            "User-Agent": "Mozilla/5.0 (compatible; fill_missing_uploads.py)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def ensure_download(rel: str) -> bool:
    # rel looks like: 2026/04/Foo.webp
    local_abs = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads" / rel
    if local_abs.exists() and local_abs.stat().st_size > 0:
        return False
    local_abs.parent.mkdir(parents=True, exist_ok=True)
    url = REMOTE_BASE + "wp-content/uploads/" + rel
    data = fetch_bytes(url)
    local_abs.write_bytes(data)
    return True


def main() -> int:
    refs: set[str] = set()
    for html in SITE_DIR.glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        refs |= {m.group("rel") for m in LOCAL_UPLOAD_RE.finditer(text)}
        refs |= {m.group("rel") for m in REMOTE_UPLOAD_RE.finditer(text)}

    if not refs:
        print("no upload refs found")
        return 0

    refs = {r.replace("%2F", "/") for r in refs}  # safety
    total = len(refs)
    downloaded = 0
    failed: list[str] = []

    for i, rel in enumerate(sorted(refs), start=1):
        try:
            if ensure_download(rel):
                downloaded += 1
            if i % 100 == 0:
                print(f"progress {i}/{total} downloaded={downloaded} failed={len(failed)}", flush=True)
        except Exception:
            failed.append(rel)

    print(f"done total_refs={total} downloaded={downloaded} failed={len(failed)}", flush=True)
    if failed:
        print("failed_first_50:", flush=True)
        for r in failed[:50]:
            print(" -", r, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

