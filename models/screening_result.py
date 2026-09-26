"""
ScreeningResult Model (OOPJ Subject Module).
Stores the aggregated multi-modal risk scoring, propositional logic flags, and explainability audit trail.
"""

from typing import Optional, List

class ScreeningResult:
    """Represents the complete academic screening evaluation for a single transaction."""

    ALLOWED_DECISIONS = ["Normal", "Review Required", "Suspicious"]

    def __init__(
        self,
        result_id: Optional[int],
        transaction_id: int,
        z_score: float = 0.0,
        rule_score: float = 0.0,
        graph_score: float = 0.0,
        risk_score: float = 0.0,
        decision: str = "Normal",
        reasons: str = "Routine transaction parameters.",
        screened_at: Optional[str] = None
    ):
        self._result_id = result_id
        self._transaction_id = transaction_id
        self._z_score = float(z_score)
        self._rule_score = float(rule_score)
        self._graph_score = float(graph_score)
        self._risk_score = float(risk_score)
        self.decision = decision
        self._reasons = reasons
        self._screened_at = screened_at

    @property
    def result_id(self) -> Optional[int]:
        return self._result_id

    @result_id.setter
    def result_id(self, val: int):
        self._result_id = val

    @property
    def transaction_id(self) -> int:
        return self._transaction_id

    @property
    def z_score(self) -> float:
        return self._z_score

    @property
    def rule_score(self) -> float:
        return self._rule_score

    @property
    def graph_score(self) -> float:
        return self._graph_score

    @property
    def risk_score(self) -> float:
        return self._risk_score

    @property
    def decision(self) -> str:
        return self._decision

    @decision.setter
    def decision(self, val: str):
        if val not in self.ALLOWED_DECISIONS:
            raise ValueError(f"Invalid decision '{val}'. Allowed: {self.ALLOWED_DECISIONS}")
        self._decision = val

    @property
    def reasons(self) -> str:
        return self._reasons

    @property
    def screened_at(self) -> Optional[str]:
        return self._screened_at

    def reasons_list(self) -> List[str]:
        """Parses semicolon or newline separated reasons into a clean list."""
        if not self._reasons:
            return []
        items = [r.strip() for r in self._reasons.replace(";", "\n").split("\n") if r.strip()]
        return items

    def badge_color(self) -> str:
        """Returns visual badge color for UI rendering."""
        if self._decision == "Normal":
            return "#10B981"  # Emerald Green
        elif self._decision == "Review Required":
            return "#F59E0B"  # Amber Orange
        else:
            return "#EF4444"  # Crimson Red

    def to_dict(self) -> dict:
        """Serializes screening result to dictionary."""
        return {
            "result_id": self._result_id,
            "transaction_id": self._transaction_id,
            "z_score": round(self._z_score, 4),
            "rule_score": round(self._rule_score, 2),
            "graph_score": round(self._graph_score, 2),
            "risk_score": round(self._risk_score, 2),
            "decision": self._decision,
            "reasons": self._reasons,
            "screened_at": self._screened_at
        }

    def __repr__(self) -> str:
        return f"<ScreeningResult txn={self._transaction_id} decision='{self._decision}' risk={self._risk_score:.1f}>"
