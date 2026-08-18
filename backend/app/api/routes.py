"""
DriftLens Deep Analyzer - API Routes
Deep drift detection using Jaccard + Cosine algorithms.
"""

from fastapi import APIRouter, HTTPException, Query
from app.modules.kubernetes import KubernetesDriftDetector
from app.core.cosine import CosineEngine
from app.core.combined import CombinedScorer
from app.core.tokenizer import Tokenizer
from app.core.k8s_filter import filter_config

router = APIRouter(prefix="/api", tags=["Deep Drift Analysis"])
k8s_detector = KubernetesDriftDetector()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "DriftLens Deep Analyzer",
        "version": "0.1.0",
        "algorithms": ["jaccard", "cosine", "combined"],
    }


@router.get("/environments")
def list_environments():
    envs = k8s_detector.list_environments()
    return {"environments": envs, "count": len(envs)}


@router.get("/analyze")
def analyze(
    env_a: str = Query(..., description="First environment"),
    env_b: str = Query(..., description="Second environment"),
    filter_noise: bool = Query(
        True, description="Filter K8s noise"),
):
    """
    Deep drift analysis using Jaccard + Cosine.
    Returns complete drift picture with value differences.
    """
    try:
        # Load manifests
        manifests_a = k8s_detector.load_environment(env_a)
        manifests_b = k8s_detector.load_environment(env_b)

        # Build config dicts
        config_a = {}
        config_b = {}

        for content in manifests_a.values():
            tokens = Tokenizer.tokenize_yaml(content)
            for token in tokens:
                if "=" in token:
                    key, val = token.split("=", 1)
                    config_a[key.strip()] = val.strip()

        for content in manifests_b.values():
            tokens = Tokenizer.tokenize_yaml(content)
            for token in tokens:
                if "=" in token:
                    key, val = token.split("=", 1)
                    config_b[key.strip()] = val.strip()

        # Filter noise if requested
        if filter_noise:
            config_a = filter_config(config_a)
            config_b = filter_config(config_b)

        # Run combined analysis
        result = CombinedScorer.compare(config_a, config_b)

        return {
            "environment_a": env_a,
            "environment_b": env_b,
            "total_keys_a": len(config_a),
            "total_keys_b": len(config_b),
            "noise_filtered": filter_noise,
            "analysis": result.to_dict(),
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analyze/matrix")
def analyze_matrix(
    filter_noise: bool = Query(True)
):
    """
    Deep analysis matrix for all environments.
    """
    try:
        envs = k8s_detector.list_environments()
        matrix = {}

        for env_a in envs:
            matrix[env_a] = {}
            for env_b in envs:
                if env_a == env_b:
                    matrix[env_a][env_b] = {
                        "combined_score": 1.0,
                        "drift_level": "NO DRIFT"
                    }
                    continue

                manifests_a = k8s_detector.load_environment(
                    env_a)
                manifests_b = k8s_detector.load_environment(
                    env_b)

                config_a = {}
                config_b = {}

                for content in manifests_a.values():
                    tokens = Tokenizer.tokenize_yaml(content)
                    for token in tokens:
                        if "=" in token:
                            k, v = token.split("=", 1)
                            config_a[k.strip()] = v.strip()

                for content in manifests_b.values():
                    tokens = Tokenizer.tokenize_yaml(content)
                    for token in tokens:
                        if "=" in token:
                            k, v = token.split("=", 1)
                            config_b[k.strip()] = v.strip()

                if filter_noise:
                    config_a = filter_config(config_a)
                    config_b = filter_config(config_b)

                result = CombinedScorer.compare(
                    config_a, config_b)

                matrix[env_a][env_b] = {
                    "jaccard_score": result.jaccard_score,
                    "cosine_score": result.cosine_score,
                    "combined_score": result.combined_score,
                    "drift_level": result.drift_level,
                }

        return {
            "environments": envs,
            "matrix": matrix,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Matrix failed: {str(e)}"
        )
