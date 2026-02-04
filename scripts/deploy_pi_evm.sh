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
echo ""

# Check if we should skip actual deployment (useful for CI/CD)
if [ "$1" = "--skip-deploy" ]; then
    echo -e "${GREEN}✓ Skipping actual deployment (--skip-deploy flag set)${NC}"
    echo ""
    echo "To deploy manually, run:"
    echo "  forge create --rpc-url \$PI_NODE_RPC --private-key \$PRIVATE_KEY contracts/ModelRoyaltyNFT.sol:ModelRoyaltyNFT"
    echo "  forge create --rpc-url \$PI_NODE_RPC --private-key \$PRIVATE_KEY contracts/CatalystPool.sol:CatalystPool"
    echo ""
    echo -e "${YELLOW}Store the deployment addresses in .env for production use${NC}"
    exit 0
fi

# Deploy ModelRoyaltyNFT
echo -e "${YELLOW}📝 Deploying ModelRoyaltyNFT contract...${NC}"
if command -v forge &> /dev/null; then
    MR_NFT_OUTPUT=$(forge create --rpc-url "$PI_NODE_RPC" --private-key "$PRIVATE_KEY" contracts/ModelRoyaltyNFT.sol:ModelRoyaltyNFT 2>&1)
    MR_NFT_RESULT=$?
    
    if [ $MR_NFT_RESULT -eq 0 ]; then
        MR_NFT_ADDRESS=$(echo "$MR_NFT_OUTPUT" | grep "Deployed to:" | awk '{print $3}')
        echo -e "${GREEN}✓ ModelRoyaltyNFT deployed: $MR_NFT_ADDRESS${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Contract deployment command failed or forge not available${NC}"
        echo -e "${YELLOW}Please deploy contracts manually using the commands above${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Forge not available. Please install Foundry to deploy contracts${NC}"
    echo -e "${YELLOW}Or deploy manually using:${NC}"
    echo "  forge create --rpc-url \$PI_NODE_RPC --private-key \$PRIVATE_KEY contracts/ModelRoyaltyNFT.sol:ModelRoyaltyNFT"
fi

# Deploy CatalystPool
echo -e "${YELLOW}📝 Deploying CatalystPool contract...${NC}"
if command -v forge &> /dev/null; then
    CATALYST_OUTPUT=$(forge create --rpc-url "$PI_NODE_RPC" --private-key "$PRIVATE_KEY" contracts/CatalystPool.sol:CatalystPool 2>&1)
    CATALYST_RESULT=$?
    
    if [ $CATALYST_RESULT -eq 0 ]; then
        CATALYST_ADDRESS=$(echo "$CATALYST_OUTPUT" | grep "Deployed to:" | awk '{print $3}')
        echo -e "${GREEN}✓ CatalystPool deployed: $CATALYST_ADDRESS${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Contract deployment command failed or forge not available${NC}"
        echo -e "${YELLOW}Please deploy contracts manually using the commands above${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Forge not available. Please install Foundry to deploy contracts${NC}"
    echo -e "${YELLOW}Or deploy manually using:${NC}"
    echo "  forge create --rpc-url \$PI_NODE_RPC --private-key \$PRIVATE_KEY contracts/CatalystPool.sol:CatalystPool"
fi

echo ""
echo -e "${GREEN}✓ Deployment process complete${NC}"
echo ""
if [ -n "$MR_NFT_ADDRESS" ] && [ -n "$CATALYST_ADDRESS" ]; then
    echo -e "${YELLOW}📋 Add these addresses to your .env file:${NC}"
    echo "MR_NFT_ADDRESS=$MR_NFT_ADDRESS"
    echo "CATALYST_POOL_ADDRESS=$CATALYST_ADDRESS"
else
    echo -e "${YELLOW}⚠️  Note: Some contracts may not have been deployed${NC}"
    echo -e "${YELLOW}Please check the output above and deploy manually if needed${NC}"
fi
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update .env with deployed contract addresses"
echo "2. Run: python scripts/seed_first_six_models.py"
echo "3. Verify contracts on Pi Network Explorer"
