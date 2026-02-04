# Pi MR-NFT Sovereign Inference Agent

The first fully autonomous agent that (1) monitors the Catalyst Pool, (2) enforces 10–30% inference royalties, (3) routes payments on Pi Mainnet, and (4) hands itself off to the next maintainer when conditions are met.

**Live on Pi Mainnet:** https://explorer.pi.network/address/0x...

## One-line pitch
Turn any GGUF model into an MR-NFT and earn 20% royalty + up to 8× catalyst bonus on every inference forever.

## Quickstart (literally 3 commands)

```bash
git clone https://github.com/onenoly1010/pi-mr-nft-agent.git
cd pi-mr-nft-agent
cp .env.example .env          # ← add your PI_NODE_RPC and PRIVATE_KEY
pip install -r requirements.txt
python agents/royalty_enforcer.py --demo
```

## Core agents included
- `catalyst_watcher.py` → real-time 8×→1× multiplier tracker
- `royalty_enforcer.py` → exact wrapper logic from the locked spec
- `model_scoring_oracle.py` → inference quality + reputation scoring
- `handoff_coordinator.py` → LangGraph state machine that hands control to new maintainer when reputation score > 95

## Contracts included
- `ModelRoyaltyNFT.sol` → ERC-721 MR-NFT with royalty enforcement
- `CatalystPool.sol` → On-chain multiplier + taper logic (8×→1×)

## Handoff Protocol
See [HANDOFF.md](./HANDOFF.md) for the exact checklist the next maintainer must complete before the agent will route royalties to their address.

## Production Deployment
See [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) for step-by-step guides on deploying to Railway, Render, Heroku, or Docker.

Quick deploy options:
- **Railway.app**: Zero-config deployment with `railway.json`
- **Render.com**: Free tier with `render.yaml` auto-detection
- **Heroku**: One-click deploy with `Procfile`
- **Docker**: Self-hosted with `docker-compose.yml`

### Current Handoff Status ✅
- **Maintainer:** @onenoly1010 (OINIO)
- **Status:** ✅ **HANDOFF COMPLETE** — Fully autonomous (December 2025)
- **Identity locked:** X (@Onenoly11), Telegram (onenoly11), Discord (Onenoly11), GitHub (onenoly1010), Pi Display (OINIO)
- **Economic rights:** 100% of inference royalties + full 12M PI Catalyst Pool routed to OINIO-controlled addresses
- **Succession:** Open to any developer who meets the conditions in [HANDOFF.md](./HANDOFF.md)

## License
MIT — fork, ship, earn forever.

---

**#PiForge #MRNFT #SovereignAI**