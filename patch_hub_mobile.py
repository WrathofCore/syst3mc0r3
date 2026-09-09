#!/usr/bin/env python3
"""Phone layout fix for syst3mc0r3.art (<=760px only). Desktop untouched, no script changes.

  - header nav becomes a wrapping row; volume sliders hidden on phones (toggles stay)
  - collections drawer anchors under the header instead of floating mid-screen
  - DS stage: Recently Minted sits under the header, hero box starts below the tiles,
    caption pinned to the stage bottom so it can't land inside the detail sheet

Run from ~/syst3mc0r3:
    python3 patch_hub_mobile.py && git add -A && git commit -m "hub: phone layout" && git push
Idempotent.
"""
import sys, pathlib

P = pathlib.Path("index.html")
s = P.read_text(encoding="utf-8")
MARK = "HUB_MOBILE_FIX"
if MARK in s:
    print("already applied"); sys.exit(0)

CSS = f"""
  /* {MARK}: phone layout. header row, drawer under header, DS stage below the minted strip */
  @media (max-width:760px){{
    .vol{{display:none;}}
    .meta{{max-width:calc(100vw - 150px);}}
    .nav{{flex-direction:row; flex-wrap:wrap; justify-content:flex-end; align-items:center; gap:6px 14px;}}
    #wallet-btn{{margin-top:0;}}
    .colllist{{top:88px; bottom:auto; max-height:calc(100vh - 100px); overflow-y:auto;}}
    body.list-open .colllist{{bottom:auto;}}
    #ds-stage{{top:186px; bottom:58vh; align-items:flex-start;}}
    #ds-stage .box{{width:max(90px, min(150px, 34vmin, calc(42vh - 216px))); margin-bottom:0;}}
    #ds-stage .ds-recent{{top:88px;}}
    #ds-cap{{bottom:0 !important;}}
  }}
"""

anchor = "</style>"
assert s.count(anchor) == 1, f"expected 1 </style>, found {s.count(anchor)}"
s = s.replace(anchor, CSS + anchor, 1)
P.write_text(s, encoding="utf-8")
print("patched: phone layout block added")
