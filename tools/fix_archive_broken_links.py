from pathlib import Path
from urllib.parse import urlsplit
import re


ROOT = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
ARCHIVE_RE = re.compile(r"^\d+\.html$")
HREF_RE = re.compile(r'href=(["\'])(.*?)\1', re.IGNORECASE)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
STOP = {"di", "dan", "yang", "apk", "hot51", "cantik", "bintang", "pesona", "terbaru", "memukau", "girl"}


def tokens(name: str) -> set[str]:
    stem = Path(name).stem.lower()
    return {t for t in TOKEN_RE.findall(stem) if t not in STOP and not t.isdigit()}


def similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def main() -> None:
    files = sorted(ROOT.glob("*.html"))
    existing = {f.name for f in files}
    archive_pages = [f for f in files if ARCHIVE_RE.match(f.name)]
    article_pages = [f.name for f in files if not ARCHIVE_RE.match(f.name) and f.name not in {"index.html", "blog.html"}]
    article_tokens = {name: tokens(name) for name in article_pages}

    changed_files = 0
    changed_links = 0
    unresolved = 0

    for page in archive_pages:
        content = page.read_text(encoding="utf-8", errors="ignore")
        replacements: dict[str, str] = {}
        for m in HREF_RE.finditer(content):
            href = m.group(2).strip()
            if (
                not href
                or href.startswith("#")
                or href.startswith("mailto:")
                or href.startswith("tel:")
                or href.startswith("javascript:")
                or "://" in href
                or href.startswith("//")
            ):
                continue
            p = urlsplit(href).path
            if not p.lower().endswith(".html"):
                continue
            target = Path(p).name
            if not target or target in existing:
                continue
            if href in replacements:
                continue

            t = tokens(target)
            best_name = None
            best_score = 0.0
            for cand, cand_t in article_tokens.items():
                score = similarity(t, cand_t)
                if score > best_score:
                    best_score = score
                    best_name = cand

            if best_name and best_score >= 0.34:
                replacements[href] = href.replace(target, best_name)
            else:
                replacements[href] = "blog.html"
                unresolved += 1

        if replacements:
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            if new_content != content:
                page.write_text(new_content, encoding="utf-8")
                changed_files += 1
                changed_links += len(replacements)

    print(f"archive_pages={len(archive_pages)} changed_files={changed_files} changed_links={changed_links} fallback_to_blog={unresolved}")


if __name__ == "__main__":
    main()
