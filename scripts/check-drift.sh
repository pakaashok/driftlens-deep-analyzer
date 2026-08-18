#!/bin/bash
# DriftLens Deep Analyzer - GitOps Drift Checker
# Compares K8s configs between environments

set -e

API_URL="${DRIFTLENS_API:-http://localhost:8001}"

echo "🔍 DriftLens Deep Analyzer - Drift Check"
echo "========================================="
echo "API: $API_URL"
echo ""

# Check health
HEALTH=$(curl -s "$API_URL/api/health" 2>/dev/null)
if [ -z "$HEALTH" ]; then
  echo "❌ Cannot connect to DriftLens API!"
  exit 1
fi
echo "✅ API: Connected"
echo ""

# Get environments
ENVS=$(curl -s "$API_URL/api/environments" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(' '.join(data['environments']))
")
echo "📦 Environments: $ENVS"
echo ""

# Analyze dev vs prod
echo "🔬 Analyzing dev vs prod..."
RESULT=$(curl -s \
  "$API_URL/api/analyze?env_a=dev&env_b=prod")

COMBINED=$(echo $RESULT | python3 -c "
import sys, json
data = json.load(sys.stdin)
c = data['analysis']['combined']
print(f\"Score: {c['similarity_percentage']}%\")
print(f\"Level: {c['drift_level']}\")
print(f\"Drift: {c['overall_drift_percentage']}%\")
print(f\"Rec:   {c['recommendation']}\")
")

echo "$COMBINED"
echo ""

# Check matrix
echo "📊 Environment Matrix:"
curl -s "$API_URL/api/analyze/matrix" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
envs = data['environments']
matrix = data['matrix']
print(f\"{'':10} \" + ' '.join(f'{e:12}' for e in envs))
for ea in envs:
    row = f'{ea:10} '
    for eb in envs:
        cell = matrix[ea][eb]
        score = cell['combined_score'] * 100
        row += f'{score:6.1f}%      '
    print(row)
"
