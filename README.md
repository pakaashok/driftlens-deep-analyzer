# 🔬 DriftLens Deep Analyzer

> **End-to-end Kubernetes configuration drift detection using Jaccard + Cosine Similarity algorithms.**
> Changes in K8s configs automatically trigger drift detection via GitHub Actions and reflect in the Live Dashboard!

![Live Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)
![Tests](https://img.shields.io/badge/Tests-55%20passing-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![K8s](https://img.shields.io/badge/K8s-Minikube-blue)

---

## 🎯 What is DriftLens Deep Analyzer?

When you manage multiple Kubernetes environments (`dev`, `staging`, `prod`), configs drift apart over time. **DriftLens Deep Analyzer**:

- 🔍 Detects **what** changed between environments
- 📊 Measures **how much** drift exists
- 🤖 **Automatically** runs when configs change
- 📺 Shows results in a **Live Dashboard**

---

## 🏗️ Architecture

```text
Developer
│
│ 1. Edit k8s config
│    k8s/overlays/dev/configmap.yaml
│    k8s/overlays/prod/configmap.yaml
│
│ 2. git push
▼
GitHub
│
│ 3. GitHub Actions triggers
│    (.github/workflows/drift-detect.yml)
│
│ 4. Runs drift detection
│    scripts/detect_drift.py
│    → Jaccard Similarity (40%)
│    → Cosine Similarity  (60%)
│
│ 5. Saves drift-results.json
│    Commits back to repo
▼
Dashboard (http://localhost:3001)
│
│ 6. Polls every 5 seconds
│    Reads from GitHub Raw URL
│
│ 7. Shows Live Results:
│    → Drift scores
│    → Value differences
│    → Keys only in dev/prod
│    → Environment matrix
▼
✅ No manual steps needed!
```

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Minikube
- kubectl
- Git

---

## 🐳 Part 1: Dashboard + API (Docker Compose)

```bash
# Step 1: Clone
git clone https://github.com/pakaashok/driftlens-deep-analyzer
cd driftlens-deep-analyzer

# Step 2: Start
docker-compose up -d

# Step 3: Verify
docker-compose ps

# Step 4: Open browser
http://localhost:3001
```

### Verify API

```bash
# Health check
curl http://localhost:8001/api/health

# Latest drift results
curl http://localhost:8001/api/drift-results

# Environments
curl http://localhost:8001/api/environments
```

---

## ☸️ Part 2: Kubernetes Deployment (Minikube)

```bash
# Step 1: Start Minikube
minikube start --driver=docker
minikube status

# Step 2: Create Namespaces
kubectl create namespace driftlens-dev
kubectl create namespace driftlens-prod

# Step 3: Deploy Dev Environment
kubectl apply -k k8s/overlays/dev/

# Step 4: Deploy Prod Environment
kubectl apply -k k8s/overlays/prod/

# Step 5: Verify Pods Running
kubectl get pods -n driftlens-dev
kubectl get pods -n driftlens-prod

# Step 6: Get Access URLs
minikube service dev-driftlens-deep-frontend   -n driftlens-dev --url

minikube service prod-driftlens-deep-frontend   -n driftlens-prod --url
```

### Expected Output

```text
=== DEV ===
NAME                                           READY
dev-driftlens-deep-backend-xxx                 1/1
dev-driftlens-deep-frontend-xxx                1/1

=== PROD ===
NAME                                           READY
prod-driftlens-deep-backend-xxx-1              1/1
prod-driftlens-deep-backend-xxx-2              1/1
prod-driftlens-deep-backend-xxx-3              1/1
prod-driftlens-deep-frontend-xxx               1/1
```

---

## 🔄 GitOps Flow - How Drift Detection Works

### Step 1: Edit K8s Config
```bash
# Edit dev config
vim k8s/overlays/dev/configmap.yaml

# Edit prod config
vim k8s/overlays/prod/configmap.yaml
```

### Step 2: Push Changes
```bash
git add k8s/
git commit -m "update: prod config change"
git push origin main
```

### Step 3: GitHub Actions Auto-Runs
```text
Push triggers GitHub Actions (~40s):
  → Runs Jaccard + Cosine analysis
  → Detects what changed
  → Updates drift-results.json
  → Commits results back to repo
```

### Step 4: Dashboard Auto-Updates
```text
Frontend polls every 5 seconds:
  → Reads from GitHub Raw URL
  → Shows updated drift scores
  → No manual steps needed! ✅
```

---

## 📺 Dashboard Features

### 🔴 Live Drift Tab
- Auto-updates every 5 seconds
- Shows:
  - Latest GitHub commit info
  - Jaccard score (key drift)
  - Cosine score (value drift)
  - Combined score
  - Value differences table
  - Keys only in dev
  - Keys only in prod

### 🔬 Manual Tab
- Compare any two environments:
  - `dev` vs `prod`
  - `dev` vs `staging`
  - `staging` vs `prod`
- On-demand analysis

### 📊 Matrix Tab
- All environments compared:
  - `dev` → `prod` → `staging`
  - `prod` → `dev` → `staging`
  - `staging` → `dev` → `prod`
- Color-coded drift levels

---

## 📁 Project Structure

```kotlin
driftlens-deep-analyzer/
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
```

---

## 📊 Algorithms

### Jaccard Similarity (40% weight)
Measures **KEY PRESENCE** drift. Compares which config keys exist in each environment.

$$	ext{Score} = rac{|A \cap B|}{|A \cup B|}$$

### Cosine Similarity (60% weight)
Measures **VALUE** drift. Compares actual config values between environments.

$$	ext{Score} = rac{A \cdot B}{\|A\| 	imes \|B\|}$$

### Drift Levels

| Level | Score | Meaning |
| :--- | :--- | :--- |
| ✅ **NO DRIFT** | 100% | Perfectly in sync |
| 🔵 **LOW DRIFT** | >90% | Minor differences |
| 🟡 **MODERATE** | >70% | Review before promote |
| 🟠 **HIGH DRIFT** | >50% | Action required |
| 🔴 **CRITICAL** | <50% | Do NOT promote! |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health |
| `GET` | `/api/environments` | List environments |
| `GET` | `/api/analyze` | Deep drift analysis |
| `GET` | `/api/analyze/matrix` | All envs matrix |
| `GET` | `/api/drift-results` | Latest CI results |

### Examples

```bash
# Health check
curl http://localhost:8001/api/health

# Analyze dev vs prod
curl "http://localhost:8001/api/analyze?env_a=dev&env_b=prod"

# Get latest drift results
curl http://localhost:8001/api/drift-results

# Get matrix
curl http://localhost:8001/api/analyze/matrix
```

---

## 🧪 Tests

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run unit tests
pytest tests/ -v

# Results:
# test_jaccard.py   - 20 passed ✅
# test_cosine.py    - 20 passed ✅
# test_tokenizer.py - 15 passed ✅
# Total: 55 passed  ✅
```

---

## 🐳 Docker Images

```bash
# Pull manually
docker pull adeeashok/driftlens-deep-analyzer:latest
docker pull adeeashok/driftlens-deep-frontend:latest

# Or use docker-compose (recommended)
docker-compose up -d
```

---

## 🤖 GitHub Actions Workflows

### `drift-detect.yml`
- **Triggers:** `k8s/**` file changes
- **Steps:**
  1. Checkout code
  2. Install Python deps
  3. Run `detect_drift.py`
  4. Save `drift-results.json`
  5. Commit results back to repo

### `deploy.yml`
- **Triggers:** Any push to `main`
- **Steps:**
  1. Run 55 tests
  2. Build backend Docker image
  3. Build frontend Docker image
  4. Push to Docker Hub

---

## 🔧 GitHub Secrets Required

Configure secrets under **GitHub → Settings → Secrets → Actions → New repository secret**:

```makefile
DOCKER_USERNAME = your-dockerhub-username
DOCKER_PASSWORD = your-dockerhub-token
```

---

## 📈 Sample Results

```text
dev vs prod Analysis:
┌─────────────────────────────────┐
│ Jaccard:  74.2%  (key drift)    │
│ Cosine:   83.1%  (value drift)  │
│ Combined: 75.5%  (overall)      │
│ Level:    MODERATE DRIFT        │
└─────────────────────────────────┘

Keys only in prod:
  data.ALERT_EMAIL
  data.MONITORING_ENABLED
  data.NEW_FEATURE
  data.RATE_LIMIT

Value Differences:
  data.LOG_LEVEL:       debug → warn
  data.REPLICAS:        1 → 3
  data.MAX_CONNECTIONS: 10 → 200
  data.TIMEOUT:         30 → 120
