"""
Tests for Cosine Similarity Engine
"""
import pytest
from app.core.cosine import CosineEngine, CosineResult


class TestCosineEngine:

    def test_identical_configs(self):
        """Identical configs = score 1.0"""
        config = {"replicas": "3", "cpu": "100m"}
        result = CosineEngine.compare(config, config)
        assert result.cosine_score == 1.0
        assert result.value_drift_percentage == 0.0

    def test_empty_configs(self):
        """Empty configs = score 1.0"""
        result = CosineEngine.compare({}, {})
        assert result.cosine_score == 1.0

    def test_different_replicas_single(self):
        """Single key: different values shows drift"""
        config_a = {"replicas": "1"}
        config_b = {"replicas": "10"}
        result = CosineEngine.compare(config_a, config_b)
        # Single dimension uses ratio similarity
        assert result.cosine_score < 1.0
        assert result.value_drift_percentage > 0
        assert "replicas" in result.value_differences

    def test_different_replicas_multi(self):
        """Multi key: different values shows drift"""
        config_a = {"replicas": "1",  "timeout": "30"}
        config_b = {"replicas": "10", "timeout": "120"}
        result = CosineEngine.compare(config_a, config_b)
        assert result.cosine_score < 1.0
        assert result.value_drift_percentage > 0

    def test_boolean_true(self):
        """Boolean true extraction"""
        assert CosineEngine.extract_numeric("true") == 1.0
        assert CosineEngine.extract_numeric("yes") == 1.0
        assert CosineEngine.extract_numeric("enabled") == 1.0

    def test_boolean_false(self):
        """Boolean false extraction"""
        assert CosineEngine.extract_numeric("false") == 0.0
        assert CosineEngine.extract_numeric("no") == 0.0
        assert CosineEngine.extract_numeric("disabled") == 0.0

    def test_log_level_ordering(self):
        """Debug < info < warn < error"""
        debug = CosineEngine.extract_numeric("debug")
        info  = CosineEngine.extract_numeric("info")
        warn  = CosineEngine.extract_numeric("warn")
        error = CosineEngine.extract_numeric("error")
        assert debug < info < warn < error

    def test_memory_units(self):
        """Memory unit conversion: Ki < Mi < Gi"""
        ki = CosineEngine.extract_numeric("1ki")
        mi = CosineEngine.extract_numeric("1mi")
        gi = CosineEngine.extract_numeric("1gi")
        assert ki < mi < gi

    def test_cpu_millicores(self):
        """CPU millicores: 100m = 100.0"""
        result = CosineEngine.extract_numeric("100m")
        assert result == 100.0

    def test_no_common_keys(self):
        """No common keys = score 0.0"""
        config_a = {"key_a": "val_a"}
        config_b = {"key_b": "val_b"}
        result = CosineEngine.compare(config_a, config_b)
        assert result.cosine_score == 0.0

    def test_value_direction_increased(self):
        """Detect increased direction"""
        config_a = {"replicas": "1"}
        config_b = {"replicas": "5"}
        result = CosineEngine.compare(config_a, config_b)
        assert result.value_differences[
            "replicas"]["direction"] == "increased"

    def test_value_direction_decreased(self):
        """Detect decreased direction"""
        config_a = {"replicas": "5"}
        config_b = {"replicas": "1"}
        result = CosineEngine.compare(config_a, config_b)
        assert result.value_differences[
            "replicas"]["direction"] == "decreased"

    def test_partial_common_keys(self):
        """Only common keys compared"""
        config_a = {
            "replicas": "1",
            "image": "nginx:1.20",
            "only_a": "value"
        }
        config_b = {
            "replicas": "5",
            "image": "nginx:1.25",
            "only_b": "value"
        }
        result = CosineEngine.compare(config_a, config_b)
        assert len(result.common_keys) == 2
        assert "only_a" not in result.common_keys
        assert "only_b" not in result.common_keys

    def test_change_percentage(self):
        """Change percentage calculated correctly"""
        config_a = {"replicas": "1"}
        config_b = {"replicas": "2"}
        result = CosineEngine.compare(config_a, config_b)
        assert result.value_differences[
            "replicas"]["change_pct"] == 100.0


class TestCombinedScorer:

    def test_identical_environments(self):
        """Identical configs = NO DRIFT"""
        from app.core.combined import CombinedScorer
        config = {
            "replicas": "3",
            "image": "nginx:1.20",
            "log_level": "info",
        }
        result = CombinedScorer.compare(config, config)
        assert result.combined_score == 1.0
        assert result.drift_level == "NO DRIFT"

    def test_different_environments(self):
        """Different configs = drift detected"""
        from app.core.combined import CombinedScorer
        config_a = {
            "replicas": "1",
            "log_level": "debug",
            "cache": "false",
        }
        config_b = {
            "replicas": "10",
            "log_level": "warn",
            "cache": "true",
        }
        result = CombinedScorer.compare(config_a, config_b)
        assert result.combined_score < 1.0
        assert result.drift_level != "NO DRIFT"

    def test_recommendation_generated(self):
        """Recommendation always generated"""
        from app.core.combined import CombinedScorer
        config_a = {"replicas": "1"}
        config_b = {"replicas": "10"}
        result = CombinedScorer.compare(config_a, config_b)
        assert result.recommendation != ""
        assert len(result.recommendation) > 0

    def test_drift_levels(self):
        """Drift level classification"""
        from app.core.combined import CombinedScorer
        assert CombinedScorer.classify(0)  == "NO DRIFT"
        assert CombinedScorer.classify(10) == "LOW DRIFT"
        assert CombinedScorer.classify(30) == "MODERATE DRIFT"
        assert CombinedScorer.classify(60) == "HIGH DRIFT"
        assert CombinedScorer.classify(80) == "CRITICAL DRIFT"

    def test_combined_score_range(self):
        """Combined score always between 0 and 1"""
        from app.core.combined import CombinedScorer
        config_a = {"replicas": "1", "log": "debug"}
        config_b = {"replicas": "10", "log": "warn"}
        result = CombinedScorer.compare(config_a, config_b)
        assert 0.0 <= result.combined_score <= 1.0

    def test_jaccard_score_present(self):
        """Jaccard score in result"""
        from app.core.combined import CombinedScorer
        config_a = {"key1": "val1", "key2": "val2"}
        config_b = {"key1": "val1", "key3": "val3"}
        result = CombinedScorer.compare(config_a, config_b)
        assert 0.0 <= result.jaccard_score <= 1.0

    def test_cosine_score_present(self):
        """Cosine score in result"""
        from app.core.combined import CombinedScorer
        config_a = {"replicas": "1"}
        config_b = {"replicas": "5"}
        result = CombinedScorer.compare(config_a, config_b)
        assert 0.0 <= result.cosine_score <= 1.0
