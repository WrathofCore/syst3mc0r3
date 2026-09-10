#!/usr/bin/env python3
import requests, time
from collections import Counter
RPC="https://rpc-gel.inkonchain.com"
DS="0xd0bd2E8dD22F65d7d4B696bd9953dC816A82C386".lower()
PIPS="0x1c882abe733534910bb334d25ce0f8ce46f0e164"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
Z="0x"+"0"*64
def rpc(m,p):
    j=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":m,"params":p},timeout=30).json()
    if "error" in j: raise SystemExit(j["error"])
    return j["result"]
head=int(rpc("eth_blockNumber",[]),16)
lo,hi=0,head
while lo<hi:
    mid=(lo+hi)//2
    lo,hi=(lo,mid) if rpc("eth_getCode",[DS,hex(mid)])!="0x" else (mid+1,hi)
logs=[];start=lo
while start<=head:
    end=min(start+9000,head)
    logs+=rpc("eth_getLogs",[{"address":DS,"fromBlock":hex(start),"toBlock":hex(end),"topics":[TRANSFER,Z]}])
    start=end+1
per=Counter(("0x"+l["topics"][2][-40:]).lower() for l in logs)
ws=list(per); print(f"{len(ws)} unique minters, checking pips one at a time...")
held={}; errs=0
for i,w in enumerate(ws):
    try:
        r=requests.post(RPC,json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":PIPS,"data":"0x70a08231"+w[2:].rjust(64,"0")},"latest"]},timeout=20).json()
        if "error" in r: errs+=1; continue
        v=int(r["result"],16)
        if v>0: held[w]=v
    except Exception: errs+=1
    if i%50==49: print(f"  {i+1}/{len(ws)}  holders so far {len(held)}"); time.sleep(0.3)
print(f"\npip holders among minters: {len(held)} of {len(ws)}   (errors: {errs})")
twos=[w for w,n in per.items() if n>=2]
print(f"wallets that minted 2: {len(twos)}, of those holding pips: {sum(1 for w in twos if w in held)}")
for w,v in sorted(held.items(), key=lambda x:-x[1])[:20]: print(f"  {w}  {v} pips  minted {per[w]}")
