#!/usr/bin/env python3
"""Point syst3mc0r3.art's OG / Twitter card at DATASTREAMERS.

Run from ~/syst3mc0r3 after dropping og/datastreamers.jpg in place:
    python3 patch_hub_og.py && git add -A && git commit -m "og: datastreamers card" && git push
Idempotent: exits 0 with no change if already applied.
"""
import sys, pathlib

P = pathlib.Path("index.html")
s = P.read_text(encoding="utf-8")
MARK = "HUB_OG_DS"
if MARK in s:
    print("already applied"); sys.exit(0)

IMG_OLD = "https://img.syst3mc0r3.art/v3/44.png"
IMG_NEW = "https://syst3mc0r3.art/og/datastreamers.jpg"
DESC_OLD = "Onchain art."
DESC_NEW = "DATASTREAMERS: 1,000 corrupted frames from a Schwarzschild simulation. Free mint, live on Ink."
TITLE_NEW = "DATASTREAMERS · SYST3M C0R3"

def rep(old, new, n):
    global s
    c = s.count(old)
    assert c == n, f"expected {n} of {old!r}, found {c}"
    s = s.replace(old, new)

rep(IMG_OLD, IMG_NEW, 2)                       # og:image + twitter:image
rep(f'content="{DESC_OLD}"', f'content="{DESC_NEW}"', 2)   # og:description + twitter:description
rep('<meta property="og:title" content="SYST3M C0R3">',
    f'<meta property="og:title" content="{TITLE_NEW}">', 1)
rep('<meta name="twitter:title" content="SYST3M C0R3">',
    f'<meta name="twitter:title" content="{TITLE_NEW}">', 1)
# <meta name="description"> and <title> untouched

# explicit image dims help X/Discord render without a second fetch
s = s.replace(
    f'<meta property="og:image" content="{IMG_NEW}">',
    f'<meta property="og:image" content="{IMG_NEW}">\n'
    f'<meta property="og:image:width" content="1200">\n'
    f'<meta property="og:image:height" content="630">\n'
    f'<!-- {MARK} -->', 1)
assert MARK in s

P.write_text(s, encoding="utf-8")
print("patched: og/twitter image, description, title")
