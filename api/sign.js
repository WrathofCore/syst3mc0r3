// /api/sign — authorizes one DATASTREAMERS mint per wallet.
// Env (Vercel project settings): SIGNER_KEY (private key of the contract's signer wallet),
//                                TURNSTILE_SECRET (Cloudflare Turnstile secret key)
// Body: { wallet, token }  -> { qty, deadline, sig }
const { ethers } = require("ethers");

const CONTRACT = process.env.DS_CONTRACT || "";                 // set after deploy
const CHAIN_ID = 57073;
const RPC = "https://rpc-gel.inkonchain.com";
const PIPS = "0x1c882abe733534910bb334d25ce0f8ce46f0e164";
const TTL = 10 * 60;                                            // signature valid 10 minutes

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ error: "POST" });
  try {
    const { wallet, token } = req.body || {};
    if (!ethers.isAddress(wallet)) return res.status(400).json({ error: "bad wallet" });
    if (!token) return res.status(400).json({ error: "no turnstile token" });
    if (!CONTRACT) return res.status(503).json({ error: "mint not configured" });

    // 1. human check
    const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
    const form = new URLSearchParams({ secret: process.env.TURNSTILE_SECRET, response: token, remoteip: ip });
    const ver = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form }).then(r => r.json());
    if (!ver.success) return res.status(403).json({ error: "turnstile failed" });

    // 2. chain checks: not already minted, pips balance for qty
    const provider = new ethers.JsonRpcProvider(RPC, CHAIN_ID);
    const ds = new ethers.Contract(CONTRACT, ["function minted(address) view returns (bool)", "function mintOpen() view returns (bool)"], provider);
    const pips = new ethers.Contract(PIPS, ["function balanceOf(address) view returns (uint256)"], provider);
    const [already, open, pipBal] = await Promise.all([ds.minted(wallet), ds.mintOpen(), pips.balanceOf(wallet)]);
    if (!open) return res.status(403).json({ error: "mint closed" });
    if (already) return res.status(403).json({ error: "already minted" });
    const qty = pipBal > 0n ? 2 : 1;

    // 3. sign (contract, chainid, wallet, qty, deadline) — must match the contract's hash exactly
    const deadline = Math.floor(Date.now() / 1000) + TTL;
    const hash = ethers.solidityPackedKeccak256(["address", "uint256", "address", "uint256", "uint256"], [CONTRACT, CHAIN_ID, wallet, qty, deadline]);
    const signer = new ethers.Wallet(process.env.SIGNER_KEY);
    const sig = await signer.signMessage(ethers.getBytes(hash));
    return res.status(200).json({ qty, deadline, sig });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: "sign failed" });
  }
};
