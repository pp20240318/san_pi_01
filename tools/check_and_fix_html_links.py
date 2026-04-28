from pathlib import Path
from urllib.parse import urlsplit
import re


ROOT = Path(r"F:/2026Code/san_pi_01/Zz_hot51.biz.id")
HTML_FILES = sorted(ROOT.glob("*.html"))
HTML_NAMES = {p.name for p in HTML_FILES}
HREF_RE = re.compile(r'href=(["\'])(.*?)\1', re.IGNORECASE)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def normalize_tokens(filename: str) -> tuple[str, ...]:
    stem = Path(filename).stem.lower()
    tokens = [t for t in TOKEN_RE.findall(stem) if t not in {"html"}]
    return tuple(sorted(tokens))


def main() -> None:
    token_index: dict[tuple[str, ...], list[str]] = {}
    for name in HTML_NAMES:
        token_index.setdefault(normalize_tokens(name), []).append(name)

    missing_records: list[tuple[Path, str, str]] = []
    for file_path in HTML_FILES:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
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
            parsed = urlsplit(href)
            path = parsed.path
            if not path.lower().endswith(".html"):
                continue
            target_name = Path(path).name
            if target_name and target_name not in HTML_NAMES:
                missing_records.append((file_path, href, target_name))

    print(f"html_files={len(HTML_FILES)} missing_links={len(missing_records)}")

    fix_map: dict[Path, dict[str, str]] = {}
    unresolved = []
    for file_path, href, target_name in missing_records:
        candidates = token_index.get(normalize_tokens(target_name), [])
        if len(candidates) == 1:
            fixed_name = candidates[0]
            new_href = href.replace(target_name, fixed_name)
            fix_map.setdefault(file_path, {})[href] = new_href
        else:
            unresolved.append((file_path.name, href, len(candidates)))

    updated_files = 0
    updated_links = 0
    for file_path, repls in fix_map.items():
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        new_content = content
        for old, new in repls.items():
            new_content = new_content.replace(old, new)
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            updated_files += 1
            updated_links += len(repls)

    print(f"auto_fixed_files={updated_files} auto_fixed_links={updated_links}")
    print(f"unresolved_links={len(unresolved)}")
    for item in unresolved[:80]:
        print(f"{item[0]} -> {item[1]} (candidates={item[2]})")


if __name__ == "__main__":
    main()
