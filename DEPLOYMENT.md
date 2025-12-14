# Deployment Guide — Pi MR-NFT Agent

**OINIO Succession — December 2025**

This guide walks through deploying the Pi MR-NFT + Catalyst Pool system to Pi Mainnet.

## Prerequisites

1. **Pi Mainnet RPC access**
   - Obtain from https://developers.pi.network
   - Add to `.env` as `PI_NODE_RPC`

2. **Private key with PI tokens**
   - For gas fees on Pi Mainnet EVM
   - Never commit this to source control

3. **Development tools**
   ```bash
   python >= 3.11
   pip install -r requirements.txt
   ```

## Quick Start Deployment

### 1. Configure Environment

```bash
# Copy example and add your keys
cp .env.example .env

# Edit .env with your values:
# - PI_NODE_RPC: Your Pi Mainnet RPC endpoint
# - PRIVATE_KEY: Your deployment wallet private key
# - CREATOR_ADDRESS: Your actual Pi Mainnet EVM address (0x followed by 40 hex chars)
#   Example: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6
#   For OINIO: Use the actual Pi Mainnet address controlled by OINIO identity
```

### 2. Deploy Smart Contracts

```bash
# Deploy contracts to Pi Mainnet EVM
cd scripts
./deploy_pi_evm.sh

# Or use forge directly:
forge create --rpc-url $PI_NODE_RPC \
  --private-key $PRIVATE_KEY \
  contracts/ModelRoyaltyNFT.sol:ModelRoyaltyNFT

forge create --rpc-url $PI_NODE_RPC \
  --private-key $PRIVATE_KEY \
  contracts/CatalystPool.sol:CatalystPool
```

**Important:** Save the deployed contract addresses and update your `.env`:
- `MR_NFT_ADDRESS=0x...`
- `CATALYST_POOL_ADDRESS=0x...`

### 3. Seed the First Six Models

```bash
# Deploy the canonical seed models
python scripts/seed_first_six_models.py
```

This will deploy:
1. Mistral-7B (general-purpose, 10% royalty)
2. Llama-2-70B (large reasoning, 20% royalty)
3. Yi-34B (multilingual, 20% royalty)
4. Phi-2 (efficient, 10% royalty)
5. Orca-2-7B (instruction-following, 10% royalty)
6. Neural-Chat-7B (conversational, 10% royalty)

The script will output:
- Deployment transaction hashes
- Royalty calculation examples
- Initial catalyst multiplier status (8×)
- Deployment record saved to `deployment_record.json`

### 4. Verify Deployment

Check your deployment on Pi Mainnet Explorer:
- Navigate to https://explorer.pi.network
- Search for your contract addresses
- Verify transactions and events

## Post-Deployment

### Record Transaction Hashes

Post deployment transaction hashes in the GitHub issue:
```
🚀 Seed Models Deployed

ModelRoyaltyNFT: 0x... (TX: 0x...)
CatalystPool: 0x... (TX: 0x...)

Seed Models:
1. Mistral-7B: TX 0x...
2. Llama-2-70B: TX 0x...
3. Yi-34B: TX 0x...
4. Phi-2: TX 0x...
5. Orca-2-7B: TX 0x...
6. Neural-Chat-7B: TX 0x...

✅ Catalyst flywheel active at 8× multiplier
```

### Start the Agent

```bash
# Run the royalty enforcer agent
python agents/royalty_enforcer.py --demo

# Or start the full FastAPI app
python app/main.py
```

### Monitor the System

```bash
# Check catalyst pool status
python agents/catalyst_watcher.py

# Check model scoring oracle
python agents/model_scoring_oracle.py

# Check handoff coordinator status
python agents/handoff_coordinator.py
```

## Troubleshooting

### "RPC connection failed"
- Verify `PI_NODE_RPC` is set correctly in `.env`
- Check your internet connection
- Ensure Pi Mainnet RPC endpoint is accessible

### "Insufficient gas"
- Ensure your wallet has enough PI tokens for gas fees
- Check current gas prices on Pi Mainnet

### "Contract deployment failed"
- Verify Solidity compiler version (0.8.20)
- Check that OpenZeppelin contracts are installed: `forge install`
- Review contract compilation: `forge build`

## Security Notes

🔒 **Never commit your `.env` file to source control**

The `.gitignore` is already configured to exclude it, but always verify before committing.

🔐 **Secure your private key**

Store it securely using a hardware wallet or encrypted keystore.

⚡ **Test on testnet first**

Before deploying to mainnet, test the entire flow on Pi Testnet.

## OINIO Identity Lock (December 2025)

The following identity is permanently locked for this deployment:

| Platform   | Handle          |
|------------|-----------------|
| X          | @Onenoly11      |
| Telegram   | onenoly11       |
| Discord    | Onenoly11       |
| GitHub     | onenoly1010     |
| Pi Display | OINIO           |

All inference royalties (10-30%) + the full 12M PI Catalyst Pool flow to OINIO-controlled addresses until succession conditions are met (see [HANDOFF.md](./HANDOFF.md)).

## Next Steps

1. ✅ Deploy contracts
2. ✅ Seed first six models
3. 📢 Announce deployment on social channels
4. 🔄 Monitor first inferences
5. 📈 Watch catalyst multiplier taper (8×→1×)
6. 🚀 Open the platform to community developers

---

**Let the sovereign AI economy begin. 🚀**

#PiForge #MRNFT #SovereignAI
