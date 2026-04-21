import hashlib
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


ROOT = Path("F:/2026Code/san_pi_01/Zz_hot51.app")
ASSET_DIR = ROOT / "local_assets"

# Match absolute URLs in quotes, parenthesis, and srcset-like text.
URL_RE = re.compile(r"https?://[^\s\"'()<>,]+")
RESOURCE_EXT_RE = re.compile(
    r"\.(?:png|jpe?g|gif|webp|svg|ico|bmp|avif|css|js|woff2?|ttf|eot|otf|map)(?:\?.*)?$",
    re.IGNORECASE,
)

SKIP_HOSTS = {
    "schema.org",
    "ogp.me",
    "gmpg.org",
    "api.w.org",
    "googletagmanager.com",
    "google-analytics.com",
    "doubleclick.net",
    "googlesyndication.com",
    "google.com",
}
PRIMARY_HOSTS = {"hot51.app", "www.hot51.app"}


def should_download(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if not host:
        return False
    if host not in PRIMARY_HOSTS:
        return False
    for skip in SKIP_HOSTS:
        if host == skip or host.endswith("." + skip):
            return False

    path = parsed.path.lower()
    if RESOURCE_EXT_RE.search(path) or "/wp-content/" in path or "/wp-includes/" in path:
        return True
    return False


def build_local_path(url: str) -> Path:
    parsed = urlparse(url)
    host = parsed.netloc.lower().replace(":", "_")
    raw_path = unquote(parsed.path.lstrip("/"))
    if not raw_path:
        raw_path = "index.html"

    path = Path(raw_path)
    suffix = path.suffix
    if parsed.query:
        digest = hashlib.md5(parsed.query.encode("utf-8")).hexdigest()[:8]
        if suffix:
            path = path.with_name(f"{path.stem}_{digest}{suffix}")
        else:
            path = Path(str(path) + "_" + digest)
    return ASSET_DIR / host / path


def download(url: str, target: Path) -> bool:
    if target.exists() and target.stat().st_size > 0:
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urlopen(req, timeout=6) as resp:
            data = resp.read()
        if not data:
            return False
        target.write_bytes(data)
        return True
    except Exception:
        return False


def local_ref(from_file: Path, target: Path) -> str:
    rel = os.path.relpath(target, start=from_file.parent)
    return rel.replace("\\", "/")


def process_file(path: Path, downloaded: dict[str, Path], failed: set[str]) -> tuple[bool, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    changed = False
    replacements = 0

    for url in sorted(set(URL_RE.findall(text)), key=len, reverse=True):
        if not should_download(url):
            continue

        if url in failed:
            continue

        target = downloaded.get(url)
        if target is None:
            target = build_local_path(url)
            ok = download(url, target)
            if ok:
                downloaded[url] = target
            else:
                failed.add(url)
                continue

        ref = local_ref(path, target)
        if url in text:
            text = text.replace(url, ref)
            changed = True
            replacements += 1

    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, replacements


def main() -> None:
    files = list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.css"))
    downloaded: dict[str, Path] = {}
    failed: set[str] = set()
    changed_files = 0
    total_replacements = 0

    for idx, f in enumerate(files, start=1):
        if idx % 10 == 0:
            print(f"Progress: {idx}/{len(files)}")
        changed, count = process_file(f, downloaded, failed)
        if changed:
            changed_files += 1
            total_replacements += count

    print(f"Processed files: {len(files)}")
    print(f"Changed files: {changed_files}")
    print(f"Downloaded resources: {len(downloaded)}")
    print(f"URL replacements: {total_replacements}")
    print(f"Failed downloads: {len(failed)}")
    if failed:
        print("Sample failed URLs:")
        for url in sorted(list(failed))[:20]:
            print(f"- {url}")


if __name__ == "__main__":
    main()
