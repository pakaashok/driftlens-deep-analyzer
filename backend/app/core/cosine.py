"""
DriftLens Control Center - Cosine Similarity Engine

Measures similarity between configuration VALUES.
While Jaccard checks if keys EXIST,
Cosine checks HOW SIMILAR the VALUES ARE.

Formula:
    cos(θ) = (A · B) / (|A| × |B|)

Score:
    1.0 = identical values
    0.0 = completely different values

Single dimension fix:
    For single values, we use ratio-based similarity
    instead of cosine (which always gives 1.0 for
    single-dimension vectors)
"""

import math
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class CosineResult:
    """Result of a Cosine similarity comparison."""
    cosine_score: float
    cosine_percentage: float
    value_drift_percentage: float
    common_keys: List[str] = field(default_factory=list)
    vector_a: Dict[str, float] = field(default_factory=dict)
    vector_b: Dict[str, float] = field(default_factory=dict)
    value_differences: Dict[str, Dict] = field(
        default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cosine_score": round(self.cosine_score, 4),
            "cosine_percentage": round(
                self.cosine_percentage, 2),
            "value_drift_percentage": round(
                self.value_drift_percentage, 2),
            "common_keys_count": len(self.common_keys),
            "common_keys": self.common_keys,
            "value_differences": self.value_differences,
        }


