#!/usr/bin/env python3
import requests, time, json
from collections import Counter, defaultdict
RPC="https://rpc-gel.inkonchain.com"
API="https://explorer.inkonchain.com/api"
DS="0xd0bd2E8dD22F65d7d4B696bd9953dC816A82C386".lower()
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
minters=sorted({("0x"+l["topics"][2][-40:]).lower() for l in logs})
print(f"{len(minters)} unique minters. tracing funding source (this takes a few minutes)...")
funder={}; firstseen={}; fails=0
for i,w in enumerate(minters):
    try:
        r=requests.get(API,params={"module":"account","action":"txlist","address":w,
            "startblock":0,"endblock":99999999,"page":1,"offset":20,"sort":"asc"},timeout=25).json()
        txs=r.get("result") or []
        if isinstance(txs,list):
            for t in txs:
                if (t.get("to") or "").lower()==w and int(t.get("value","0"))>0:
                    funder[w]=(t.get("from") or "").lower()
                    firstseen[w]=int(t.get("timeStamp",0)); break
    except Exception: fails+=1
    if i%50==49:
        print(f"  {i+1}/{len(minters)}  traced {len(funder)}  fails {fails}"); time.sleep(0.4)
    time.sleep(0.08)
print(f"\ntraced funding for {len(funder)} of {len(minters)} wallets (fails {fails})")
c=Counter(funder.values())
print(f"{len(c)} distinct funding sources\n")
print("--- top funders ---")
covered=0
for addr,n in c.most_common(25):
    if n>1: covered+=n
    print(f"  {addr}  funded {n}")
big=sum(n for a,n in c.items() if n>=5)
print(f"\nwallets funded by a source that funded 5+ wallets: {big} of {len(funder)}")
print(f"wallets funded by a source that funded 2+ wallets: {covered} of {len(funder)}")
print(f"wallets with a unique funder (1 each):             {sum(1 for a,n in c.items() if n==1)}")
if firstseen:
    hours=Counter(t//3600*3600 for t in firstseen.values())
    top=hours.most_common(5)
    print("\n--- wallet creation, busiest hours ---")
    for h,n in top: print(f"  {time.strftime('%m-%d %H:00',time.localtime(h))}  {n} wallets first funded")
json.dump({"funder":funder,"firstseen":firstseen},open("funders.json","w"))
print("\nsaved funders.json")
