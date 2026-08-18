"""
DriftLens Control Center - Combined Drift Scorer
Combines Jaccard + Cosine for complete drift analysis.

Weights:
    Jaccard: 40% (key presence drift)
    Cosine:  60% (value similarity drift)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Set, List
from app.core.jaccard import JaccardEngine
from app.core.cosine import CosineEngine


class DriftLevel:
    NO_DRIFT = "NO DRIFT"
    LOW      = "LOW DRIFT"
    MODERATE = "MODERATE DRIFT"
    HIGH     = "HIGH DRIFT"
    CRITICAL = "CRITICAL DRIFT"


@dataclass
class CombinedResult:
    """Complete drift analysis combining Jaccard + Cosine."""

    # Jaccard
    jaccard_score: float
    jaccard_percentage: float
    key_drift_percentage: float
    only_in_a: List[str]
    only_in_b: List[str]
    common_keys: List[str]

    # Cosine
    cosine_score: float
    cosine_percentage: float
    value_drift_percentage: float
    value_differences: Dict

    # Combined
    combined_score: float
    combined_percentage: float
    overall_drift_percentage: float
    drift_level: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jaccard": {
                "score": round(self.jaccard_score, 4),
                "similarity_percentage": round(
                    self.jaccard_percentage, 2),
                "key_drift_percentage": round(
                    self.key_drift_percentage, 2),
                "only_in_a": self.only_in_a,
                "only_in_b": self.only_in_b,
                "common_keys": self.common_keys,
            },
            "cosine": {
                "score": round(self.cosine_score, 4),
                "similarity_percentage": round(
                    self.cosine_percentage, 2),
                "value_drift_percentage": round(
                    self.value_drift_percentage, 2),
                "value_differences": self.value_differences,
            },
            "combined": {
                "score": round(self.combined_score, 4),
                "similarity_percentage": round(
                    self.combined_percentage, 2),
                "overall_drift_percentage": round(
                    self.overall_drift_percentage, 2),
                "drift_level": self.drift_level,
                "recommendation": self.recommendation,
            },
        }


class CombinedScorer:
    """Combines Jaccard + Cosine scores."""

    JACCARD_WEIGHT = 0.4
    COSINE_WEIGHT  = 0.6

    @staticmethod
    def classify(drift_pct: float) -> str:
        """Classify drift percentage into level."""
        drift_pct = float(drift_pct)
        if drift_pct == 0:    return DriftLevel.NO_DRIFT
        elif drift_pct <= 20: return DriftLevel.LOW
        elif drift_pct <= 40: return DriftLevel.MODERATE
        elif drift_pct <= 70: return DriftLevel.HIGH
        else:                 return DriftLevel.CRITICAL

    @staticmethod
    def recommend(
        key_drift: float,
        value_drift: float,
        level: str,
    ) -> str:
        """Generate human-readable recommendation."""
        key_drift   = float(key_drift)
        value_drift = float(value_drift)

        if level == DriftLevel.NO_DRIFT:
            return (
                "✅ Environments are identical. "
                "No action needed."
            )
        if key_drift > 30 and value_drift > 30:
            return (
                "🚨 CRITICAL: Both config keys AND values "
                "differ significantly. "
                "Immediate review required!"
            )
        if key_drift > 30 and value_drift <= 30:
            return (
                "⚠️ KEY DRIFT: Missing or extra config keys "
                "detected. Check for missing configurations."
            )
        if key_drift <= 30 and value_drift > 30:
            return (
                "⚠️ VALUE DRIFT: Config keys match but "
                "values differ significantly. Review replicas,"
                " resource limits, and env-specific settings."
            )
        if level == DriftLevel.LOW:
            return (
                "✅ LOW DRIFT: Minor differences detected. "
                "Review before promotion to production."
            )
        if level == DriftLevel.MODERATE:
            return (
                "🟡 MODERATE DRIFT: Noticeable differences. "
                "Ensure all differences are intentional."
            )
        return (
            "🔴 HIGH DRIFT: Significant differences. "
            "Review all config changes carefully."
        )

    @classmethod
    def compare(
        cls,
        config_a: Dict[str, str],
        config_b: Dict[str, str],
    ) -> CombinedResult:
        """Run complete drift analysis."""

        tokens_a = set(config_a.keys())
        tokens_b = set(config_b.keys())

        # ── Run Jaccard ───────────────────────────────────
        jaccard = JaccardEngine.compare(tokens_a, tokens_b)

        # SimilarityResult attributes:
        # jaccard.score              → float (direct)
        # jaccard.drift_percentage() → METHOD (call it!)
        # jaccard.similarity_percentage() → METHOD (call it!)
        # jaccard.only_in_a          → Set[str] (direct)
        # jaccard.only_in_b          → Set[str] (direct)
        # jaccard.common             → Set[str] (direct)

        j_score = float(jaccard.score)
        j_drift = float(jaccard.drift_percentage())
        j_sim   = float(jaccard.similarity_percentage())
        j_only_a = sorted(list(jaccard.only_in_a))
        j_only_b = sorted(list(jaccard.only_in_b))
        j_common = sorted(list(jaccard.common))

        # ── Run Cosine ────────────────────────────────────
        cosine = CosineEngine.compare(config_a, config_b)

        # ── Combined Score ────────────────────────────────
        combined = (
            cls.JACCARD_WEIGHT * j_score +
            cls.COSINE_WEIGHT  * cosine.cosine_score
        )

        overall_drift = (1 - combined) * 100
        level = cls.classify(overall_drift)
        rec = cls.recommend(
            key_drift=j_drift,
            value_drift=cosine.value_drift_percentage,
            level=level,
        )

        return CombinedResult(
            # Jaccard
            jaccard_score=j_score,
            jaccard_percentage=j_sim,
            key_drift_percentage=j_drift,
            only_in_a=j_only_a,
            only_in_b=j_only_b,
            common_keys=j_common,
            # Cosine
            cosine_score=cosine.cosine_score,
            cosine_percentage=cosine.cosine_percentage,
            value_drift_percentage=cosine.value_drift_percentage,
            value_differences=cosine.value_differences,
            # Combined
            combined_score=round(combined, 4),
            combined_percentage=round(combined * 100, 2),
            overall_drift_percentage=round(overall_drift, 2),
            drift_level=level,
            recommendation=rec,
        )
