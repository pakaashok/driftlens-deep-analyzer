import json
import sys
import glob
import os
from datetime import datetime, timezone

sys.path.insert(0, 'backend')
from app.core.tokenizer import Tokenizer
from app.core.combined import CombinedScorer
from app.core.k8s_filter import filter_config

def load(path):
    config = {}
    for f in glob.glob(
      f'{path}/**/*.yaml', recursive=True):
        tokens = Tokenizer.tokenize_yaml(
          open(f).read())
        for t in tokens:
            if '=' in t:
                k, v = t.split('=', 1)
                config[k.strip()] = v.strip()
    return filter_config(config)

dev  = load('k8s/overlays/dev')
prod = load('k8s/overlays/prod')
r    = CombinedScorer.compare(dev, prod)

commit  = os.environ.get('GITHUB_SHA', 'local')
actor   = os.environ.get('GITHUB_ACTOR', 'manual')
message = os.environ.get('COMMIT_MESSAGE', 'manual')

out = {
    'environment_a': 'dev',
    'environment_b': 'prod',
    'total_keys_a': len(dev),
    'total_keys_b': len(prod),
    'timestamp': datetime.now(
        timezone.utc).isoformat(),
    'commit': commit,
    'triggered_by': actor,
    'commit_message': message,
    'analysis': r.to_dict()
}

with open('drift-results.json', 'w') as f:
    json.dump(out, f, indent=2)

c = out['analysis']['combined']
print(f"Level: {c['drift_level']}")
print(f"Drift: {c['overall_drift_percentage']}%")
print(f"Score: {c['similarity_percentage']}%")
