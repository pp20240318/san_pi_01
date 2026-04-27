from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SITE_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")
SITE = "https://hot51.biz.id"


def fetch_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; clone_post_details.py)",
            "Accept": "text/html,*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def is_post_path(path: str) -> bool:
    # Keep only single-segment permalink paths: /some-slug/
    if not path.startswith("/"):
        return False
    if path in ("/", "/blog/", "/contact-us/", "/privacy-policy/"):
        return False
    if path.startswith("/wp-") or path.startswith("/wp-content/") or path.startswith("/wp-includes/"):
        return False
    if path.startswith("/feed/") or path.startswith("/comments/") or path.startswith("/xmlrpc.php"):
        return False
    # ignore search or query paths
    if "?" in path:
        return False
    parts = [p for p in path.split("/") if p]
    return len(parts) == 1


def filename_for_url(url: str) -> str | None:
    u = urlparse(url)
    if (u.scheme, u.netloc) not in (("https", "hot51.biz.id"), ("http", "hot51.biz.id")):
        return None
    path = u.path
    if not is_post_path(path):
        return None
    slug = [p for p in path.split("/") if p][0]
    # basic filename safety
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug).strip("-")
    if not slug:
        return None
    return f"{slug}.html"


HREF_RE = re.compile(r'href=["\'](https?://hot51\.biz\.id/[^"\']+)["\']', re.I)


def localize_internal_links(html: str) -> str:
    # permalink pages -> local html
    def repl(m: re.Match[str]) -> str:
        url = m.group(1)
        fn = filename_for_url(url)
        if fn:
            return f'href="{fn}"'
        return m.group(0)

    html = HREF_RE.sub(repl, html)

    # Also fix main nav common pages
    html = html.replace('href="https://hot51.biz.id/"', 'href="index.html"')
    html = html.replace("href='https://hot51.biz.id/'", "href='index.html'")
    html = html.replace('href="https://hot51.biz.id/blog/"', 'href="blog.html"')
    html = html.replace('href="https://hot51.biz.id/contact-us/"', 'href="contact-us.html"')
    html = html.replace('href="https://hot51.biz.id/privacy-policy/"', 'href="privacy-policy.html"')
    return html


def iter_seed_files() -> list[Path]:
    seeds: list[Path] = []
    if (SITE_DIR / "blog.html").exists():
        seeds.append(SITE_DIR / "blog.html")
    for i in range(2, 140):
        p = SITE_DIR / f"{i}.html"
        if p.exists():
            seeds.append(p)
    return seeds


def main() -> int:
    seeds = iter_seed_files()
    if not seeds:
        print("No seed pages found (blog.html, 2..139).")
        return 2

    urls: set[str] = set()
    for f in seeds:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in HREF_RE.finditer(text):
            url = m.group(1)
            if filename_for_url(url):
                urls.add(url)

    print(f"found_post_urls={len(urls)}", flush=True)

    downloaded = 0
    skipped = 0
    for idx, url in enumerate(sorted(urls), start=1):
        fn = filename_for_url(url)
        if not fn:
            continue
        out = SITE_DIR / fn
        if out.exists() and out.stat().st_size > 0:
            skipped += 1
            continue
        try:
            html = fetch_text(url)
            html = localize_internal_links(html)
            out.write_text(html, encoding="utf-8")
            downloaded += 1
        except Exception:
            pass
        if idx % 50 == 0:
            print(f"progress {idx}/{len(urls)} downloaded={downloaded} skipped={skipped}", flush=True)

    # Rewrite seed pages to point to local details
    rewrote = 0
    for f in seeds:
        text = f.read_text(encoding="utf-8", errors="ignore")
        new_text = localize_internal_links(text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            rewrote += 1

    print(f"done downloaded={downloaded} skipped={skipped} rewrote_seeds={rewrote}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

