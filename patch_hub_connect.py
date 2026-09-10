#!/usr/bin/env python3
import sys, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")
if "HUB_CONNECT_FIX" in s: print("connect: already applied"); sys.exit(0)
OLD = """  btn.textContent='Connecting…';
  try{
    const p=new ethers.providers.Web3Provider(window.ethereum);
    const [addr]=await p.send('eth_requestAccounts',[]);
    btn.textContent=addr.slice(0,6)+'…'+addr.slice(-4);
    try{ await window.ethereum.request({method:'wallet_switchEthereumChain',params:[{chainId:V3.chainIdHex}]}); }
    catch(err){ if(err.code===4902){ await window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:V3.chainIdHex,chainName:V3.chainName,rpcUrls:[V3.rpcUrl],blockExplorerUrls:[V3.explorer],nativeCurrency:{name:'Ether',symbol:'ETH',decimals:18}}]}); } }
    const bal=(await new ethers.Contract(V3.contract,ABI,p).balanceOf(addr)).toNumber();"""
NEW = """  btn.textContent='Connecting…';
  try{ /* HUB_CONNECT_FIX: network prompt first off the tap, provider built after the switch */
    const eth=window.ethereum, want=V3.chainIdHex.toLowerCase();
    if(String(eth.chainId||'').toLowerCase()!==want){
      try{ await eth.request({method:'wallet_addEthereumChain',params:[{chainId:V3.chainIdHex,chainName:V3.chainName,rpcUrls:[V3.rpcUrl],blockExplorerUrls:[V3.explorer],nativeCurrency:{name:'Ether',symbol:'ETH',decimals:18}}]}); }
      catch(err){ if(err && (err.code===4001 || /denied|rejected/i.test(err.message||''))) throw err;
        try{ await eth.request({method:'wallet_switchEthereumChain',params:[{chainId:V3.chainIdHex}]}); }catch(e2){} }
    }
    const p=new ethers.providers.Web3Provider(eth,'any');
    let accs=await eth.request({method:'eth_accounts'}).catch(()=>[]);
    if(!accs||!accs.length) accs=await p.send('eth_requestAccounts',[]);
    const addr=accs[0];
    btn.textContent=addr.slice(0,6)+'…'+addr.slice(-4);
    const bal=(await new ethers.Contract(V3.contract,ABI,p).balanceOf(addr)).toNumber();"""
assert s.count(OLD) == 1, "connectWallet block not found exactly once"
s = s.replace(OLD, NEW, 1)
P.write_text(s, encoding="utf-8"); print("connect: patched")
