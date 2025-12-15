"""
Handoff Coordinator Agent

Sovereign succession state machine using LangGraph:
- Tracks maintainer reputation score (0-100)
- Validates handoff conditions
- Routes royalties to current maintainer
- Orchestrates successor verification + multisig approval
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

logger = logging.getLogger(__name__)


class HandoffPhase(Enum):
    """Handoff process phases."""
    ACTIVE_CUSTODIAN = "active_custodian"
    SUCCESSION_ELIGIBLE = "succession_eligible"
    VERIFICATION_PENDING = "verification_pending"
    MULTISIG_VOTE = "multisig_vote"
    TRANSITION_COMPLETE = "transition_complete"


@dataclass
class MaintainerState:
    """Current maintainer state."""
    github_handle: str
    evm_address: str
    reputation_score: float = 50.0  # 0-100
    inferences_processed: int = 0
    days_since_deployment: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    phase: HandoffPhase = HandoffPhase.ACTIVE_CUSTODIAN


@dataclass
class HandoffProposal:
    """Successor handoff proposal."""
    successor_github: str
    successor_evm_address: str
    fork_repo_link: str
    inferences_achieved: int
    days_active: int
    quality_score: float
    submitted_at: datetime
    votes_received: Dict[str, bool] = field(default_factory=dict)  # signer → approved


class HandoffCoordinator:
    """Orchestrates sovereign agent succession."""

    def __init__(self, current_maintainer: MaintainerState, multisig_signers: List[str]):
        """
        Initialize handoff coordinator.
        
        Args:
            current_maintainer: Initial maintainer state
            multisig_signers: List of 3-of-5 multisig signer addresses
        """
        self.current_maintainer = current_maintainer
        self.multisig_signers = multisig_signers
        self.proposals: Dict[str, HandoffProposal] = {}
        self.vote_threshold = 3  # 3-of-5 required
        
        logger.info(f"Handoff coordinator initialized for {current_maintainer.github_handle}")

    def update_reputation(self, delta: float) -> float:
        """
        Update maintainer reputation score.
        
        Args:
            delta: Score change (+/- 0-10 points typical)
        
        Returns:
            New reputation score
        """
        self.current_maintainer.reputation_score = max(
            0, min(100, self.current_maintainer.reputation_score + delta)
        )
        logger.info(
            f"Reputation updated: {self.current_maintainer.github_handle} = "
            f"{self.current_maintainer.reputation_score:.1f}/100"
        )
        return self.current_maintainer.reputation_score

    def check_succession_eligibility(self) -> bool:
        """
        Check if current maintainer is eligible for succession.
        
        Returns:
            True if maintainer has met handoff conditions
        """
        eligible = (
            self.current_maintainer.reputation_score >= 95 and
            self.current_maintainer.inferences_processed >= 10_000 and
            self.current_maintainer.days_since_deployment >= 30
        )
        
        logger.info(
            f"Succession eligibility check: {eligible} "
            f"(reputation: {self.current_maintainer.reputation_score:.1f}/100, "
            f"inferences: {self.current_maintainer.inferences_processed}/10000, "
            f"days: {self.current_maintainer.days_since_deployment}/30)"
        )
        
        if eligible:
            self.current_maintainer.phase = HandoffPhase.SUCCESSION_ELIGIBLE
        
        return eligible

    def submit_handoff_proposal(self, proposal: HandoffProposal) -> str:
        """
        Submit successor handoff proposal.
        
        Args:
            proposal: Handoff proposal from successor
        
        Returns:
            Proposal ID
        """
        proposal_id = f"handoff_{proposal.successor_github}_{int(datetime.now().timestamp())}"
        self.proposals[proposal_id] = proposal
        
        # Validate proposal
        if not self._validate_proposal(proposal):
            logger.warning(f"Proposal {proposal_id} failed validation")
            return proposal_id
        
        self.current_maintainer.phase = HandoffPhase.VERIFICATION_PENDING
        logger.info(f"Handoff proposal submitted: {proposal_id}")
        
        return proposal_id

    def _validate_proposal(self, proposal: HandoffProposal) -> bool:
        """Validate handoff proposal meets conditions."""
        valid = (
            proposal.inferences_achieved >= 10_000 and
            proposal.days_active >= 30 and
            proposal.quality_score >= 75.0 and
            len(proposal.fork_repo_link) > 0
        )
        
        if not valid:
            logger.warning(
                f"Proposal validation failed: inferences={proposal.inferences_achieved}/10000, "
                f"days={proposal.days_active}/30, quality={proposal.quality_score}/100"
            )
        
        return valid

    def vote_on_proposal(self, proposal_id: str, signer: str, approve: bool) -> None:
        """
        Record multisig vote on proposal.
        
        Args:
            proposal_id: Proposal to vote on
            signer: Multisig signer address
            approve: Vote to approve
        """
        if proposal_id not in self.proposals:
            logger.error(f"Proposal {proposal_id} not found")
            return
        
        if signer not in self.multisig_signers:
            logger.error(f"Signer {signer} not in multisig")
            return
        
        proposal = self.proposals[proposal_id]
        proposal.votes_received[signer] = approve
        
        logger.info(f"Vote recorded: {signer} → {'APPROVED' if approve else 'REJECTED'}")
        
        self._check_vote_threshold(proposal_id)

    def _check_vote_threshold(self, proposal_id: str) -> None:
        """Check if proposal has reached vote threshold."""
        proposal = self.proposals[proposal_id]
        approvals = sum(1 for v in proposal.votes_received.values() if v)
        
        if approvals >= self.vote_threshold:
            logger.info(f"Proposal {proposal_id} APPROVED by multisig ({approvals}/{self.vote_threshold})")
            self._execute_handoff(proposal)
        elif len(proposal.votes_received) == len(self.multisig_signers):
            logger.error(f"Proposal {proposal_id} REJECTED by multisig ({approvals}/{self.vote_threshold})")

    def _execute_handoff(self, proposal: HandoffProposal) -> None:
        """Execute successful handoff to successor."""
        new_maintainer = MaintainerState(
            github_handle=proposal.successor_github,
            evm_address=proposal.successor_evm_address,
            phase=HandoffPhase.TRANSITION_COMPLETE
        )
        
        self.current_maintainer = new_maintainer
        logger.critical(
            f"🚀 HANDOFF EXECUTED: {proposal.successor_github} is now maintainer! "
            f"All future royalties route to {proposal.successor_evm_address}"
        )

    def get_state(self) -> Dict:
        """Return coordinator state."""
        return {
            "current_maintainer": {
                "github": self.current_maintainer.github_handle,
                "evm_address": self.current_maintainer.evm_address,
                "reputation": self.current_maintainer.reputation_score,
                "phase": self.current_maintainer.phase.value,
            },
            "proposals_pending": len(self.proposals),
            "multisig_signers_count": len(self.multisig_signers),
        }


if __name__ == "__main__":
    # Demo handoff coordinator
    initial_maintainer = MaintainerState(
        github_handle="onenoly1010",
        evm_address="0xOINIO"
    )
    
    coordinator = HandoffCoordinator(
        initial_maintainer,
        ["0xSigner1", "0xSigner2", "0xSigner3", "0xSigner4", "0xSigner5"]
    )
    
    # Simulate reputation building
    coordinator.update_reputation(45.0)  # Start at 95
    coordinator.current_maintainer.inferences_processed = 10_500
    coordinator.current_maintainer.days_since_deployment = 35
    
    print(f"Succession eligible: {coordinator.check_succession_eligibility()}")
    print(f"Coordinator state: {coordinator.get_state()}")
