from __future__ import annotations

import re
from pathlib import Path
from urllib.request import Request, urlopen


SITE = "https://hot51.biz.id"
BLOG_PAGE_URL = SITE + "/blog/page/{n}/"
TARGET_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")


def fetch_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; clone_blog_pagination.py)",
            "Accept": "text/html,*/*",
        },
    )
    with urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def localize_pagination_links(html: str) -> str:
    # Blog root page and pagination
    html = html.replace(f'{SITE}/blog/"', 'blog.html"')
    html = html.replace(f"{SITE}/blog/'", "blog.html'")
    html = re.sub(rf"{re.escape(SITE)}/blog/page/(\d+)/", r"\1.html", html)
    # Handle relative /blog/page/N/ and /blog/
    html = re.sub(r'(?<=["\'])/blog/page/(\d+)/', r"\1.html", html)
    html = re.sub(r'(?<=["\'])/blog/', "blog.html", html)
    html = html.replace('href="1.html"', 'href="blog.html"')
    html = html.replace("href='1.html'", "href='blog.html'")
    return html


def main() -> int:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail: list[int] = []

    for n in range(2, 140):
        url = BLOG_PAGE_URL.format(n=n)
        out = TARGET_DIR / f"{n}.html"
        try:
            html = fetch_text(url)
            html = localize_pagination_links(html)
            out.write_text(html, encoding="utf-8")
            ok += 1
            print(f"ok {n}")
        except Exception as ex:
            fail.append(n)
            print(f"fail {n}: {ex}")

    # Also normalize local blog root page links
    blog_root = TARGET_DIR / "blog.html"
    if blog_root.exists():
        root_text = blog_root.read_text(encoding="utf-8", errors="ignore")
        new_root = localize_pagination_links(root_text)
        if new_root != root_text:
            blog_root.write_text(new_root, encoding="utf-8")
            print("normalized blog.html pagination links")

    print(f"done ok={ok} fail={len(fail)}")
    if fail:
        print("failed pages:", ",".join(map(str, fail)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

