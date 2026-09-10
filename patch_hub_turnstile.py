#!/usr/bin/env python3
import sys, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")
if "HUB_TURNSTILE_VIS" in s: print("turnstile visibility: already applied"); sys.exit(0)
OLD = """  dsWidget = turnstile.render(el, { sitekey: DS.turnstileSiteKey, theme:'dark', appearance:'interaction-only' });
}"""
NEW = """  dsWidget = turnstile.render(el, { sitekey: DS.turnstileSiteKey, theme:'dark', appearance:'interaction-only' });
  /* HUB_TURNSTILE_VIS: interaction-only means the checkbox appears out of nowhere. In the
     mobile sheet it can land below the fold, so scroll it into view the moment it has height. */
  if(!el.__dsWatch){
    el.__dsWatch = 1;
    try{
      new ResizeObserver(()=>{
        if(el.offsetHeight > 10){
          try{ el.scrollIntoView({block:'center', behavior:'smooth'}); }catch(e){ el.scrollIntoView(); }
          dsSetStatus('Check the box to continue');
        }
      }).observe(el);
    }catch(e){}
  }
}"""
assert s.count(OLD) == 1, "turnstile render block not found exactly once"
s = s.replace(OLD, NEW, 1)
OLDCSS = "  @media (max-width:760px){\n    .vol{display:none;}"
NEWCSS = ("  @media (max-width:760px){\n"
          "    #ds-turnstile-m{ scroll-margin:20px 0; }\n"
          "    .detail{ padding-bottom:34px; }\n"
          "    .vol{display:none;}")
assert s.count(OLDCSS) == 1, "mobile css block not found"
s = s.replace(OLDCSS, NEWCSS, 1)
P.write_text(s, encoding="utf-8"); print("turnstile visibility: patched")
