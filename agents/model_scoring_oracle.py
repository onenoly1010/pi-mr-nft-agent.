"""
Model Scoring Oracle Agent

Evaluates model quality + inference reputation:
- Tracks inference success/failure rates
- Calculates quality score (0-100)
- Determines eligibility for catalyst bonuses
- Feeds into handoff reputation system
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model status in the ecosystem."""
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    PREMIUM = "premium"
    FLAGGED = "flagged"
    RETIRED = "retired"


@dataclass
class InferenceMetric:
    """Single inference quality metric."""
    timestamp: datetime
    success: bool
    latency_ms: float
    output_quality_score: float  # 0-100
    user_rating: Optional[float] = None


@dataclass
class ModelScore:
    """Aggregated model scoring data."""
    model_id: str
    total_inferences: int = 0
    success_rate: float = 0.0
    quality_score: float = 0.0
    avg_latency_ms: float = 0.0
    status: ModelStatus = ModelStatus.ONBOARDING
    metrics: List[InferenceMetric] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)


class ModelScoringOracle:
    """Evaluates model quality and reputation."""

    def __init__(self, lookback_days: int = 30):
        """
        Initialize oracle.
        
        Args:
            lookback_days: Days to consider for scoring
        """
        self.lookback_days = lookback_days
        self.models: Dict[str, ModelScore] = {}

    def record_inference(
        self,
        model_id: str,
        success: bool,
        latency_ms: float,
        output_quality: float,
        user_rating: Optional[float] = None
    ) -> None:
        """
        Record a single inference for scoring.
        
        Args:
            model_id: Model identifier
            success: Inference completed successfully
            latency_ms: Response latency in milliseconds
            output_quality: Quality score (0-100)
            user_rating: Optional user rating (0-5 stars)
        """
        if model_id not in self.models:
            self.models[model_id] = ModelScore(model_id=model_id)

        metric = InferenceMetric(
            timestamp=datetime.now(),
            success=success,
            latency_ms=latency_ms,
            output_quality_score=output_quality,
            user_rating=user_rating
        )

        self.models[model_id].metrics.append(metric)
        self._update_score(model_id)

    def _update_score(self, model_id: str) -> None:
        """Recalculate aggregate score for model."""
        model_score = self.models[model_id]
        
        # Filter metrics within lookback window
        cutoff = datetime.now() - timedelta(days=self.lookback_days)
        recent_metrics = [m for m in model_score.metrics if m.timestamp > cutoff]

        if not recent_metrics:
            return

        # Calculate success rate
        successes = sum(1 for m in recent_metrics if m.success)
        model_score.success_rate = successes / len(recent_metrics)

        # Calculate average quality
        qualities = [m.output_quality_score for m in recent_metrics]
        model_score.quality_score = sum(qualities) / len(qualities)

        # Calculate average latency
        latencies = [m.latency_ms for m in recent_metrics]
        model_score.avg_latency_ms = sum(latencies) / len(latencies)

        # Update total inferences
        model_score.total_inferences = len(model_score.metrics)

        # Determine status
        self._update_status(model_id)
        model_score.last_update = datetime.now()

        logger.info(
            f"Model {model_id} scored: {model_score.quality_score:.1f}/100 "
            f"({model_score.success_rate*100:.1f}% success, "
            f"{model_score.avg_latency_ms:.0f}ms avg)"
        )

    def _update_status(self, model_id: str) -> None:
        """Update model status based on metrics."""
        score = self.models[model_id]

        if score.total_inferences < 10:
            score.status = ModelStatus.ONBOARDING
        elif score.quality_score >= 85 and score.success_rate >= 0.98:
            score.status = ModelStatus.PREMIUM
        elif score.success_rate < 0.90:
            score.status = ModelStatus.FLAGGED
        else:
            score.status = ModelStatus.ACTIVE

    def get_score(self, model_id: str) -> Optional[ModelScore]:
        """Retrieve model score."""
        return self.models.get(model_id)

    def is_eligible_for_catalyst(self, model_id: str) -> bool:
        """Check if model is eligible for catalyst bonus."""
        score = self.get_score(model_id)
        if not score:
            return False
        
        return (
            score.status in (ModelStatus.ACTIVE, ModelStatus.PREMIUM) and
            score.quality_score >= 75 and
            score.success_rate >= 0.95
        )

    def get_all_scores(self) -> Dict[str, ModelScore]:
        """Retrieve all model scores."""
        return self.models.copy()


if __name__ == "__main__":
    oracle = ModelScoringOracle()

    # Demo scoring
    for i in range(15):
        oracle.record_inference(
            model_id="mistral-7b",
            success=i < 14,  # One failure
            latency_ms=250 + (i % 50),
            output_quality=85 + (i % 10),
            user_rating=4.5 if i % 3 != 0 else 4.0
        )

    score = oracle.get_score("mistral-7b")
    print(f"Model score: {score}")
    print(f"Catalyst eligible: {oracle.is_eligible_for_catalyst('mistral-7b')}")
