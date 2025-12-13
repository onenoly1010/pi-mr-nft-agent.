"""
Test suite for Pi MR-NFT agents and contracts

Run with: pytest -n auto
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta

# Import agents
from agents.catalyst_watcher import CatalystPoolWatcher
from agents.royalty_enforcer import RoyaltyEnforcer, RoyaltyTier, InferenceData
from agents.model_scoring_oracle import ModelScoringOracle
from agents.handoff_coordinator import HandoffCoordinator, MaintainerState


class TestCatalystWatcher:
    """Test Catalyst Pool watcher."""

    @pytest.fixture
    def watcher(self):
        return CatalystPoolWatcher("0xCatalyst", "http://localhost:8545")

    @pytest.mark.asyncio
    async def test_get_multiplier_tier_1(self, watcher):
        """Test 8x multiplier in first tier."""
        watcher.total_inferences = 50_000
        multiplier = await watcher.get_current_multiplier()
        assert multiplier == 8.0

    @pytest.mark.asyncio
    async def test_get_multiplier_tier_2_taper(self, watcher):
        """Test linear taper in second tier."""
        watcher.total_inferences = 550_000  # Midpoint of taper
        multiplier = await watcher.get_current_multiplier()
        assert 1.0 < multiplier < 8.0

    @pytest.mark.asyncio
    async def test_get_multiplier_final(self, watcher):
        """Test 1x multiplier at capacity."""
        watcher.total_inferences = 1_000_000
        multiplier = await watcher.get_current_multiplier()
        assert multiplier == 1.0


class TestRoyaltyEnforcer:
    """Test royalty enforcement logic."""

    @pytest.fixture
    def enforcer(self):
        return RoyaltyEnforcer("0xCreator", "http://localhost:8545")

    def test_calculate_royalty_standard(self, enforcer):
        """Test standard 10% royalty."""
        base, total = enforcer.calculate_royalty(
            Decimal("100"),
            RoyaltyTier.STANDARD,
            catalyst_multiplier=8.0
        )
        assert base == Decimal("10")
        assert total == Decimal("80")  # 10 * 8.0

    def test_calculate_royalty_premium(self, enforcer):
        """Test premium 20% royalty."""
        base, total = enforcer.calculate_royalty(
            Decimal("100"),
            RoyaltyTier.PREMIUM,
            catalyst_multiplier=4.0
        )
        assert base == Decimal("20")
        assert total == Decimal("80")  # 20 * 4.0

    def test_calculate_royalty_exclusive(self, enforcer):
        """Test exclusive 30% royalty."""
        base, total = enforcer.calculate_royalty(
            Decimal("100"),
            RoyaltyTier.EXCLUSIVE,
            catalyst_multiplier=1.0
        )
        assert base == Decimal("30")
        assert total == Decimal("30")  # 30 * 1.0

    @pytest.mark.asyncio
    async def test_wrap_inference(self, enforcer):
        """Test inference wrapping and royalty record."""
        data = InferenceData(
            model_id="test-model",
            user_address="0xUser",
            compute_cost_pi=Decimal("10"),
            inference_hash="0xHash",
            creator_address="0xCreator",
            timestamp=int(datetime.now().timestamp())
        )

        record = await enforcer.wrap_inference(
            data,
            RoyaltyTier.STANDARD,
            catalyst_multiplier=8.0
        )

        assert record["model_id"] == "test-model"
        assert record["base_royalty_pi"] == 1.0  # 10% of 10
        assert record["total_royalty_pi"] == 8.0  # 1 * 8


class TestModelScoringOracle:
    """Test model quality scoring."""

    @pytest.fixture
    def oracle(self):
        return ModelScoringOracle()

    def test_record_single_inference(self, oracle):
        """Test recording a single inference."""
        oracle.record_inference(
            model_id="test-model",
            success=True,
            latency_ms=250,
            output_quality=90.0
        )

        score = oracle.get_score("test-model")
        assert score is not None
        assert score.quality_score == 90.0
        assert score.success_rate == 1.0

    def test_record_multiple_inferences(self, oracle):
        """Test aggregating multiple inferences."""
        for i in range(10):
            oracle.record_inference(
                model_id="test-model",
                success=i < 9,  # 9 success, 1 failure
                latency_ms=250 + (i * 10),
                output_quality=85 + (i % 5)
            )

        score = oracle.get_score("test-model")
        assert score.success_rate == 0.9
        assert 85 <= score.quality_score <= 90

    def test_catalyst_eligibility(self, oracle):
        """Test catalyst bonus eligibility."""
        # Ineligible: too few inferences
        oracle.record_inference(
            "new-model",
            True,
            250,
            90.0
        )
        assert not oracle.is_eligible_for_catalyst("new-model")

        # Build reputation
        for _ in range(20):
            oracle.record_inference("new-model", True, 250, 85.0)

        score = oracle.get_score("new-model")
        assert score.success_rate >= 0.95
        assert oracle.is_eligible_for_catalyst("new-model")


class TestHandoffCoordinator:
    """Test sovereign handoff protocol."""

    @pytest.fixture
    def coordinator(self):
        maintainer = MaintainerState(
            github_handle="test-maintainer",
            evm_address="0xMaintainer"
        )
        return HandoffCoordinator(
            maintainer,
            ["0xSigner1", "0xSigner2", "0xSigner3", "0xSigner4", "0xSigner5"]
        )

    def test_update_reputation(self, coordinator):
        """Test reputation score updates."""
        initial = coordinator.current_maintainer.reputation_score
        coordinator.update_reputation(10.0)
        assert coordinator.current_maintainer.reputation_score == initial + 10.0

    def test_reputation_bounds(self, coordinator):
        """Test reputation stays in 0-100 range."""
        coordinator.update_reputation(100.0)  # Try to go beyond 100
        assert coordinator.current_maintainer.reputation_score == 100.0

        coordinator.update_reputation(-200.0)  # Try to go below 0
        assert coordinator.current_maintainer.reputation_score == 0.0

    def test_succession_eligibility(self, coordinator):
        """Test handoff condition verification."""
        assert not coordinator.check_succession_eligibility()

        # Meet all conditions
        coordinator.current_maintainer.reputation_score = 95.0
        coordinator.current_maintainer.inferences_processed = 10_500
        coordinator.current_maintainer.days_since_deployment = 35

        assert coordinator.check_succession_eligibility()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
