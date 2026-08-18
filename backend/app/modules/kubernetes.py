"""
DriftLens Control Center - Kubernetes Drift Module
Detects drift between Kubernetes manifests across environments.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from app.core.jaccard import JaccardEngine
from app.core.tokenizer import Tokenizer


class KubernetesDriftDetector:
    """Detects drift between Kubernetes manifests."""

    def __init__(self, samples_root: Optional[str] = None):
        if samples_root is None:
            samples_root = self._find_samples_root()
        self.samples_root = samples_root

    def _find_samples_root(self) -> str:
        """
        Find samples directory in multiple possible locations.
        Works for both local development and Docker deployment.
        """
        # Option 1: Environment variable override
        env_path = os.getenv("SAMPLES_ROOT")
        if env_path and Path(env_path).exists():
            return env_path

        # Option 2: Docker path (/app/samples)
        docker_path = Path("/app/samples/kubernetes")
        if docker_path.exists():
            return str(docker_path)

        # Option 3: Local development (relative to this file)
        # backend/app/modules/kubernetes.py -> project root -> samples
        local_path = Path(__file__).resolve().parents[3] / "samples" / "kubernetes"
        if local_path.exists():
            return str(local_path)

        # Option 4: Current working directory
        cwd_path = Path.cwd() / "samples" / "kubernetes"
        if cwd_path.exists():
            return str(cwd_path)

        # Default fallback
        return str(Path("/app/samples/kubernetes"))

    def load_environment(self, env_name: str) -> Dict[str, str]:
        """Load all YAML manifests for a given environment."""
        env_path = Path(self.samples_root) / env_name
        if not env_path.exists():
            raise FileNotFoundError(
                f"Environment '{env_name}' not found in {self.samples_root}"
            )

        manifests = {}
        for yaml_file in env_path.glob("*.yaml"):
            manifests[yaml_file.name] = yaml_file.read_text()
        for yaml_file in env_path.glob("*.yml"):
            manifests[yaml_file.name] = yaml_file.read_text()
        return manifests

    def compare_content(self, content_a: str, content_b: str, mode: str = "full") -> Dict:
        """Compare two YAML content strings."""
        if mode == "keys_only":
            set_a = Tokenizer.tokenize_yaml_keys_only(content_a)
            set_b = Tokenizer.tokenize_yaml_keys_only(content_b)
        else:
            set_a = Tokenizer.tokenize_yaml(content_a)
            set_b = Tokenizer.tokenize_yaml(content_b)
        result = JaccardEngine.compare(set_a, set_b)
        return result.to_dict()

    def compare_environments(self, env_a: str, env_b: str, mode: str = "full") -> Dict:
        """Compare two entire environments."""
        manifests_a = self.load_environment(env_a)
        manifests_b = self.load_environment(env_b)

        common_files = set(manifests_a.keys()) & set(manifests_b.keys())
        only_in_a = set(manifests_a.keys()) - set(manifests_b.keys())
        only_in_b = set(manifests_b.keys()) - set(manifests_a.keys())

        file_reports = {}
        for filename in sorted(common_files):
            file_reports[filename] = self.compare_content(
                manifests_a[filename], manifests_b[filename], mode
            )

        all_tokens_a = set()
        all_tokens_b = set()
        for content in manifests_a.values():
            all_tokens_a |= Tokenizer.tokenize_yaml(content)
        for content in manifests_b.values():
            all_tokens_b |= Tokenizer.tokenize_yaml(content)

        overall = JaccardEngine.compare(all_tokens_a, all_tokens_b).to_dict()

        return {
            "environment_a": env_a,
            "environment_b": env_b,
            "mode": mode,
            "overall": overall,
            "files_compared": sorted(list(common_files)),
            "files_only_in_a": sorted(list(only_in_a)),
            "files_only_in_b": sorted(list(only_in_b)),
            "per_file_reports": file_reports,
        }

    def list_environments(self) -> List[str]:
        """List all available environments."""
        root = Path(self.samples_root)
        if not root.exists():
            return []
        return sorted([d.name for d in root.iterdir() if d.is_dir()])

    def similarity_matrix_all_envs(self) -> Dict[str, Dict[str, float]]:
        """Generate similarity matrix across all environments."""
        envs = self.list_environments()
        env_tokens = {}
        for env in envs:
            manifests = self.load_environment(env)
            tokens = set()
            for content in manifests.values():
                tokens |= Tokenizer.tokenize_yaml(content)
            env_tokens[env] = tokens
        return JaccardEngine.similarity_matrix(env_tokens)
