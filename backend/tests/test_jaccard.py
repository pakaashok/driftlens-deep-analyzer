"""Tests for the Jaccard engine."""
import pytest
from app.core.jaccard import JaccardEngine, SimilarityResult


class TestJaccardSimilarity:
    """Test suite for basic Jaccard similarity."""

    def test_identical_sets(self):
        """Two identical sets should have similarity 1.0."""
        set_a = {"apple", "banana", "cherry"}
        set_b = {"apple", "banana", "cherry"}
        assert JaccardEngine.similarity(set_a, set_b) == 1.0

    def test_completely_different_sets(self):
        """Two disjoint sets should have similarity 0.0."""
        set_a = {"apple", "banana"}
        set_b = {"cherry", "date"}
        assert JaccardEngine.similarity(set_a, set_b) == 0.0

    def test_partial_overlap(self):
        """Test partial overlap between sets."""
        set_a = {"apple", "banana", "cherry"}
        set_b = {"banana", "cherry", "date"}
        # Intersection: {banana, cherry} = 2
        # Union: {apple, banana, cherry, date} = 4
        # Jaccard = 2/4 = 0.5
        assert JaccardEngine.similarity(set_a, set_b) == 0.5

    def test_both_empty_sets(self):
        """Two empty sets should be considered identical (1.0)."""
        assert JaccardEngine.similarity(set(), set()) == 1.0

    def test_one_empty_set(self):
        """Comparison with empty set should return 0.0."""
        set_a = {"apple", "banana"}
        assert JaccardEngine.similarity(set_a, set()) == 0.0
        assert JaccardEngine.similarity(set(), set_a) == 0.0

    def test_subset_relationship(self):
        """Test when one set is a subset of another."""
        set_a = {"apple", "banana"}
        set_b = {"apple", "banana", "cherry", "date"}
        # Intersection: 2, Union: 4, Jaccard = 0.5
        assert JaccardEngine.similarity(set_a, set_b) == 0.5


class TestJaccardCompare:
    """Test suite for detailed comparison."""

    def test_compare_returns_similarity_result(self):
        """compare() should return a SimilarityResult object."""
        set_a = {"apple", "banana"}
        set_b = {"banana", "cherry"}
        result = JaccardEngine.compare(set_a, set_b)
        assert isinstance(result, SimilarityResult)

    def test_compare_detailed_output(self):
        """Verify all fields of SimilarityResult."""
        set_a = {"apple", "banana", "cherry"}
        set_b = {"banana", "cherry", "date"}
        result = JaccardEngine.compare(set_a, set_b)

        assert result.score == 0.5
        assert result.intersection_size == 2
        assert result.union_size == 4
        assert result.only_in_a == {"apple"}
        assert result.only_in_b == {"date"}
        assert result.common == {"banana", "cherry"}

    def test_drift_percentage(self):
        """Drift % should be 100 - similarity %."""
        set_a = {"a", "b", "c", "d"}
        set_b = {"a", "b"}
        # Similarity = 2/4 = 0.5 -> Drift = 50%
        result = JaccardEngine.compare(set_a, set_b)
        assert result.drift_percentage() == 50.0

    def test_drift_detected_flag(self):
        """Verify drift detection threshold logic."""
        set_a = {"a", "b", "c", "d"}
        set_b = {"a", "b", "c", "e"}
        result = JaccardEngine.compare(set_a, set_b)
        # Similarity = 3/5 = 0.6, drift detected (< 0.95)
        assert result.is_drift_detected() is True

    def test_no_drift_when_identical(self):
        """When sets are identical, no drift should be detected."""
        set_a = {"a", "b", "c"}
        set_b = {"a", "b", "c"}
        result = JaccardEngine.compare(set_a, set_b)
        assert result.is_drift_detected() is False

    def test_to_dict_serialization(self):
        """to_dict() should return JSON-serializable data."""
        set_a = {"apple", "banana"}
        set_b = {"banana", "cherry"}
        result = JaccardEngine.compare(set_a, set_b)
        d = result.to_dict()

        assert "similarity_score" in d
        assert "drift_percentage" in d
        assert "only_in_a" in d
        assert "only_in_b" in d
        assert "common" in d
        assert isinstance(d["only_in_a"], list)  # Sorted list, not set


class TestJaccardMultiple:
    """Test suite for multi-set comparisons."""

    def test_compare_multiple(self):
        """Test pairwise comparison of multiple sets."""
        sets = {
            "dev": {"a", "b", "c"},
            "staging": {"a", "b", "d"},
            "prod": {"a", "b", "c"},
        }
        results = JaccardEngine.compare_multiple(sets)

        # Should have 3 pairs: (dev,staging), (dev,prod), (staging,prod)
        assert len(results) == 3

        # Results are sorted by score descending
        # dev vs prod = 1.0 (identical) should be first
        assert results[0][2] == 1.0

    def test_similarity_matrix(self):
        """Test full similarity matrix generation."""
        sets = {
            "dev": {"a", "b"},
            "prod": {"a", "c"},
        }
        matrix = JaccardEngine.similarity_matrix(sets)

        # Diagonal should be 1.0
        assert matrix["dev"]["dev"] == 1.0
        assert matrix["prod"]["prod"] == 1.0

        # Cross values: intersection={a}=1, union={a,b,c}=3 -> 1/3
        assert matrix["dev"]["prod"] == round(1 / 3, 4)
        assert matrix["prod"]["dev"] == round(1 / 3, 4)

    def test_matrix_is_symmetric(self):
        """Similarity matrix should be symmetric."""
        sets = {
            "a": {"x", "y"},
            "b": {"y", "z"},
            "c": {"x", "z"},
        }
        matrix = JaccardEngine.similarity_matrix(sets)
        for name_a in sets:
            for name_b in sets:
                assert matrix[name_a][name_b] == matrix[name_b][name_a]


class TestRealWorldScenarios:
    """Real DevOps scenarios to validate practical usefulness."""

    def test_kubernetes_deployment_drift(self):
        """Simulate K8s deployment drift between dev and prod."""
        dev_manifest = {
            "spec.replicas=3",
            "spec.image=nginx:1.20",
            "spec.port=80",
            "metadata.namespace=default",
        }
        prod_manifest = {
            "spec.replicas=10",  # Drift: different replicas
            "spec.image=nginx:1.20",
            "spec.port=80",
            "metadata.namespace=default",
            "spec.nodeSelector=prod",  # Drift: extra field in prod
        }
        result = JaccardEngine.compare(dev_manifest, prod_manifest)

        # 3 common, 6 union -> 0.5 similarity, 50% drift
        assert result.score == 0.5
        assert result.drift_percentage() == 50.0
        assert "spec.replicas=3" in result.only_in_a
        assert "spec.nodeSelector=prod" in result.only_in_b

    def test_identical_config_no_drift(self):
        """Two identical configs should show zero drift."""
        config = {"debug=false", "port=8080", "host=localhost"}
        result = JaccardEngine.compare(config, config)
        assert result.drift_percentage() == 0.0
        assert result.is_drift_detected() is False
        