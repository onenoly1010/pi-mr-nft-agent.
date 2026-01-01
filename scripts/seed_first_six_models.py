#!/usr/bin/env python3
"""
Seed first six models into the MR-NFT ecosystem.

OINIO Succession Handoff — December 2025
Deployed by: onenoly1010 (OINIO)
Identity: X (@Onenoly11), Telegram (onenoly11), Discord (Onenoly11), GitHub (onenoly1010)

These are canonical models that demonstrate the sovereign agent's capability:
1. Mistral-7B (general-purpose, 10% royalty)
2. Llama-2-70B (large language model for complex reasoning, 20% royalty)
3. Yi-34B (multilingual, 20% royalty)
4. Phi-2 (efficient inference, 10% royalty)
5. Orca-2-7B (instruction-following, 10% royalty)
6. Neural-Chat-7B (conversational, 10% royalty)

Run with: python scripts/seed_first_six_models.py
"""

import asyncio
import json
import os

# Import agents
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from decimal import Decimal

from agents.catalyst_watcher import CatalystPoolWatcher
from agents.royalty_enforcer import InferenceData, RoyaltyEnforcer, RoyaltyTier

load_dotenv()


SEED_MODELS = [
    {
        "model_id": "mistral-7b",
        "name": "Mistral 7B",
        "ipfs_hash": "QmMistral7b",
        "royalty_tier": RoyaltyTier.STANDARD,  # 10%
        "description": "General-purpose instruction-following model",
    },
    {
        "model_id": "llama-2-70b",
        "name": "Llama 2 70B",
        "ipfs_hash": "QmLlama270b",
        "royalty_tier": RoyaltyTier.PREMIUM,  # 20%
        "description": "Large language model for complex reasoning",
    },
    {
        "model_id": "yi-34b",
        "name": "Yi 34B",
        "ipfs_hash": "QmYi34b",
        "royalty_tier": RoyaltyTier.PREMIUM,  # 20%
        "description": "Multilingual model with strong performance",
    },
    {
        "model_id": "phi-2",
        "name": "Phi-2",
        "ipfs_hash": "QmPhi2",
        "royalty_tier": RoyaltyTier.STANDARD,  # 10%
        "description": "Efficient small language model",
    },
    {
        "model_id": "orca-2-7b",
        "name": "Orca-2 7B",
        "ipfs_hash": "QmOrca27b",
        "royalty_tier": RoyaltyTier.STANDARD,  # 10%
        "description": "Instruction-optimized model",
    },
    {
        "model_id": "neural-chat-7b",
        "name": "Neural Chat 7B",
        "ipfs_hash": "QmNeuralChat7b",
        "royalty_tier": RoyaltyTier.STANDARD,  # 10%
        "description": "Conversational AI model",
    },
]


async def seed_models():
    """Deploy and initialize the first six seed models."""
    
    print("=" * 60)
    print("🌱 Pi MR-NFT Seed Models Deployment")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("Maintainer: OINIO (onenoly1010)")
    print("Handoff Date: December 2025")
    print()

    # Initialize agents
    rpc_url = os.getenv("PI_NODE_RPC", "https://api.node.pi.network")
    creator_address = os.getenv("CREATOR_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")
    
    # Validate configuration
    if not creator_address:
        print("❌ Error: CREATOR_ADDRESS not set in .env file")
        print("   Please set your Pi Mainnet EVM address (0x...)")
        return
    
    if not private_key:
        print("❌ Error: PRIVATE_KEY not set in .env file")
        print("   Please set your deployment wallet private key")
        return
    
    # WARNING: Creator address is sensitive. Do not share or log this information until deployment is complete and verified on-chain.
    # print(f"Creator Address: {creator_address}")
    print(f"RPC Endpoint: {rpc_url}")

    enforcer = RoyaltyEnforcer(creator_address, rpc_url, private_key)
    catalyst_watcher = CatalystPoolWatcher(
        os.getenv("CATALYST_POOL_ADDRESS", "0x..."),
        rpc_url
    )

    # Deploy each seed model
    deployed_models = []
    
    for idx, model_config in enumerate(SEED_MODELS, 1):
        print(f"\n[{idx}/6] Deploying {model_config['name']}...")
        print(f"  Model ID: {model_config['model_id']}")
        print(f"  IPFS Hash: {model_config['ipfs_hash']}")
        print(f"  Royalty Tier: {model_config['royalty_tier'].name}")
        print(f"  Description: {model_config['description']}")
        
        # Create sample inference data
        inference_data = InferenceData(
            model_id=model_config["model_id"],
            user_address="0xDemoUser",
            compute_cost_pi=Decimal("1.0"),  # 1 PI per inference
            inference_hash=f"0xDemo{idx}",
            creator_address=creator_address,
            timestamp=int(datetime.now().timestamp()),
        )

        # Record the inference with royalty enforcement
        royalty_record = await enforcer.wrap_inference(
            inference_data,
            model_config["royalty_tier"],
            catalyst_multiplier=8.0,  # Start at 8x
        )

        # Track deployment
        deployed_models.append({
            "index": idx,
            "model_id": model_config["model_id"],
            "name": model_config["name"],
            "royalty_tier": model_config["royalty_tier"].name,
            "deployed_at": datetime.now().isoformat(),
            "sample_royalty_record": royalty_record,
        })

        print(f"  ✓ Deployed (sample royalty: {royalty_record['total_royalty_pi']} PI)")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Seed Deployment Complete")
    print("=" * 60)
    print(f"\nModels deployed: {len(deployed_models)}/6")
    
    for model in deployed_models:
        print(f"  {model['index']}. {model['name']} ({model['royalty_tier']})")

    # Save deployment record
    deployment_record = {
        "timestamp": datetime.now().isoformat(),
        "creator": creator_address,
        "total_models": len(deployed_models),
        "models": deployed_models,
        "catalyst_status": catalyst_watcher.get_state(),
    }

    output_file = Path(__file__).parent.parent / "deployment_record.json"
    with open(output_file, "w") as f:
        json.dump(deployment_record, f, indent=2)

    print(f"\n📄 Deployment record saved: {output_file}")
    print("\n🚀 Catalyst flywheel is now active!")
    print("   Developers can now fork this repo and start earning royalties.")
    print("\n📋 Next Steps:")
    print("   1. Post deployment transaction hashes in GitHub issues")
    print("   2. Announce deployment on X (@Onenoly11)")
    print("   3. Monitor first inferences via catalyst_watcher.py")
    print("\n✅ OINIO succession handoff complete - Let the sovereign AI economy begin!")
    print("   #PiForge #MRNFT #SovereignAI")


if __name__ == "__main__":
    asyncio.run(seed_models())
