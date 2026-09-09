#!/usr/bin/env python3
import sys, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")
if "HUB_ACCOUNTS_FIX" in s: print("accounts: already applied"); sys.exit(0)
OLD = "  await p.send('eth_requestAccounts',[]);\n  const id=await eth.request({method:'eth_chainId'}).catch(()=>'');"
NEW = ("  /* HUB_ACCOUNTS_FIX: silent check first; only prompt to connect if the site truly isn't connected */\n"
       "  const accs=await eth.request({method:'eth_accounts'}).catch(()=>[]);\n"
       "  if(!accs||!accs.length) await p.send('eth_requestAccounts',[]);\n"
       "  const id=await eth.request({method:'eth_chainId'}).catch(()=>'');")
assert s.count(OLD) == 1, "signer accounts line not found"
s = s.replace(OLD, NEW, 1)
P.write_text(s, encoding="utf-8"); print("accounts: patched")
