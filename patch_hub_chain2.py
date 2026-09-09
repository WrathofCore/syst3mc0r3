#!/usr/bin/env python3
import sys, re, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")
M = "HUB_CHAIN_FIX2"
if M in s: print("chain v2: already applied"); sys.exit(0)
NEW = """async function dsSigner(){ /* HUB_CHAIN_FIX2 */
  const eth=window.ethereum, want=DS.chainIdHex.toLowerCase();
  const withTimeout=(pr,ms)=>Promise.race([pr,new Promise((_,rej)=>setTimeout(()=>rej(new Error('chain: timeout')),ms))]);
  const addParams=[{chainId:DS.chainIdHex,chainName:DS.chainName,rpcUrls:[DS.rpcUrl],blockExplorerUrls:[DS.explorer],nativeCurrency:{name:'Ether',symbol:'ETH',decimals:18}}];
  /* network prompt first, straight off the tap, before any other await: mobile wallets drop prompts buried in async chains */
  const now=String(eth.chainId||'').toLowerCase();
  if(now!==want){
    try{ await withTimeout(eth.request({method:'wallet_addEthereumChain',params:addParams}),20000); }
    catch(err){
      if(err && (err.code===4001 || /denied|rejected/i.test(err.message||''))) throw err;
      try{ await withTimeout(eth.request({method:'wallet_switchEthereumChain',params:[{chainId:DS.chainIdHex}]}),20000); }
      catch(e2){ if(e2 && (e2.code===4001 || /denied|rejected/i.test(e2.message||''))) throw e2; throw new Error('chain: cannot switch'); }
    }
  }
  /* provider built AFTER the switch, and told to tolerate changes, so ethers never locks onto the old chain */
  const p=new ethers.providers.Web3Provider(eth,'any');
  await p.send('eth_requestAccounts',[]);
  const id=await eth.request({method:'eth_chainId'}).catch(()=>'');
  if(String(id).toLowerCase()!==want) throw new Error('chain: wrong network');
  return new ethers.Contract(DS.contract,DS_ABI,p.getSigner());
}
"""
pat = re.compile(r"async function dsSigner\(\)\{.*?\n\}\n(?=async function dsTx)", re.S)
assert len(pat.findall(s)) == 1, "dsSigner block not found exactly once"
s = pat.sub(lambda m: NEW, s, count=1)
OM = "out='Wallet didn\\'t switch to Ink · add Ink Mainnet in your wallet, switch to it, reload'"
NM = "out='Wallet didn\\'t switch to Ink · approve the network prompt and tap Mint again'"
if s.count(OM) == 1: s = s.replace(OM, NM, 1)
P.write_text(s, encoding="utf-8"); print("chain v2: patched")
