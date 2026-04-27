from pathlib import Path

target = Path(
    "F:/2026Code/san_pi_01/Zz_hot51.biz.id/static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/js/flatsome.2ea394a51301.js"
)

old = b'a.p=globalThis.flatsomeVars?.assets_url??"/",'
new = b'a.p=("file:"===globalThis.location?.protocol?"static/remote/hot51.biz.id/wp-content/themes/flatsome/assets/":(globalThis.flatsomeVars?.assets_url??"/")),'

b = target.read_bytes()
i = b.find(old)
if i == -1:
    raise SystemExit("pattern not found")

target.write_bytes(b.replace(old, new, 1))
print("patched")

