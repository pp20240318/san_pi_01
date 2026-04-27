from pathlib import Path
import re

site = Path("F:/2026Code/san_pi_01/Zz_hot51.biz.id")

attr_re = re.compile(
    r"\s+integrity=\"[^\"]*\"\s+data-cf-beacon='[^']*'\s+crossorigin=\"anonymous\"",
    re.IGNORECASE,
)

updated = 0
for html in site.glob("*.html"):
    text = html.read_text(encoding="utf-8", errors="ignore")
    new_text, n = attr_re.subn("", text)
    if n:
        html.write_text(new_text, encoding="utf-8")
        updated += 1

print(updated)
