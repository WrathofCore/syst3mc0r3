#!/usr/bin/env python3
import sys, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")
if "HUB_LABEL_FIX" in s: print("labels: already applied"); sys.exit(0)
OLD1 = """    dsSetBtn(id,'Confirm in wallet…',true);
    const c=await dsSigner();
    const tx=await fn(c);"""
NEW1 = """    dsSetBtn(id,'Connecting…',true); /* HUB_LABEL_FIX */
    const c=await dsSigner();
    dsSetBtn(id,'Checking…',true);
    const tx=await fn(c);"""
OLD2 = """    try{ turnstile.reset(dsWidget); }catch(e){}
    return c.mint(j.qty, j.deadline, j.sig);"""
NEW2 = """    try{ turnstile.reset(dsWidget); }catch(e){}
    dsSetBtn('mintDS','Confirm in wallet…',true);
    return c.mint(j.qty, j.deadline, j.sig);"""
assert s.count(OLD1) == 1, "dsTx label block not found"
assert s.count(OLD2) == 1, "mint call not found"
s = s.replace(OLD1, NEW1, 1).replace(OLD2, NEW2, 1)
P.write_text(s, encoding="utf-8"); print("labels: patched")
