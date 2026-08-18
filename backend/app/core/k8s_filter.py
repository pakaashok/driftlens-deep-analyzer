"""
DriftLens - Kubernetes Noise Filter

Removes K8s internal fields that are not useful
for drift detection comparison.

These fields are always different between environments
but don't represent actual configuration drift:
- metadata.uid (auto-generated)
- metadata.creationTimestamp (auto-generated)
- metadata.resourceVersion (auto-generated)
- status.* (runtime state)
- spec.clusterIP (auto-assigned)
"""

from typing import Dict, Set

# Keys to exclude from drift comparison
NOISE_KEYS: Set[str] = {
    # K8s internal identifiers
    "metadata.uid",
    "metadata.resourceVersion",
    "metadata.creationTimestamp",
    "metadata.generation",
    "metadata.managedFields",

    # Runtime status (not config)
    "status.replicas",
    "status.readyReplicas",
    "status.availableReplicas",
    "status.updatedReplicas",
    "status.observedGeneration",
    "status.terminatingReplicas",

    # Auto-assigned networking
    "spec.clusterIP",
    "spec.clusterIPs[0]",

    # Last applied config (too verbose)
    "metadata.annotations.kubectl.kubernetes.io/"
    "last-applied-configuration",
    "metadata.annotations.deployment.kubernetes.io/"
    "revision",
}

# Key prefixes to exclude
NOISE_PREFIXES: tuple = (
    "status.conditions",
    "status.condition",
    "metadata.managedFields",
)


def is_noise(key: str) -> bool:
    """Check if a key is K8s noise."""
    if key in NOISE_KEYS:
        return True
    for prefix in NOISE_PREFIXES:
        if key.startswith(prefix):
            return True
    return False


def filter_config(
    config: Dict[str, str]
) -> Dict[str, str]:
    """Remove noise keys from config dict."""
    return {
        k: v for k, v in config.items()
        if not is_noise(k)
    }


def get_meaningful_differences(
    value_differences: Dict
) -> Dict:
    """Filter noise from value differences."""
    return {
        k: v for k, v in value_differences.items()
        if not is_noise(k)
    }
