#!/bin/bash
# Deploy Pi MR-NFT + Catalyst Pool to Pi Mainnet EVM

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Pi MR-NFT Deployment Script${NC}"
echo "================================"

# Load environment
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Copy .env.example and add your keys.${NC}"
    exit 1
fi

source .env

# Validate env vars
if [ -z "$PI_NODE_RPC" ]; then
    echo -e "${YELLOW}Error: PI_NODE_RPC not set${NC}"
    exit 1
fi

if [ -z "$PRIVATE_KEY" ]; then
    echo -e "${YELLOW}Error: PRIVATE_KEY not set${NC}"
    exit 1
fi

# Dry run mode
if [ "$1" = "--dry-run" ]; then
    echo -e "${GREEN}✓ Dry-run mode (no actual deployment)${NC}"
    echo "  RPC: $PI_NODE_RPC"
    echo "  Deployer: $(echo $PRIVATE_KEY | cut -c1-6)..."
    exit 0
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
if ! command -v forge &> /dev/null; then
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
fi

echo -e "${YELLOW}📦 Installing Solidity dependencies...${NC}"
forge install openzeppelin/openzeppelin-contracts --no-commit

# Compile contracts
echo -e "${YELLOW}🔨 Compiling contracts...${NC}"
forge build

# Deploy
echo -e "${YELLOW}🚀 Deploying to Pi Mainnet...${NC}"

# Note: This is a placeholder - actual deployment would use forge/hardhat/etc
echo -e "${GREEN}✓ Deployment configuration ready${NC}"
echo ""
echo "To deploy, run:"
echo "  forge create --rpc-url $PI_NODE_RPC --private-key $PRIVATE_KEY contracts/ModelRoyaltyNFT.sol:ModelRoyaltyNFT"
echo "  forge create --rpc-url $PI_NODE_RPC --private-key $PRIVATE_KEY contracts/CatalystPool.sol:CatalystPool"
echo ""
echo -e "${YELLOW}Store the deployment addresses in .env for production use${NC}"
