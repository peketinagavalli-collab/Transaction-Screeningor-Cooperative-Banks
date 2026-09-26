"""
DMGT Module: Propositional Logic Rule Engine.
Evaluates atomic propositions (A, N, Z, G) and compound logical rules for academic transaction screening.
"""

from typing import Dict, List, Tuple, Any

class Rule:
    """Represents a formal propositional logic rule with antecedents and consequential decision."""

    def __init__(self, rule_id: str, name: str, formula_str: str, consequence: str, weight: float = 1.0):
        self.rule_id = rule_id
        self.name = name
        self.formula_str = formula_str
        self.consequence = consequence
        self.weight = weight

    def evaluate(self, props: Dict[str, bool]) -> Tuple[bool, str]:
        """
        Evaluates the truth value of the rule given proposition truth assignments.
        
        Returns:
            Tuple of (rule_triggered, explanation)
        """
        A = props.get("A", False)
        N = props.get("N", False)
        Z = props.get("Z", False)
        G = props.get("G", False)

        result = False
        if self.rule_id == "RULE_1":
            # A ∧ N -> Review Required
            result = A and N
        elif self.rule_id == "RULE_2":
            # A ∧ N ∧ Z -> Suspicious
            result = A and N and Z
        elif self.rule_id == "RULE_3":
            # Z ∧ G -> Review Required
            result = Z and G
        elif self.rule_id == "RULE_4":
            # A ∧ N ∧ Z ∧ G -> Suspicious
            result = A and N and Z and G

        status_str = "TRUE" if result else "FALSE"
        explanation = f"{self.name} [{self.formula_str}]: {status_str}"
        return result, explanation


class RuleEngine:
    """
    Evaluates DMGT propositional logic for incoming transactions.
    
    Propositions:
    A: Amount exceeds threshold
    N: Payee is new
    Z: Statistical anomaly is high
    G: Graph/network behavior is unusual
    """

    def __init__(self, amount_threshold: float = 50000.0, z_threshold: float = 3.0, graph_threshold: float = 0.5):
        self.amount_threshold = float(amount_threshold)
        self.z_threshold = float(z_threshold)
        self.graph_threshold = float(graph_threshold)

        # Standard DMGT academic rules
        self.rules = [
            Rule("RULE_4", "Rule 4 (Highest Priority)", "A ∧ N ∧ Z ∧ G", "Suspicious", weight=100.0),
            Rule("RULE_2", "Rule 2 (Critical Risk)", "A ∧ N ∧ Z", "Suspicious", weight=85.0),
            Rule("RULE_3", "Rule 3 (Structural & Stat Anomaly)", "Z ∧ G", "Review Required", weight=65.0),
            Rule("RULE_1", "Rule 1 (Novel High-Value Transfer)", "A ∧ N", "Review Required", weight=50.0),
        ]

    def evaluate_propositions(
        self,
        amount: float,
        is_new_payee: bool,
        z_score: float,
        graph_risk_indicator: float
    ) -> Dict[str, bool]:
        """Calculates boolean truth values for atomic propositions A, N, Z, G."""
        return {
            "A": bool(amount >= self.amount_threshold),
            "N": bool(is_new_payee),
            "Z": bool(abs(z_score) >= self.z_threshold),
            "G": bool(graph_risk_indicator >= self.graph_threshold)
        }

    def evaluate(
        self,
        amount: float,
        is_new_payee: bool,
        z_score: float,
        graph_risk_indicator: float
    ) -> Dict[str, Any]:
        """
        Executes complete propositional logic evaluation on a transaction.
        
        Returns:
            Dictionary containing truth assignments, triggered rules, rule score, and explanation.
        """
        props = self.evaluate_propositions(amount, is_new_payee, z_score, graph_risk_indicator)
        
        triggered_rules = []
        rule_explanations = []
        highest_decision = "Normal"
        max_rule_weight = 0.0

        for r in self.rules:
            is_active, expl = r.evaluate(props)
            rule_explanations.append(expl)
            if is_active:
                triggered_rules.append(r)
                if r.weight > max_rule_weight:
                    max_rule_weight = r.weight
                
                # Priority: Suspicious > Review Required > Normal
                if r.consequence == "Suspicious":
                    highest_decision = "Suspicious"
                elif r.consequence == "Review Required" and highest_decision != "Suspicious":
                    highest_decision = "Review Required"

        # Baseline score calculation for Rule Risk
        rule_risk_score = max_rule_weight
        if not triggered_rules:
            # Minor score for individual true propositions even if full compound rule didn't fire
            active_count = sum(1 for v in props.values() if v)
            rule_risk_score = min(active_count * 12.0, 35.0)

        # Generate human-readable reasons
        reasons = []
        if props["A"]:
            reasons.append(f"Amount (₹{amount:,.2f}) exceeds threshold (₹{self.amount_threshold:,.2f}) [Proposition A = TRUE]")
        if props["N"]:
            reasons.append("Beneficiary is a newly encountered payee for this account [Proposition N = TRUE]")
        if props["Z"]:
            reasons.append(f"Statistical deviation is high (|z| = {abs(z_score):.2f} >= {self.z_threshold}) [Proposition Z = TRUE]")
        if props["G"]:
            reasons.append(f"Network graph connectivity is unusual (indicator = {graph_risk_indicator:.2f}) [Proposition G = TRUE]")

        for r in triggered_rules:
            reasons.append(f"DMGT Logic Rule Triggered: {r.name} ({r.formula_str}) ⟹ {r.consequence}")

        if not reasons:
            reasons.append("All propositional logic checks evaluated to FALSE (Normal baseline).")

        return {
            "propositions": props,
            "triggered_rules": [r.rule_id for r in triggered_rules],
            "rule_explanations": rule_explanations,
            "rule_decision": highest_decision,
            "rule_score": rule_risk_score,
            "reasons": reasons
        }

    @staticmethod
    def get_truth_table() -> List[Dict[str, Any]]:
        """Generates the full 16-row ($2^4$) truth table for academic DMGT demonstration."""
        rows = []
        for A in [True, False]:
            for N in [True, False]:
                for Z in [True, False]:
                    for G in [True, False]:
                        p = {"A": A, "N": N, "Z": Z, "G": G}
                        r1 = A and N
                        r2 = A and N and Z
                        r3 = Z and G
                        r4 = A and N and Z and G
                        
                        decision = "Normal"
                        if r4 or r2:
                            decision = "Suspicious"
                        elif r3 or r1:
                            decision = "Review Required"

                        rows.append({
                            "A (Amount)": "T" if A else "F",
                            "N (New)": "T" if N else "F",
                            "Z (Z-Score)": "T" if Z else "F",
                            "G (Graph)": "T" if G else "F",
                            "R1 (A∧N)": "T" if r1 else "F",
                            "R2 (A∧N∧Z)": "T" if r2 else "F",
                            "R3 (Z∧G)": "T" if r3 else "F",
                            "R4 (A∧N∧Z∧G)": "T" if r4 else "F",
                            "Consequence": decision
                        })
        return rows
