#!/usr/bin/env python3
import sys, pathlib
P = pathlib.Path("index.html"); s = P.read_text(encoding="utf-8")

# ---- 1. phone layout (CSS only, <=760px) ----
M1 = "HUB_MOBILE_FIX"
if M1 not in s:
    css = """
  /* HUB_MOBILE_FIX: phone layout. header row, drawer under header, DS stage below the minted strip */
  @media (max-width:760px){
    .vol{display:none;}
    .meta{max-width:calc(100vw - 150px);}
    .nav{flex-direction:row; flex-wrap:wrap; justify-content:flex-end; align-items:center; gap:6px 14px;}
    #wallet-btn{margin-top:0;}
    .colllist{top:88px; bottom:auto; max-height:calc(100vh - 100px); overflow-y:auto;}
    body.list-open .colllist{bottom:auto;}
    #ds-stage{top:186px; bottom:58vh; align-items:flex-start;}
    #ds-stage .box{width:max(90px, min(150px, 34vmin, calc(42vh - 216px))); margin-bottom:0;}
    #ds-stage .ds-recent{top:88px;}
    #ds-cap{bottom:0 !important;}
  }
"""
    assert s.count("</style>") == 1
    s = s.replace("</style>", css + "</style>", 1); print("phone layout: patched")
else: print("phone layout: already applied")

# ---- 2. chain switch timeout + real chain check ----
M2 = "HUB_CHAIN_FIX"
if M2 not in s:
    OLD = """async function dsSigner(){
  const p=new ethers.providers.Web3Provider(window.ethereum);
  await p.send('eth_requestAccounts',[]);
  try{ await window.ethereum.request({method:'wallet_switchEthereumChain',params:[{chainId:DS.chainIdHex}]}); }
  catch(err){ if(err.code===4902){ await window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:DS.chainIdHex,chainName:DS.chainName,rpcUrls:[DS.rpcUrl],blockExplorerUrls:[DS.explorer],nativeCurrency:{name:'Ether',symbol:'ETH',decimals:18}}]}); } else throw err; }
  return new ethers.Contract(DS.contract,DS_ABI,p.getSigner());
}"""
    NEW = """async function dsSigner(){ /* HUB_CHAIN_FIX */
  const p=new ethers.providers.Web3Provider(window.ethereum);
  await p.send('eth_requestAccounts',[]);
  const want=DS.chainIdHex.toLowerCase();
  const onInk=async()=>{ try{ const id=await window.ethereum.request({method:'eth_chainId'}); return String(id).toLowerCase()===want; }catch(e){ return false; } };
  const withTimeout=(pr,ms)=>Promise.race([pr,new Promise((_,rej)=>setTimeout(()=>rej(new Error('chain: timeout')),ms))]);
  if(!(await onInk())){
    try{ await withTimeout(window.ethereum.request({method:'wallet_switchEthereumChain',params:[{chainId:DS.chainIdHex}]}),25000); }
    catch(err){
      if(err && err.code===4902){
        try{ await withTimeout(window.ethereum.request({method:'wallet_addEthereumChain',params:[{chainId:DS.chainIdHex,chainName:DS.chainName,rpcUrls:[DS.rpcUrl],blockExplorerUrls:[DS.explorer],nativeCurrency:{name:'Ether',symbol:'ETH',decimals:18}}]}),25000); }
        catch(e2){ throw new Error('chain: cannot add'); }
      } else if(err && (err.code===4001 || /denied|rejected/i.test(err.message||''))){ throw err; }
      else throw new Error('chain: cannot switch');
    }
    if(!(await onInk())) throw new Error('chain: wrong network');
  }
  return new ethers.Contract(DS.contract,DS_ABI,p.getSigner());
}"""
    assert s.count(OLD) == 1, "dsSigner block not found"
    s = s.replace(OLD, NEW, 1)
    OM = "    else if(msg.includes('turnstile')) out='Complete the check first';"
    NM = "    else if(msg.startsWith('chain:')) out='Wallet didn\\'t switch to Ink · add Ink Mainnet in your wallet, switch to it, reload';\n" + OM
    assert s.count(OM) == 1, "status line not found"
    s = s.replace(OM, NM, 1); print("chain switch: patched")
else: print("chain switch: already applied")

P.write_text(s, encoding="utf-8")
