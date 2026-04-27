from __future__ import annotations

import re
from pathlib import Path
from urllib.request import Request, urlopen


SITE_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")


def fetch_bytes(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; fix_offline_errors.py)",
            "Accept": "*/*",
        },
    )
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def ensure_download(url: str, local_abs: Path) -> bool:
    if local_abs.exists() and local_abs.stat().st_size > 0:
        return False
    local_abs.parent.mkdir(parents=True, exist_ok=True)
    data = fetch_bytes(url)
    local_abs.write_bytes(data)
    return True


def main() -> int:
    # 1) Replace Cloudflare email-decode absolute path (breaks on file://)
    #    /cdn-cgi/... -> static/js/email-decode.min.js
    email_decode_pat = re.compile(
        r'(<script[^>]+src=["\'])/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode\.min\.js(["\'])',
        re.IGNORECASE,
    )

    # 2) Replace remote live-search / hoverIntent to local copies
    replacements = [
        (
            "https://hot51.biz.id/wp-content/themes/flatsome/assets/js/extensions/flatsome-live-search.js?ver=3.20.5",
            "static/js/flatsome-live-search.js",
        ),
        (
            "https://hot51.biz.id/wp-includes/js/hoverIntent.min.js?ver=1.10.2",
            "static/js/hoverIntent.min.js",
        ),
    ]

    updated = 0
    for html in SITE_DIR.glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        new_text = email_decode_pat.sub(r"\1static/js/email-decode.min.js\2", text)
        for a, b in replacements:
            new_text = new_text.replace(a, b)
        if new_text != text:
            html.write_text(new_text, encoding="utf-8")
            updated += 1

    print(f"html_updated={updated}")

    # 3) Ensure the specific missing image exists locally
    rel = "static/remote/hot51.biz.id/wp-content/uploads/2026/04/Georgia-Fisher-HOT51.COM_-2-768x384.webp"
    local_abs = SITE_DIR / rel
    remote_url = "https://hot51.biz.id/wp-content/uploads/2026/04/Georgia-Fisher-HOT51.COM_-2-768x384.webp"
    downloaded = ensure_download(remote_url, local_abs)
    print(f"image_downloaded={int(downloaded)} -> {local_abs}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

