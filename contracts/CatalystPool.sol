// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title CatalystPool
 * @dev On-chain Catalyst Pool with 8x→1x taper logic
 * 
 * Manages the 12M PI Catalyst Pool:
 * - First 100,000 inferences: 8x multiplier
 * - Next 900,000 inferences: linear taper 8x→1x
 * - Inferences 1,000,000+: 1x base multiplier
 */
contract CatalystPool is Ownable {
    // Constants
    uint256 public constant POOL_CAPACITY = 1_000_000; // Total inference events
    uint256 public constant TIER_1_LIMIT = 100_000; // Full 8x tier
    uint256 public constant TIER_2_LIMIT = 1_000_000; // Taper tier
    uint256 public constant TIER_1_MULTIPLIER = 8; // 8x in basis points
    uint256 public constant BASE_MULTIPLIER = 1; // 1x in basis points

    // State
    uint256 public totalInferencesProcessed = 0;
    address public catalystToken; // PI token address
    
    uint256 public totalCatalystAllocated = 0;
    uint256 public totalCatalystClaimed = 0;

    mapping(address => uint256) public creatorAllocation;
    mapping(address => uint256) public creatorClaimed;

    event InferenceRecorded(
        address indexed creator,
        uint256 inferenceCost,
        uint256 catalyst_multiplier,
        uint256 totalReward
    );

    event CatalystClaimed(
        address indexed creator,
        uint256 amount
    );

    event MultiplierUpdated(
        uint256 totalProcessed,
        uint256 currentMultiplier
    );

    constructor(address _catalystToken) {
        catalystToken = _catalystToken;
    }

    /**
     * @dev Get current catalyst multiplier based on progress
     * @return multiplier Current multiplier (8 → 1)
     */
    function getCurrentMultiplier() public view returns (uint256) {
        if (totalInferencesProcessed < TIER_1_LIMIT) {
            return TIER_1_MULTIPLIER; // 8x
        } else if (totalInferencesProcessed < TIER_2_LIMIT) {
            // Linear taper: 8 → 1 over 900,000 inferences
            uint256 progressInTier2 = totalInferencesProcessed - TIER_1_LIMIT;
            uint256 tier2Range = TIER_2_LIMIT - TIER_1_LIMIT;
            uint256 decline = (7 * progressInTier2) / tier2Range; // 7x decline
            return TIER_1_MULTIPLIER - decline; // 8 - decline
        } else {
            return BASE_MULTIPLIER; // 1x
        }
    }

    /**
     * @dev Record inference and apply catalyst bonus
     * @param creator Model creator address
     * @param inferenceCost Base inference cost
     */
    function recordInference(
        address creator,
        uint256 inferenceCost
    ) external onlyOwner returns (uint256) {
        require(creator != address(0), "Invalid creator");
        require(totalInferencesProcessed < POOL_CAPACITY, "Pool capacity reached");

        uint256 currentMultiplier = getCurrentMultiplier();
        uint256 catalystBonus = (inferenceCost * currentMultiplier) / BASE_MULTIPLIER;
        uint256 totalReward = inferenceCost + catalystBonus;

        // Update state
        totalInferencesProcessed++;
        creatorAllocation[creator] += totalReward;
        totalCatalystAllocated += catalystBonus;

        emit InferenceRecorded(creator, inferenceCost, currentMultiplier, totalReward);
        emit MultiplierUpdated(totalInferencesProcessed, currentMultiplier);

        return totalReward;
    }

    /**
     * @dev Creator claims their catalyst rewards
     */
    function claimRewards() external returns (uint256) {
        uint256 allocation = creatorAllocation[msg.sender];
        uint256 claimed = creatorClaimed[msg.sender];
        uint256 claimable = allocation - claimed;

        require(claimable > 0, "No rewards to claim");

        creatorClaimed[msg.sender] = allocation;
        totalCatalystClaimed += claimable;

        // Transfer PI tokens to creator
        require(
            IERC20(catalystToken).transfer(msg.sender, claimable),
            "Transfer failed"
        );

        emit CatalystClaimed(msg.sender, claimable);
        return claimable;
    }

    /**
     * @dev Get pool status
     */
    function getPoolStatus() external view returns (
        uint256 capacity,
        uint256 processed,
        uint256 multiplier,
        uint256 remaining,
        uint256 allocated,
        uint256 claimed
    ) {
        return (
            POOL_CAPACITY,
            totalInferencesProcessed,
            getCurrentMultiplier(),
            POOL_CAPACITY - totalInferencesProcessed,
            totalCatalystAllocated,
            totalCatalystClaimed
        );
    }

    /**
     * @dev Get creator's allocation
     */
    function getCreatorStatus(address creator) external view returns (
        uint256 allocated,
        uint256 claimed,
        uint256 claimable
    ) {
        uint256 total = creatorAllocation[creator];
        uint256 claimed_amount = creatorClaimed[creator];
        uint256 claimable_amount = total - claimed_amount;
        
        return (total, claimed_amount, claimable_amount);
    }
}
