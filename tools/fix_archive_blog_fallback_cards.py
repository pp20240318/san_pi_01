from pathlib import Path
import re


ROOT = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
ARCHIVE_RE = re.compile(r"^\d+\.html$")
CARD_LINK_RE = re.compile(r'<a href="blog\.html" class="plain" aria-label="([^"]+)">', re.IGNORECASE)


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return f"{s}.html" if s else "blog.html"


def make_placeholder(path: Path, title: str) -> None:
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
</head>
<body style="font-family:Arial,sans-serif;max-width:760px;margin:48px auto;line-height:1.6;padding:0 16px;">
  <h1>{title}</h1>
  <p>Artikel ini sedang dalam proses sinkronisasi arsip offline.</p>
  <p><a href="blog.html">Kembali ke daftar blog</a></p>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    files = sorted([p for p in ROOT.glob("*.html") if ARCHIVE_RE.match(p.name)])
    existing = {p.name for p in ROOT.glob("*.html")}
    changed_files = 0
    changed_links = 0
    created_pages = 0

    for page in files:
        content = page.read_text(encoding="utf-8", errors="ignore")
        labels = CARD_LINK_RE.findall(content)
        if not labels:
            continue

        new_content = content
        for label in labels:
            target = slugify(label)
            if target == "blog.html":
                continue
            old1 = f'<a href="blog.html" class="plain" aria-label="{label}">'
            new1 = f'<a href="{target}" class="plain" aria-label="{label}">'
            old2 = f'<a href="blog.html" class="plain">{label}</a>'
            new2 = f'<a href="{target}" class="plain">{label}</a>'
            if old1 in new_content:
                new_content = new_content.replace(old1, new1)
                changed_links += 1
            if old2 in new_content:
                new_content = new_content.replace(old2, new2)
                changed_links += 1
            if target not in existing:
                make_placeholder(ROOT / target, label)
                existing.add(target)
                created_pages += 1

        if new_content != content:
            page.write_text(new_content, encoding="utf-8")
            changed_files += 1

    print(
        f"changed_files={changed_files} changed_links={changed_links} "
        f"created_placeholder_pages={created_pages}"
    )


if __name__ == "__main__":
    main()
