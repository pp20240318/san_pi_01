"""Batch fill missing wp-content/uploads assets by month prefix.

Goal: make local offline copy complete without fetching everything at once.
Scans all *.html under SITE_DIR, extracts uploads refs, groups by YYYY/MM/,
then downloads missing files in small batches.

Usage (PowerShell):
  python -u tools/batch_fill_uploads_by_month.py --max-total 800 --per-month 200

Repeat until it prints overall_missing=0.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen


SITE_DIR = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
REMOTE_BASE = "https://hot51.biz.id/wp-content/uploads/"

LOCAL_UPLOAD_RE = re.compile(
    r"static/remote/hot51\.biz\.id/wp-content/uploads/(?P<rel>[\w\-/%.]+?\.(?:png|jpe?g|webp|gif|svg|ico))",
    re.IGNORECASE,
)
REMOTE_UPLOAD_RE = re.compile(
    r"https?://hot51\.biz\.id/wp-content/uploads/(?P<rel>[\w\-/%.]+?\.(?:png|jpe?g|webp|gif|svg|ico))",
    re.IGNORECASE,
)


def fetch_bytes(url: str, timeout: int = 60) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; batch_fill_uploads_by_month.py)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def month_prefix(rel: str) -> str | None:
    # rel like: 2025/07/Foo.webp
    parts = rel.split("/", 2)
    if len(parts) < 3:
        return None
    yyyy, mm = parts[0], parts[1]
    if not (len(yyyy) == 4 and yyyy.isdigit() and len(mm) == 2 and mm.isdigit()):
        return None
    return f"{yyyy}/{mm}/"


def iter_refs() -> set[str]:
    refs: set[str] = set()
    for html in SITE_DIR.glob("*.html"):
        t = html.read_text(encoding="utf-8", errors="ignore")
        refs |= {m.group("rel") for m in LOCAL_UPLOAD_RE.finditer(t)}
        refs |= {m.group("rel") for m in REMOTE_UPLOAD_RE.finditer(t)}
    return {r.replace("%2F", "/") for r in refs}


def missing_for(rel: str) -> bool:
    p = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads" / rel
    return (not p.exists()) or p.stat().st_size == 0


def download_rel(rel: str) -> None:
    out = SITE_DIR / "static/remote/hot51.biz.id/wp-content/uploads" / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    url = REMOTE_BASE + rel
    out.write_bytes(fetch_bytes(url))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-total", type=int, default=800, help="max downloads per run")
    ap.add_argument("--per-month", type=int, default=200, help="max downloads per month per run")
    ap.add_argument("--only", type=str, default="", help="only this prefix, e.g. 2025/07/")
    args = ap.parse_args(argv)

    only = args.only.strip().replace("\\", "/")
    if only and not only.endswith("/"):
        only += "/"

    refs = iter_refs()
    by_month: dict[str, list[str]] = defaultdict(list)
    unknown: list[str] = []
    for rel in refs:
        mp = month_prefix(rel)
        if not mp:
            unknown.append(rel)
            continue
        if only and not rel.startswith(only):
            continue
        by_month[mp].append(rel)

    # Compute missing lists per month
    missing_map: dict[str, list[str]] = {}
    overall_missing = 0
    for mp in sorted(by_month.keys()):
        miss = [r for r in sorted(set(by_month[mp])) if missing_for(r)]
        missing_map[mp] = miss
        overall_missing += len(miss)

    print(
        f"months={len(missing_map)} refs={len(refs)} overall_missing={overall_missing}"
        + (f" only={only!r}" if only else ""),
        flush=True,
    )

    if overall_missing == 0:
        return 0

    downloaded = 0
    failed = 0
    for mp in sorted(missing_map.keys()):
        if downloaded >= args.max_total:
            break
        miss = missing_map[mp]
        if not miss:
            continue
        take = miss[: max(0, min(args.per_month, args.max_total - downloaded))]
        if not take:
            continue
        print(f"month {mp} missing={len(miss)} fetching={len(take)}", flush=True)
        ok_this = 0
        for rel in take:
            try:
                download_rel(rel)
                downloaded += 1
                ok_this += 1
                if downloaded % 50 == 0:
                    print(f"  fetched_total={downloaded} failed={failed}", flush=True)
            except Exception as e:
                failed += 1
                if failed <= 20:
                    print(f"  FAIL {rel}: {e}", flush=True)
        print(f"  month_done {mp} ok={ok_this}", flush=True)

    print(f"run_done downloaded={downloaded} failed={failed}", flush=True)
    # If we failed a lot, return non-zero so it stands out.
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

