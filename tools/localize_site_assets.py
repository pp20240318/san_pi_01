from __future__ import annotations

import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


RESOURCE_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
    ".ico",
    ".css",
    ".js",
    ".woff2",
    ".woff",
    ".ttf",
    ".eot",
    ".otf",
    ".mp4",
    ".webm",
    ".mp3",
    ".wav",
    ".json",
    ".xml",
}


URL_RE = re.compile(
    r"""(?P<url>(?:https?:)?//[^\s"'<>]+|https?://[^\s"'<>]+)""",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DownloadItem:
    url: str
    local_rel: str  # relative to site root (posix)


def _normalize_url(raw: str) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("//"):
        return "https:" + raw
    if raw.lower().startswith("http://") or raw.lower().startswith("https://"):
        return raw
    return None


def _is_resource_url(u: str) -> bool:
    p = urlparse(u)
    path = p.path or ""
    ext = Path(path).suffix.lower()
    return ext in RESOURCE_EXTS


def _safe_posix_path(s: str) -> str:
    s = s.replace("\\", "/")
    s = re.sub(r"/{2,}", "/", s)
    s = s.lstrip("/")
    s = re.sub(r"[^A-Za-z0-9._/=-]", "_", s)
    return s


def _local_rel_for(url: str) -> str:
    """
    Save into: static/remote/<host>/<path> (with hash if query present).
    """
    p = urlparse(url)
    host = p.netloc or "unknown-host"
    path = p.path or "/"
    path_clean = _safe_posix_path(path)
    base = Path(path_clean).name or "index"
    parent = str(Path(path_clean).parent).replace("\\", "/")
    parent = "" if parent in (".", "/") else parent

    ext = Path(base).suffix
    if not ext:
        ext = ".bin"

    # If query/fragment exists, add stable hash to avoid collisions
    if p.query or p.fragment:
        h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        stem = Path(base).stem or "asset"
        base = f"{stem}.{h}{ext}"

    parts = ["static", "remote", _safe_posix_path(host)]
    if parent:
        parts.append(parent)
    parts.append(base)
    return "/".join([x for x in parts if x])


def _iter_html_files(site_dir: Path) -> Iterable[Path]:
    yield from sorted(site_dir.rglob("*.html"))


def _extract_resource_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for m in URL_RE.finditer(text):
        u = _normalize_url(m.group("url"))
        if not u:
            continue
        if _is_resource_url(u):
            # strip fragment for fetching; keep full url for mapping
            urls.add(u)
    return urls


def _fetch_bytes(url: str, timeout_s: int = 30) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; localize_site_assets.py)",
            "Accept": "*/*",
        },
        method="GET",
    )
    with urlopen(req, timeout=timeout_s) as resp:
        return resp.read()


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _replace_urls(text: str, mapping: dict[str, str]) -> str:
    # Replace longest-first to avoid partial overlaps
    for src in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(src, mapping[src])
    return text


def localize(site_dir: Path) -> None:
    site_dir = site_dir.resolve()
    if not site_dir.exists():
        raise SystemExit(f"Site dir not found: {site_dir}")

    html_files = list(_iter_html_files(site_dir))
    if not html_files:
        print(f"No .html files found under {site_dir}")
        return

    # 1) Collect all resource URLs from html
    resource_urls: set[str] = set()
    html_texts: dict[Path, str] = {}
    for f in html_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        html_texts[f] = txt
        resource_urls |= _extract_resource_urls(txt)

    if not resource_urls:
        print("No remote resource URLs found in HTML.")
        return

    # 2) Build mapping and download files
    mapping: dict[str, str] = {}
    downloaded = 0
    failed: list[str] = []

    for url in sorted(resource_urls):
        local_rel = _local_rel_for(url)
        mapping[url] = local_rel
        local_abs = site_dir / Path(local_rel)
        if local_abs.exists() and local_abs.stat().st_size > 0:
            continue
        try:
            data = _fetch_bytes(url)
            _write_file(local_abs, data)
            downloaded += 1
        except Exception:
            failed.append(url)

    # 3) Rewrite HTML files
    rewritten = 0
    for f, txt in html_texts.items():
        new_txt = _replace_urls(txt, mapping)
        if new_txt != txt:
            f.write_text(new_txt, encoding="utf-8", errors="ignore")
            rewritten += 1

    print(f"HTML files: {len(html_files)}")
    print(f"Remote resource URLs found: {len(resource_urls)}")
    print(f"Downloaded new files: {downloaded}")
    print(f"Rewritten HTML files: {rewritten}")
    if failed:
        print(f"Failed downloads: {len(failed)}")
        for u in failed[:50]:
            print(f"  - {u}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/localize_site_assets.py <site_dir>", file=sys.stderr)
        return 2
    localize(Path(argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