class CosineEngine:
    """Cosine Similarity Engine for config value comparison."""

    LOG_LEVELS = {
        "trace": 1.0, "debug": 2.0, "info": 3.0,
        "warn": 4.0, "warning": 4.0, "error": 5.0,
        "critical": 6.0, "fatal": 7.0,
    }

    MEMORY_UNITS = {
        "ki": 1024, "mi": 1024 ** 2, "gi": 1024 ** 3,
        "k": 1000, "g": 1000 ** 3,
    }

    @classmethod
    def extract_numeric(cls, value: str) -> float:
        """
        Extract numeric value from config string.
        Order matters: CPU check BEFORE memory check!
        """
        if not isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0

        v = value.strip().lower()

        # Boolean
        if v in ("true", "yes", "enabled", "on", "1"):
            return 1.0
        if v in ("false", "no", "disabled", "off", "0"):
            return 0.0

        # Log levels
        if v in cls.LOG_LEVELS:
            return cls.LOG_LEVELS[v]

        # Pure number first
        try:
            return float(v)
        except ValueError:
            pass

        # CPU millicores: MUST check before memory
        # "100m" = 100 millicores (NOT megabytes!)
        cpu = re.match(r"^([\d.]+)m$", v)
        if cpu:
            return float(cpu.group(1))

        # Memory units (Ki, Mi, Gi only - NOT m!)
        mem = re.match(r"^([\d.]+)(ki|mi|gi|k|g)$", v)
        if mem:
            num = float(mem.group(1))
            unit = mem.group(2)
            return num * cls.MEMORY_UNITS.get(unit, 1)

        # Version strings (nginx:1.20 → 120)
        version = re.search(r"(\d+)\.(\d+)", v)
        if version:
            major = int(version.group(1))
            minor = int(version.group(2))
            return float(f"{major}{minor:02d}")

        # String → consistent numeric hash
        return float(abs(hash(v)) % 10000)

    @classmethod
    def value_similarity(
        cls,
        val_a: float,
        val_b: float
    ) -> float:
        """
        Calculate similarity between two numeric values.

        Uses ratio-based approach which works for
        both single and multi-dimensional comparisons.

        Returns 0.0 to 1.0
        """
        if val_a == val_b:
            return 1.0

        # Both zero
        if val_a == 0 and val_b == 0:
            return 1.0

        # One is zero
        if val_a == 0 or val_b == 0:
            return 0.0

        # Ratio similarity: min/max
        ratio = min(val_a, val_b) / max(val_a, val_b)
        return ratio

    @classmethod
    def build_vectors(
        cls,
        config_a: Dict[str, str],
        config_b: Dict[str, str],
    ) -> Tuple:
        """Build numeric vectors from config dicts."""
        common_keys = sorted(
            set(config_a.keys()) & set(config_b.keys())
        )

        vec_a, vec_b = [], []
        num_a_dict, num_b_dict = {}, {}

        for key in common_keys:
            na = cls.extract_numeric(config_a[key])
            nb = cls.extract_numeric(config_b[key])
            vec_a.append(na)
            vec_b.append(nb)
            num_a_dict[key] = na
            num_b_dict[key] = nb

        return vec_a, vec_b, common_keys, \
               num_a_dict, num_b_dict

    @staticmethod
    def dot_product(a: List[float], b: List[float]) -> float:
        """Calculate dot product: A · B"""
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def magnitude(vec: List[float]) -> float:
        """Calculate vector magnitude: |A|"""
        return math.sqrt(sum(x ** 2 for x in vec))

    @classmethod
    def calculate_cosine(
        cls,
        vec_a: List[float],
        vec_b: List[float]
    ) -> float:
        """
        Calculate cosine similarity for multi-dim vectors.
        For single dimension, use ratio instead.
        """
        if not vec_a or not vec_b:
            return 1.0

        # Single dimension: use ratio similarity
        # Cosine of single vectors is always 1.0
        # regardless of magnitude difference!
        if len(vec_a) == 1:
            return cls.value_similarity(vec_a[0], vec_b[0])

        mag_a = cls.magnitude(vec_a)
        mag_b = cls.magnitude(vec_b)

        if mag_a == 0 and mag_b == 0:
            return 1.0
        if mag_a == 0 or mag_b == 0:
            return 0.0

        dot = cls.dot_product(vec_a, vec_b)
        score = dot / (mag_a * mag_b)

        # For multi-dim, blend cosine with avg ratio
        # This handles cases where directions match
        # but magnitudes differ greatly
        avg_ratio = sum(
            cls.value_similarity(a, b)
            for a, b in zip(vec_a, vec_b)
        ) / len(vec_a)

        # 60% cosine direction + 40% magnitude ratio
        blended = 0.6 * max(0.0, min(1.0, score)) + \
                  0.4 * avg_ratio

        return max(0.0, min(1.0, blended))

    @classmethod
    def compare(
        cls,
        config_a: Dict[str, str],
        config_b: Dict[str, str],
    ) -> CosineResult:
        """
        Compare two config dicts using cosine similarity.
        """
        if not config_a and not config_b:
            return CosineResult(
                cosine_score=1.0,
                cosine_percentage=100.0,
                value_drift_percentage=0.0,
            )

        vec_a, vec_b, common_keys, num_a, num_b = \
            cls.build_vectors(config_a, config_b)

        if not common_keys:
            return CosineResult(
                cosine_score=0.0,
                cosine_percentage=0.0,
                value_drift_percentage=100.0,
                common_keys=[],
            )

        score = cls.calculate_cosine(vec_a, vec_b)

        # Find value differences
        differences = {}
        for key in common_keys:
            val_a = config_a.get(key, "")
            val_b = config_b.get(key, "")

            if val_a != val_b:
                na = num_a[key]
                nb = num_b[key]

                if na != 0:
                    pct = abs(nb - na) / abs(na) * 100
                else:
                    pct = 100.0 if nb != 0 else 0.0

                differences[key] = {
                    "value_a": val_a,
                    "value_b": val_b,
                    "numeric_a": round(na, 4),
                    "numeric_b": round(nb, 4),
                    "change_pct": round(pct, 2),
                    "direction": "increased" if nb > na
                                else "decreased"
                                if nb < na else "changed",
                }

        return CosineResult(
            cosine_score=round(score, 4),
            cosine_percentage=round(score * 100, 2),
            value_drift_percentage=round(
                (1 - score) * 100, 2),
            common_keys=common_keys,
            vector_a=num_a,
            vector_b=num_b,
            value_differences=differences,
        )
