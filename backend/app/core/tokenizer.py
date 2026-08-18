"""
DriftLens Control Center - Tokenizer Module

Converts raw content (YAML, JSON, text) into sets of tokens
for Jaccard similarity comparison.
"""

import re
import json
import yaml
from typing import Set, Any, Union


class Tokenizer:
    """
    Tokenization strategies for different content types.

    A "token" is a unit we compare. Examples:
    - For text: individual words
    - For YAML/JSON: flattened key-value paths (e.g., "spec.replicas=3")
    """

    @staticmethod
    def tokenize_words(text: str, lowercase: bool = True) -> Set[str]:
        """
        Tokenize text into a set of words.

        Args:
            text: Input text
            lowercase: Whether to lowercase all tokens

        Returns:
            Set of word tokens
        """
        if not text:
            return set()

        tokens = re.findall(r'\w+', text)

        if lowercase:
            tokens = [t.lower() for t in tokens]

        return set(tokens)

    @staticmethod
    def tokenize_lines(text: str, strip: bool = True) -> Set[str]:
        """
        Tokenize text into a set of lines.

        Args:
            text: Input text
            strip: Whether to strip whitespace from each line

        Returns:
            Set of line tokens
        """
        if not text:
            return set()

        lines = text.splitlines()
        if strip:
            lines = [line.strip() for line in lines if line.strip()]

        return set(lines)

    @staticmethod
    def tokenize_yaml(yaml_content: str) -> Set[str]:
        """
        Tokenize YAML content into flattened key=value paths.

        Example:
            Input:
                spec:
                  replicas: 3
                  image: nginx

            Output:
                {"spec.replicas=3", "spec.image=nginx"}

        Args:
            yaml_content: Raw YAML string

        Returns:
            Set of flattened key=value tokens
        """
        if not yaml_content:
            return set()

        try:
            data = yaml.safe_load(yaml_content)
            if data is None:
                return set()
            return Tokenizer._flatten_to_set(data)
        except yaml.YAMLError as e:
            print(f"[Tokenizer] YAML parse error: {e}")
            return set()

    @staticmethod
    def tokenize_json(json_content: str) -> Set[str]:
        """
        Tokenize JSON content into flattened key=value paths.

        Args:
            json_content: Raw JSON string

        Returns:
            Set of flattened key=value tokens
        """
        if not json_content:
            return set()

        try:
            data = json.loads(json_content)
            return Tokenizer._flatten_to_set(data)
        except json.JSONDecodeError as e:
            print(f"[Tokenizer] JSON parse error: {e}")
            return set()

    @staticmethod
    def tokenize_env(env_content: str) -> Set[str]:
        """
        Tokenize .env style content (KEY=VALUE lines).

        Args:
            env_content: Raw .env content

        Returns:
            Set of KEY=VALUE tokens
        """
        if not env_content:
            return set()

        tokens = set()
        for line in env_content.splitlines():
            line = line.strip()
            # Skip comments and blank lines
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                tokens.add(line)

        return tokens

    @staticmethod
    def _flatten_to_set(
        data: Any,
        parent_key: str = '',
        separator: str = '.'
    ) -> Set[str]:
        """
        Recursively flatten a nested dict/list into a set of key=value strings.

        Args:
            data: Nested data (dict, list, or primitive)
            parent_key: Current key path (used in recursion)
            separator: Separator for nested keys

        Returns:
            Set of "path.to.key=value" strings
        """
        tokens = set()

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else str(key)
                if isinstance(value, (dict, list)):
                    tokens.update(Tokenizer._flatten_to_set(value, new_key, separator))
                else:
                    tokens.add(f"{new_key}={value}")

        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_key = f"{parent_key}[{index}]"
                if isinstance(item, (dict, list)):
                    tokens.update(Tokenizer._flatten_to_set(item, new_key, separator))
                else:
                    tokens.add(f"{new_key}={item}")

        else:
            # Primitive value at root level
            if parent_key:
                tokens.add(f"{parent_key}={data}")

        return tokens

    @staticmethod
    def tokenize_yaml_keys_only(yaml_content: str) -> Set[str]:
        """
        Tokenize YAML into only the key paths (ignore values).

        Useful when you care about STRUCTURE drift, not value drift.

        Args:
            yaml_content: Raw YAML string

        Returns:
            Set of key paths only (no values)
        """
        full_tokens = Tokenizer.tokenize_yaml(yaml_content)
        # Extract just the "key" part before "="
        return {token.split('=')[0] for token in full_tokens}
        