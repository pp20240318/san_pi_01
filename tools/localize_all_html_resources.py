from __future__ import annotations

from pathlib import Path

SITE_DIR = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")


def localize_html(text: str) -> str:
    t = text

    # Core resource roots
    t = t.replace("https://hot51.biz.id/wp-content/", "static/remote/hot51.biz.id/wp-content/")
    t = t.replace("http://hot51.biz.id/wp-content/", "static/remote/hot51.biz.id/wp-content/")
    t = t.replace("https://hot51.biz.id/wp-includes/", "static/remote/hot51.biz.id/wp-includes/")
    t = t.replace("http://hot51.biz.id/wp-includes/", "static/remote/hot51.biz.id/wp-includes/")

    # Local analytics/js fallback
    t = t.replace("https://hot51.biz.id/?local_ga_js=1", "static/js/-1.js")
    t = t.replace("http://hot51.biz.id/?local_ga_js=1", "static/js/-1.js")

    # Cloudflare email decode absolute path -> local
    t = t.replace(
        '/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js',
        'static/js/email-decode.min.js',
    )

    # Common top-level page links
    t = t.replace('href="https://hot51.biz.id/"', 'href="index.html"')
    t = t.replace("href='https://hot51.biz.id/'", "href='index.html'")
    t = t.replace('href="http://hot51.biz.id/"', 'href="index.html"')
    t = t.replace('href="https://hot51.biz.id/blog/"', 'href="blog.html"')
    t = t.replace('href="https://hot51.biz.id/contact-us/"', 'href="contact-us.html"')
    t = t.replace('href="https://hot51.biz.id/privacy-policy/"', 'href="privacy-policy.html"')

    # Search form should not post to remote when offline
    t = t.replace('action="https://hot51.biz.id/"', 'action="index.html"')
    t = t.replace("action='https://hot51.biz.id/'", "action='index.html'")

    # Map key CSS/JS to known local files under static/
    fixed = {
        "static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/css/flatsome.css?ver=3.20.5": "static/css/flatsome.css",
        "static/remote/hot51.biz.id/wp-content/themes/flatsome-child/style.css?ver=3.0": "static/css/style.css",
        "static/remote/hot51.biz.id/wp-content/plugins/seo-by-rank-math/includes/modules/schema/blocks/toc/assets/css/toc_list_style.css?ver=1.0.268": "static/css/toc_list_style.css",
        "static/remote/hot51.biz.id/wp-includes/js/jquery/jquery.min.js?ver=3.7.1": "static/js/jquery.min.js",
        "static/remote/hot51.biz.id/wp-includes/js/jquery/jquery-migrate.min.js?ver=3.4.1": "static/js/jquery-migrate.min.js",
        "static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/js/flatsome.js?ver=e2eddd6c228105dac048": "static/js/flatsome.js",
        "static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/js/extensions/flatsome-live-search.js?ver=3.20.5": "static/js/flatsome-live-search.js",
        "static/remote/hot51.biz.id/wp-includes/js/hoverIntent.min.js?ver=1.10.2": "static/js/hoverIntent.min.js",
    }
    for old, new in fixed.items():
        t = t.replace(old, new)

    # Keep share/canonical metadata as-is; they don't affect rendering.
    return t


def main() -> int:
    updated = 0
    files = sorted(SITE_DIR.glob("*.html"))
    for f in files:
        old = f.read_text(encoding="utf-8", errors="ignore")
        new = localize_html(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            updated += 1

    print(f"files={len(files)} updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

