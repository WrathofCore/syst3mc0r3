#!/usr/bin/env python3
import sys, time, requests
from collections import Counter

RPC      = "https://rpc-gel.inkonchain.com"
CONTRACT = "0xd0bd2E8dD22F65d7d4B696bd9953dC816A82C386".lower()
PIPS     = "0x1c882abe733534910bb334d25ce0f8ce46f0e164".lower()
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO32   = "0x" + "0" * 64
HOURS    = float(sys.argv[1]) if len(sys.argv) > 1 else None

_id = [0]
def rpc(method, params):
    _id[0] += 1
    j = requests.post(RPC, json={"jsonrpc":"2.0","id":_id[0],"method":method,"params":params}, timeout=30).json()
    if "error" in j: raise SystemExit(f"{method}: {j['error']}")
    return j["result"]

def batch(calls):
    out = []
    for i in range(0, len(calls), 80):
        chunk = calls[i:i+80]
        payload = [{"jsonrpc":"2.0","id":j,"method":m,"params":p} for j,(m,p) in enumerate(chunk)]
        res = requests.post(RPC, json=payload, timeout=60).json()
        res.sort(key=lambda x: x["id"])
        out += [x.get("result") for x in res]
    return out

head = int(rpc("eth_blockNumber", []), 16)
print(f"head block {head:,}  scanning...")
lo, hi = 0, head
while lo < hi:
    mid = (lo + hi) // 2
    code = rpc("eth_getCode", [CONTRACT, hex(mid)])
    if code and code != "0x": hi = mid
    else: lo = mid + 1
deploy = lo
print(f"deploy block {deploy:,}")

logs, start = [], deploy
while start <= head:
    end = min(start + 9000, head)
    logs += rpc("eth_getLogs", [{"address":CONTRACT,"fromBlock":hex(start),"toBlock":hex(end),"topics":[TRANSFER,ZERO32]}])
    start = end + 1
print(f"{len(logs):,} mints found")
if not logs: raise SystemExit

blocks = sorted({int(l["blockNumber"], 16) for l in logs})
ts = {}
for b, r in zip(blocks, batch([("eth_getBlockByNumber",[hex(b),False]) for b in blocks])):
    if r: ts[b] = int(r["timestamp"], 16)

now = int(time.time())
rows = sorted((ts.get(int(l["blockNumber"],16),0), int(l["blockNumber"],16), ("0x"+l["topics"][2][-40:]).lower()) for l in logs)
if HOURS:
    rows = [r for r in rows if r[0] >= now - HOURS*3600]
    print(f"last {HOURS}h: {len(rows):,} mints")
    if not rows: raise SystemExit

print("\n--- rate (15 min buckets) ---")
buck = Counter()
for t, *_ in rows: buck[t // 900 * 900] += 1
for k in sorted(buck):
    print(f"{time.strftime('%m-%d %H:%M', time.localtime(k))}  {buck[k]:>4}  {'#'*min(buck[k],60)}")

per = Counter(r[2] for r in rows)
print(f"\n{len(per):,} unique wallets, {sum(per.values()):,} tokens")
print("distribution:", dict(sorted(Counter(per.values()).items())))
multi = [(w,n) for w,n in per.items() if n > 2]
if multi:
    print(f"!! {len(multi)} wallets over the 2 cap:")
    for w,n in sorted(multi, key=lambda x:-x[1])[:15]: print("  ", w, n)

wallets = list(per)
print(f"\nchecking history on {len(wallets):,} wallets...")
nonces = batch([("eth_getTransactionCount",[w,"latest"]) for w in wallets])
bals   = batch([("eth_getBalance",[w,"latest"]) for w in wallets])
pipbal = batch([("eth_call",[{"to":PIPS,"data":"0x70a08231"+w[2:].rjust(64,"0")},"latest"]) for w in wallets])
fresh=aged=holders=zerobal=0
for w,n,b,p in zip(wallets,nonces,bals,pipbal):
    nn = int(n,16) if n else 0
    bb = int(b,16) if b else 0
    pp = int(p,16) if p and p!="0x" else 0
    if nn <= 2: fresh += 1
    else: aged += 1
    if bb == 0: zerobal += 1
    if pp > 0: holders += 1
print(f"  fresh (nonce<=2): {fresh}   aged: {aged}")
print(f"  zero ETH left:    {zerobal}")
print(f"  hold a pip:       {holders}")

gaps = [rows[i][0]-rows[i-1][0] for i in range(1,len(rows))]
if gaps:
    g = sorted(gaps)
    print(f"\ngap between mints: median {g[len(g)//2]}s, min {g[0]}s, max {g[-1]}s")
    print(f"  {sum(1 for x in gaps if x <= 5)} of {len(gaps)} gaps under 5s")
