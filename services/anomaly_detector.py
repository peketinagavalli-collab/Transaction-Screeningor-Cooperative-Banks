"""
Python Statistical Anomaly Detection Module.
Calculates historical sample Mean (μ), Standard Deviation (σ), and Z-score (z) with full mathematical explainability.
"""

import math
from typing import List, Dict, Any, Union

class AnomalyDetector:
    """
    Computes statistical metrics and evaluates Gaussian standard score (Z-Score) anomalies.
    
    Formulas:
      1. Mean: μ = (Σx) / n
      2. Standard Deviation: σ = sqrt( Σ(x - μ)² / n )
      3. Z-Score: z = (x - μ) / σ
    """

    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = float(z_threshold)

    def calculate_stats(self, historical_amounts: List[float]) -> Dict[str, float]:
        """
        Calculates descriptive statistics (mean, variance, standard deviation) from historical data.
        """
        if not historical_amounts:
            # Baseline fallback for accounts with zero history
            return {
                "count": 0,
                "sum": 0.0,
                "mean": 20000.0,
                "sum_sq_diff": 0.0,
                "variance": 100000000.0,
                "std_dev": 10000.0
            }

        n = len(historical_amounts)
        total_sum = sum(historical_amounts)
        mean = total_sum / n

        # Sum of squared deviations: Σ(x - μ)²
        sq_diffs = [(x - mean) ** 2 for x in historical_amounts]
        sum_sq_diff = sum(sq_diffs)
        
        # Population / Sample standard deviation (academic formula uses division by n)
        variance = sum_sq_diff / n if n > 0 else 0.0
        std_dev = math.sqrt(variance)

        # Minimum standard deviation floor to avoid division by zero
        if std_dev < 1.0:
            std_dev = max(mean * 0.1, 1000.0)

        return {
            "count": n,
            "sum": total_sum,
            "mean": mean,
            "sum_sq_diff": sum_sq_diff,
            "variance": variance,
            "std_dev": std_dev
        }

    def compute_z_score(
        self,
        current_amount: float,
        historical_amounts: List[float]
    ) -> Dict[str, Any]:
        """
        Calculates Z-score and produces a detailed step-by-step audit trail.
        
        Returns:
            Dictionary with exact arithmetic substitutions and LaTeX formulas.
        """
        stats = self.calculate_stats(historical_amounts)
        mu = stats["mean"]
        sigma = stats["std_dev"]
        n = stats["count"]
        x = float(current_amount)

        # z = (x - μ) / σ
        deviation = x - mu
        z_score = deviation / sigma if sigma > 0 else 0.0
        abs_z = abs(z_score)
        is_anomaly = abs_z >= self.z_threshold

        # Statistical risk score mapped to 0 - 100
        # If z <= 1: risk ~ 10-25; if z == 3: risk ~ 70; if z >= 5: risk ~ 95-100
        statistical_risk = min(max((abs_z / max(self.z_threshold, 1.0)) * 60.0, 5.0), 100.0)

        # Step-by-step arithmetic representation
        step_by_step = {
            "n": n,
            "sum_x": stats["sum"],
            "mean_val": mu,
            "std_dev_val": sigma,
            "current_amount": x,
            "raw_deviation": deviation,
            "z_score": z_score,
            "abs_z_score": abs_z,
            "z_threshold": self.z_threshold,
            "is_anomaly": is_anomaly,
            "formula_mean": r"\mu = \frac{\sum_{i=1}^n x_i}{n}",
            "calc_mean_str": f"\\mu = \\frac{{{stats['sum']:,.2f}}}{{{n}}} = ₹{mu:,.2f}" if n > 0 else f"\\mu = ₹{mu:,.2f} \\text{{ (Default baseline)}}",
            "formula_std": r"\sigma = \sqrt{\frac{\sum_{i=1}^n (x_i - \mu)^2}{n}}",
            "calc_std_str": f"\\sigma = \\sqrt{{\\frac{{{stats['sum_sq_diff']:,.2f}}}{{{n}}}}} = ₹{sigma:,.2f}" if n > 0 else f"\\sigma = ₹{sigma:,.2f}",
            "formula_z": r"z = \frac{x - \mu}{\sigma}",
            "calc_z_str": f"z = \\frac{{{x:,.2f} - {mu:,.2f}}}{{{sigma:,.2f}}} = \\frac{{{deviation:,.2f}}}{{{sigma:,.2f}}} = {z_score:.2f}",
            "decision_str": f"|z| = {abs_z:.2f} \\ge {self.z_threshold:.2f} \\implies \\text{{STATISTICAL ANOMALY = TRUE}}" if is_anomaly else f"|z| = {abs_z:.2f} < {self.z_threshold:.2f} \\implies \\text{{STATISTICAL ANOMALY = FALSE}}"
        }

        return {
            "z_score": z_score,
            "is_anomaly": is_anomaly,
            "statistical_risk": statistical_risk,
            "mean": mu,
            "std_dev": sigma,
            "step_by_step": step_by_step
        }
