"""Tests for the Tokenizer module."""
import pytest
from app.core.tokenizer import Tokenizer


class TestWordTokenization:
    """Test word-level tokenization."""

    def test_simple_words(self):
        text = "hello world foo bar"
        result = Tokenizer.tokenize_words(text)
        assert result == {"hello", "world", "foo", "bar"}

    def test_lowercase_conversion(self):
        text = "Hello WORLD Foo"
        result = Tokenizer.tokenize_words(text)
        assert result == {"hello", "world", "foo"}

    def test_empty_string(self):
        assert Tokenizer.tokenize_words("") == set()

    def test_punctuation_stripped(self):
        text = "hello, world! foo.bar"
        result = Tokenizer.tokenize_words(text)
        assert result == {"hello", "world", "foo", "bar"}


class TestYamlTokenization:
    """Test YAML tokenization."""

    def test_simple_yaml(self):
        yaml_content = """
spec:
  replicas: 3
  image: nginx
"""
        result = Tokenizer.tokenize_yaml(yaml_content)
        assert "spec.replicas=3" in result
        assert "spec.image=nginx" in result

    def test_nested_yaml(self):
        yaml_content = """
metadata:
  name: my-app
  labels:
    env: prod
    tier: backend
"""
        result = Tokenizer.tokenize_yaml(yaml_content)
        assert "metadata.name=my-app" in result
        assert "metadata.labels.env=prod" in result
        assert "metadata.labels.tier=backend" in result

    def test_yaml_with_list(self):
        yaml_content = """
containers:
  - name: web
    port: 80
  - name: api
    port: 8080
"""
        result = Tokenizer.tokenize_yaml(yaml_content)
        assert "containers[0].name=web" in result
        assert "containers[0].port=80" in result
        assert "containers[1].name=api" in result
        assert "containers[1].port=8080" in result

    def test_empty_yaml(self):
        assert Tokenizer.tokenize_yaml("") == set()

    def test_invalid_yaml(self):
        result = Tokenizer.tokenize_yaml("::: invalid :::")
        assert isinstance(result, set)


class TestJsonTokenization:
    """Test JSON tokenization."""

    def test_simple_json(self):
        json_content = '{"debug": true, "port": 8080}'
        result = Tokenizer.tokenize_json(json_content)
        assert "debug=True" in result
        assert "port=8080" in result

    def test_nested_json(self):
        json_content = '{"db": {"host": "localhost", "port": 5432}}'
        result = Tokenizer.tokenize_json(json_content)
        assert "db.host=localhost" in result
        assert "db.port=5432" in result

    def test_invalid_json(self):
        result = Tokenizer.tokenize_json("{invalid}")
        assert isinstance(result, set)


class TestEnvTokenization:
    """Test .env file tokenization."""

    def test_simple_env(self):
        env_content = "DEBUG=true\nPORT=8080\nHOST=localhost"
        result = Tokenizer.tokenize_env(env_content)
        assert "DEBUG=true" in result
        assert "PORT=8080" in result
        assert "HOST=localhost" in result

    def test_env_ignores_comments(self):
        env_content = "# This is a comment\nDEBUG=true\n# Another comment\nPORT=8080"
        result = Tokenizer.tokenize_env(env_content)
        assert len(result) == 2
        assert "DEBUG=true" in result
        assert "PORT=8080" in result

    def test_env_ignores_blank_lines(self):
        env_content = "DEBUG=true\n\n\nPORT=8080\n"
        result = Tokenizer.tokenize_env(env_content)
        assert len(result) == 2


class TestRealWorldYamlDrift:
    """Test with real DevOps drift scenarios."""

    def test_kubernetes_deployment_drift(self):
        """Compare dev vs prod K8s deployments."""
        dev_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  image: nginx:1.20
"""
        prod_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 10
  image: nginx:1.20
"""
        dev_tokens = Tokenizer.tokenize_yaml(dev_yaml)
        prod_tokens = Tokenizer.tokenize_yaml(prod_yaml)

        # Should differ only on replicas
        assert "spec.replicas=2" in dev_tokens
        assert "spec.replicas=10" in prod_tokens
        assert "spec.image=nginx:1.20" in dev_tokens
        assert "spec.image=nginx:1.20" in prod_tokens

    def test_yaml_keys_only_mode(self):
        """Structure-only comparison ignoring values."""
        yaml_content = """
spec:
  replicas: 3
  image: nginx
"""
        result = Tokenizer.tokenize_yaml_keys_only(yaml_content)
        assert "spec.replicas" in result
        assert "spec.image" in result
        # Values should NOT be included
        assert "spec.replicas=3" not in result
