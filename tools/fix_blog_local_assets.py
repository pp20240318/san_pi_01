from pathlib import Path
import re

site = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")
pages = [site / "blog.html"] + [site / f"{i}.html" for i in range(2, 140)]

repls = [
    ("https://hot51.biz.id/wp-content/themes/flatsome/assets/css/flatsome.css?ver=3.20.5", "static/css/flatsome.css"),
    ("https://hot51.biz.id/wp-content/themes/flatsome-child/style.css?ver=3.0", "static/css/style.css"),
    ("https://hot51.biz.id/wp-includes/js/jquery/jquery.min.js?ver=3.7.1", "static/js/jquery.min.js"),
    ("https://hot51.biz.id/wp-includes/js/jquery/jquery-migrate.min.js?ver=3.4.1", "static/js/jquery-migrate.min.js"),
    ("https://hot51.biz.id/?local_ga_js=1", "static/js/-1.js"),
]

prefix_map = [
    ("https://hot51.biz.id/wp-content/uploads/", "static/remote/hot51.biz.id/wp-content/uploads/"),
    ("https://hot51.biz.id/wp-content/fonts/", "static/remote/hot51.biz.id/wp-content/fonts/"),
    ("https://hot51.biz.id/wp-content/themes/flatsome/assets/css/icons/", "static/font/"),
]

removed_patterns = [
    re.compile(r"^\s*<link rel='prefetch' href='https://hot51\.biz\.id/wp-content/themes/flatsome/assets/js/[^']*'\s*/>\s*$", re.M),
    re.compile(r'<script[^>]*id="google_gtagjs"[^>]*></script>\s*', re.I),
]

updated = 0
for p in pages:
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    nt = t
    for a, b in repls:
        nt = nt.replace(a, b)
    for a, b in prefix_map:
        nt = nt.replace(a, b)
    for pat in removed_patterns:
        nt = pat.sub("", nt)

    nt = nt.replace('href="https://hot51.biz.id/"', 'href="index.html"')
    nt = nt.replace("href='https://hot51.biz.id/'", "href='index.html'")
    nt = nt.replace('action="https://hot51.biz.id/"', 'action="index.html"')

    if nt != t:
        p.write_text(nt, encoding="utf-8")
        updated += 1

print(f"updated={updated}")

