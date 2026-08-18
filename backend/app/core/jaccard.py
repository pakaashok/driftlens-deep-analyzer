"""
DriftLens Control Center - Core Jaccard Similarity Engine

Implements Jaccard similarity for drift detection.
Formula: J(A, B) = |A ∩ B| / |A ∪ B|

Similarity Score:
- 1.0 = Identical (no drift)
- 0.0 = Completely different (100% drift)
"""

from typing import Set, Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class SimilarityResult:
    """Result of a Jaccard similarity comparison."""
    score: float
    intersection_size: int
    union_size: int
    only_in_a: Set[str] = field(default_factory=set)
    only_in_b: Set[str] = field(default_factory=set)
    common: Set[str] = field(default_factory=set)

    def drift_percentage(self) -> float:
        """Return drift as percentage (100% - similarity)."""
        return round((1 - self.score) * 100, 2)

    def similarity_percentage(self) -> float:
        """Return similarity as percentage."""
        return round(self.score * 100, 2)

    def is_drift_detected(self, threshold: float = 0.95) -> bool:
        """Check if drift exceeds acceptable threshold."""
        return self.score < threshold

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "similarity_score": round(self.score, 4),
            "similarity_percentage": self.similarity_percentage(),
            "drift_percentage": self.drift_percentage(),
            "intersection_size": self.intersection_size,
            "union_size": self.union_size,
            "only_in_a": sorted(list(self.only_in_a)),
            "only_in_b": sorted(list(self.only_in_b)),
            "common": sorted(list(self.common)),
            "drift_detected": self.is_drift_detected(),
        }


class JaccardEngine:
    """
    Core Jaccard similarity engine for drift detection.

    Usage:
        engine = JaccardEngine()
        result = engine.compare(set_a, set_b)
        print(f"Similarity: {result.score}")
        print(f"Drift: {result.drift_percentage()}%")
    """

    @staticmethod
    def similarity(set_a: Set[str], set_b: Set[str]) -> float:
        """
        Calculate raw Jaccard similarity between two sets.

        Args:
            set_a: First set
            set_b: Second set

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not set_a and not set_b:
            return 1.0  # Two empty sets are considered identical

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        if union == 0:
            return 0.0

        return intersection / union

    @staticmethod
    def compare(set_a: Set[str], set_b: Set[str]) -> SimilarityResult:
        """
        Perform detailed comparison between two sets.

        Args:
            set_a: First set (e.g., dev environment)
            set_b: Second set (e.g., prod environment)

        Returns:
            SimilarityResult with detailed drift information
        """
        intersection = set_a & set_b
        union = set_a | set_b
        only_in_a = set_a - set_b
        only_in_b = set_b - set_a

        score = len(intersection) / len(union) if union else 1.0

        return SimilarityResult(
            score=score,
            intersection_size=len(intersection),
            union_size=len(union),
            only_in_a=only_in_a,
            only_in_b=only_in_b,
            common=intersection,
        )

    @staticmethod
    def compare_multiple(
        sets: Dict[str, Set[str]]
    ) -> List[Tuple[str, str, float]]:
        """
        Compare multiple sets pairwise.

        Args:
            sets: Dict mapping names to sets (e.g., {"dev": set1, "prod": set2})

        Returns:
            List of (name_a, name_b, similarity_score) tuples
        """
        names = list(sets.keys())
        results = []

        for i, name_a in enumerate(names):
            for name_b in names[i + 1:]:
                score = JaccardEngine.similarity(sets[name_a], sets[name_b])
                results.append((name_a, name_b, round(score, 4)))

        # Sort by score descending (most similar first)
        results.sort(key=lambda x: x[2], reverse=True)
        return results

    @staticmethod
    def similarity_matrix(
        sets: Dict[str, Set[str]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Generate full similarity matrix for heatmap visualization.

        Args:
            sets: Dict mapping names to sets

        Returns:
            2D dict: matrix[name_a][name_b] = similarity_score
        """
        names = list(sets.keys())
        matrix = {}

        for name_a in names:
            matrix[name_a] = {}
            for name_b in names:
                if name_a == name_b:
                    matrix[name_a][name_b] = 1.0
                else:
                    matrix[name_a][name_b] = round(
                        JaccardEngine.similarity(sets[name_a], sets[name_b]), 4
                    )

        return matrix
        