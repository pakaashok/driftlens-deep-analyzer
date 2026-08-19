Markdown# 🔬 DriftLens Deep Analyzer

> End-to-end Kubernetes configuration drift detection using **Jaccard + Cosine Similarity** algorithms.
> Changes in K8s configs automatically trigger drift detection via GitHub Actions and reflect in the Live Dashboard!

---

## 🎯 What is DriftLens Deep Analyzer?

When you manage multiple Kubernetes environments (`dev`, `staging`, `prod`), configs drift apart over time. DriftLens Deep Analyzer:

- 🔍 Detects **what** changed between environments
- 📊 Measures **how much** drift exists
- 🤖 **Automatically** runs when configs change
- 📺 Shows results in a **Live Dashboard**

---

## 🏗️ Architecture

Developer││ 1. Edit k8s config│    k8s/overlays/dev/configmap.yaml│    k8s/overlays/prod/configmap.yaml││ 2. git push▼GitHub││ 3. GitHub Actions triggers│    (.github/workflows/drift-detect.yml)││ 4. Runs drift detection│    scripts/detect_drift.py│    → Jaccard Similarity (40%)│    → Cosine Similarity  (60%)││ 5. Saves drift-results.json│    Commits back to repo▼Dashboard (http://localhost:3001)││ 6. Polls every 5 seconds│    Reads from GitHub Raw URL││ 7. Shows Live Results:│    → Drift scores│    → Value differences│    → Keys only in dev/prod│    → Environment matrix▼✅ No manual steps needed!
---

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose
- Git

### Run in 3 Steps

```bash
# Step 1: Clone
git clone [https://github.com/pakaashok/driftlens-deep-analyzer](https://github.com/pakaashok/driftlens-deep-analyzer)
cd driftlens-deep-analyzer

# Step 2: Start
docker-compose up -d

# Step 3: Open browser
http://localhost:3001
✅ That's it! Dashboard is live!🔄 GitOps FlowStep 1: Edit K8s ConfigBash# Edit dev config
vim k8s/overlays/dev/configmap.yaml

# Edit prod config
vim k8s/overlays/prod/configmap.yaml
Step 2: Push ChangesBashgit add k8s/
git commit -m "update: prod config change"
git push origin main
Step 3: Watch Dashboard UpdatePlaintextGitHub Actions runs automatically (~40s)
Dashboard updates automatically (~5s polling)
http://localhost:3001 ✅
📺 Dashboard Features🔴 Live Drift TabAuto-updates every 5 secondsShows latest GitHub commit infoJaccard + Cosine + Combined scoresValue differences tableKeys only in dev/prod🔬 Manual TabCompare any two environmentsOn-demand analysis📊 Matrix TabAll environments comparedColor-coded drift levels📁 Project StructureKotlindriftlens-deep-analyzer/
│
├── 🐳 docker-compose.yml
│      └── One command deployment!
│
├── 📊 drift-results.json
│      └── Auto-updated by GitHub Actions
│
├── ☸️  k8s/
│   ├── base/
│   │   ├── backend-deployment.yaml
│   │   ├── backend-service.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── frontend-service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── dev/
│       │   ├── configmap.yaml   ← Edit this!
│       │   └── kustomization.yaml
│       └── prod/
│           ├── configmap.yaml   ← Edit this!
│           └── kustomization.yaml
│
├── 🐍 backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── jaccard.py       ← Jaccard algo
│   │   │   ├── cosine.py        ← Cosine algo
│   │   │   ├── combined.py      ← Combined scorer
│   │   │   ├── tokenizer.py     ← YAML tokenizer
│   │   │   └── k8s_filter.py    ← Noise filter
│   │   ├── api/
│   │   │   └── routes.py        ← API endpoints
│   │   ├── models/
│   │   │   └── schemas.py       ← Data models
│   │   ├── modules/
│   │   │   └── kubernetes.py    ← K8s loader
│   │   └── main.py              ← FastAPI app
│   ├── tests/
│   │   ├── test_jaccard.py      ← 20 tests
│   │   ├── test_cosine.py       ← 20 tests
│   │   └── test_tokenizer.py    ← 15 tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── ⚛️  frontend/
│   ├── app/
│   │   ├── dashboard.tsx        ← Main dashboard
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── lib/
│   │   └── api.ts               ← API client
│   └── Dockerfile
│
├── 📜 scripts/
│   ├── detect_drift.py          ← Drift detector
│   └── check-drift.sh           ← Manual check
│
└── 🤖 .github/
    └── workflows/
        ├── drift-detect.yml     ← Auto drift CI
        └── deploy.yml           ← Docker build CI
📊 AlgorithmsJaccard Similarity (40% weight)Measures KEY PRESENCE drift. Compares which config keys exist in each environment.$$\text{Score} = \frac{\vert{}A \cap B\vert{}}{\vert{}A \cup B\vert{}}$$Cosine Similarity (60% weight)Measures VALUE drift. Compares actual config values between environments.$$\text{Score} = \frac{A \cdot B}{\Vert{}A\Vert{} \times \Vert{}B\Vert{}}$$Drift LevelsLevelScoreMeaning✅ NO DRIFT100%Perfectly in sync🔵 LOW DRIFT> 90%Minor differences🟡 MODERATE> 70%Review before promote🟠 HIGH DRIFT> 50%Action required🔴 CRITICAL< 50%Do NOT promote!🌐 API EndpointsMethodEndpointDescriptionGET/api/healthService health checkGET/api/environmentsList all available environmentsGET/api/analyzeRun deep drift analysisGET/api/analyze/matrixComparative matrix for all environmentsGET/api/drift-resultsFetch latest CI scan resultsExamplesBash# Health check
curl http://localhost:8001/api/health

# Analyze dev vs prod
curl "http://localhost:8001/api/analyze?env_a=dev&env_b=prod"

# Get latest drift results
curl http://localhost:8001/api/drift-results

# Get environment matrix
curl http://localhost:8001/api/analyze/matrix
☸️ Kubernetes DeploymentBash# Start minikube
minikube start --driver=docker

# Create namespaces
kubectl create namespace driftlens-dev
kubectl create namespace driftlens-prod

# Deploy using Kustomize
kubectl apply -k k8s/overlays/dev/
kubectl apply -k k8s/overlays/prod/

# Check status
kubectl get all -n driftlens-dev
kubectl get all -n driftlens-prod

# Get service URLs
minikube service dev-driftlens-deep-frontend -n driftlens-dev --url
minikube service prod-driftlens-deep-frontend -n driftlens-prod --url
🧪 TestsBashcd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run PyTest
pytest tests/ -v

# Output summary:
# test_jaccard.py   - 20 passed ✅
# test_cosine.py    - 20 passed ✅
# test_tokenizer.py - 15 passed ✅
# Total: 55 passed  ✅
🐳 Docker ImagesBash# Pull and run manually
docker pull adeeashok/driftlens-deep-analyzer:latest
docker pull adeeashok/driftlens-deep-frontend:latest

# Or use docker-compose (recommended)
docker-compose up -d
🤖 GitHub Actions Workflowsdrift-detect.ymlTriggers: Changes under k8s/**Steps:Checkout codeInstall Python dependenciesRun scripts/detect_drift.pySave drift-results.jsonCommit updated results back to main branchdeploy.ymlTriggers: Push to mainSteps:Run 55 unit testsBuild backend Docker imageBuild frontend Docker imagePush images to Docker Hub🔧 GitHub Secrets RequiredConfigure the following secrets under GitHub → Settings → Secrets and variables → Actions → New repository secret:MakefileDOCKER_USERNAME = your-dockerhub-username
DOCKER_PASSWORD = your-dockerhub-token
📈 Sample ResultsPlaintextdev vs prod Analysis:
┌─────────────────────────────────┐
│ Jaccard:  74.2%  (key drift)    │
│ Cosine:   83.1%  (value drift)  │
│ Combined: 75.5%  (overall)      │
│ Level:    MODERATE DRIFT        │
└─────────────────────────────────┘

Keys only in prod:
  - data.ALERT_EMAIL
  - data.MONITORING_ENABLED
  - data.NEW_FEATURE
  - data.RATE_LIMIT

Value Differences:
  - data.LOG_LEVEL:       debug → warn
  - data.REPLICAS:        1 → 3
  - data.MAX_CONNECTIONS:  10 → 200
  - data.TIMEOUT:         30 → 120
  