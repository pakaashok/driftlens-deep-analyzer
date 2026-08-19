# 🔬 DriftLens Deep Analyzer

> **End-to-end Kubernetes configuration drift detection — powered by Jaccard + Cosine Similarity algorithms**

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5)
![Tests](https://img.shields.io/badge/Tests-55%20Passing-success)
![License](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)

---

## 📖 What is DriftLens Deep Analyzer?

When you manage multiple Kubernetes environments (`dev`, `staging`, `prod`), configurations naturally drift apart over time. 

**DriftLens Deep Analyzer** automatically detects, measures, and visualizes configuration drift across Kubernetes manifests using a dual-algorithm approach:

- 🔍 **Detects WHAT changed** between environments (Keys & Values)
- 📊 **Measures HOW MUCH drift exists** using combined similarity scoring
- 🤖 **Automatically triggers** CI/CD analysis when manifests change
- 📺 **Shows real-time status** via a Live Dashboard with 5s auto-polling

### 🔬 How The Dual-Algorithm Engine Works

```text
1. Jaccard Similarity (40% Weight) — Measures KEY PRESENCE drift
   Formula: |A ∩ B| / |A ∪ B|
   Evaluates structural differences and key availability between manifests.

2. Cosine Similarity (60% Weight) — Measures VALUE drift
   Formula: (A · B) / (|A| × |B|)
   Evaluates actual value variations for common configuration keys.

Combined Score = (0.40 × Jaccard) + (0.60 × Cosine)
```

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       Developer Workflow                    │
│  1. Edit K8s Manifests (k8s/overlays/dev or prod)           │
│  2. Push changes to GitHub (`git push origin main`)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions Pipeline                   │
│  3. Triggered by workflow (.github/workflows/drift-detect.yml)│
│  4. Runs deep detection engine (scripts/detect_drift.py)    │
│     ├── Evaluates Jaccard Similarity (40%)                  │
│     └── Evaluates Cosine Similarity (60%)                   │
│  5. Generates & commits drift-results.json back to repository │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Live Dashboard (http://localhost:3001)         │
│  6. Frontend polls raw commit output every 5 seconds         │
│  7. Renders real-time metrics:                              │
│     ├── Combined Drift Scores & Risk Levels                 │
│     ├── Value Differences Breakdown                         │
│     └── Missing Keys Matrix Across Environments             │
└──────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Deep Drift Detection** | Multi-dimensional manifest comparison across all environments |
| 🧮 **Dual Scoring Engine** | Blends Jaccard (keys) and Cosine (values) similarity models |
| 📺 **Live Dashboard** | Auto-polling Next.js frontend rendering real-time drift metrics |
| 🚦 **Risk Level System** | Categorizes drift: NO DRIFT / LOW / MODERATE / HIGH / CRITICAL |
| 📊 **Matrix Analysis** | Multi-environment grid view comparing all environments at once |
| 🐳 **Containerized** | Multi-stage Docker deployment managed via Docker Compose |
| ☸️ **K8s & Kustomize Native** | Integrated structure supporting Kustomize overlays |
| 🤖 **Automated CI Workflow** | Headless script execution via GitHub Actions |
| 🔌 **REST API** | Fast, interactive FastAPI OpenAPI backend |
| 🧪 **Extensively Tested** | 55 unit tests covering algorithms, tokenizers, and filters |

---

## 🚀 Quick Start

### Prerequisites

- Docker + Docker Compose
- Git

### One Command Deployment!

```bash
# Step 1: Clone Repository
git clone https://github.com/pakaashok/driftlens-deep-analyzer.git
cd driftlens-deep-analyzer

# Step 2: Start Container Stack
docker-compose up -d
```

Open Dashboard: [**http://localhost:3001**](http://localhost:3001) 🎉

---

## 🔄 GitOps Workflow

### Step 1: Edit K8s Manifests
```bash
# Edit development overlay configuration
vim k8s/overlays/dev/configmap.yaml

# Edit production overlay configuration
vim k8s/overlays/prod/configmap.yaml
```

### Step 2: Commit & Push Changes
```bash
git add k8s/
git commit -m "update: sync production configuration values"
git push origin main
```

### Step 3: View Auto-Updated Results
```text
1. GitHub Actions workflow triggers automatically (~40s runtime)
2. Live Dashboard updates automatically via 5s polling cycle
3. View updated drift score directly at http://localhost:3001
```

---

## 📺 Dashboard Features

* **🔴 Live Drift Tab**
  * Auto-updates every 5 seconds
  * Displays current repository commit metadata
  * Visualizes Jaccard, Cosine, and Combined scores
  * Renders explicit key-value difference tables
* **🔬 Manual Tab**
  * Execute on-demand comparisons between any two environments
* **📊 Matrix Tab**
  * View cross-environment similarity scores in a single grid

---

## 📁 Project Structure

```text
driftlens-deep-analyzer/
├── 🐳 docker-compose.yml             # Local multi-container deployment
├── 📊 drift-results.json             # Live CI scan output target
├── 📝 README.md                      # Project documentation
│
├── ☸️  k8s/                           # Kubernetes manifests (Kustomize)
│   ├── base/                         # Base deployments and services
│   └── overlays/                     # Environment-specific patches
│       ├── dev/                      # Dev environment overlays
│       └── prod/                     # Prod environment overlays
│
├── 🐍 backend/                       # Python FastAPI Engine
│   ├── Dockerfile                    # Container definition
│   ├── requirements.txt
│   ├── app/
│   │   ├── core/                     # Math & Parsing Core
│   │   │   ├── jaccard.py            # Jaccard algorithm implementation
│   │   │   ├── cosine.py             # Cosine algorithm implementation
│   │   │   ├── combined.py           # Weighted similarity combiner
│   │   │   ├── tokenizer.py          # YAML tokenizer
│   │   │   └── k8s_filter.py         # Metadata/Noise filtering
│   │   ├── api/                      # REST Endpoints
│   │   │   └── routes.py
│   │   ├── models/                   # Schemas & Types
│   │   │   └── schemas.py
│   │   ├── modules/                  # Kubernetes load routines
│   │   │   └── kubernetes.py
│   │   └── main.py                   # FastAPI Application Entry
│   └── tests/                        # PyTest Suite
│       ├── test_jaccard.py           # 20 Jaccard tests
│       ├── test_cosine.py            # 20 Cosine tests
│       └── test_tokenizer.py         # 15 Tokenizer tests
│
├── ⚛️  frontend/                      # Next.js Live Dashboard
│   ├── Dockerfile                    # Multi-stage production build
│   ├── app/                          # Next.js App Router
│   │   ├── dashboard.tsx             # Primary dashboard interface
│   │   ├── page.tsx
│   │   └── globals.css
│   └── lib/                          # API client layer
│       └── api.ts
│
├── 📜 scripts/                        # Automation & CI Scripts
│   ├── detect_drift.py               # Standalone drift detection script
│   └── check-drift.sh                # Local CLI verification wrapper
│
└── 🤖 .github/                       # GitHub Actions Workflows
    └── workflows/
        ├── drift-detect.yml          # Automated CI drift analysis
        └── deploy.yml                # Docker build & push workflow
```

---

## 📊 Drift Level Classification

| Level | Score Threshold | Meaning | Action Needed |
| :--- | :--- | :--- | :--- |
| ✅ **NO DRIFT** | 100% | Environments fully aligned | None |
| 🔵 **LOW DRIFT** | > 90% | Minor configuration variances | Safe to promote |
| 🟡 **MODERATE** | > 70% | Noticeable value or key differences | Review changes |
| 🟠 **HIGH DRIFT** | > 50% | Major configuration differences | Manual sync recommended |
| 🔴 **CRITICAL** | < 50% | Severe configuration divergence | **Do NOT promote!** |

---

## 🌐 API Reference

### Health Check

```http
GET /api/health
```

### Compare Environments

```http
GET /api/analyze?env_a=dev&env_b=prod
```

### Retrieve Environment Matrix

```http
GET /api/analyze/matrix
```

### Retrieve Latest CI Drift Scan

```http
GET /api/drift-results
```

### CLI Quick Examples

```bash
# Check Backend Health
curl http://localhost:8001/api/health

# Run Deep Analysis (Dev vs Prod)
curl "http://localhost:8001/api/analyze?env_a=dev&env_b=prod"

# Get Matrix View
curl http://localhost:8001/api/analyze/matrix
```

---

## ☸️ Kubernetes Local Deployment

Deploy sample applications directly to a local Minikube cluster:

```bash
# Start Minikube cluster
minikube start --driver=docker

# Create environment namespaces
kubectl create namespace driftlens-dev
kubectl create namespace driftlens-prod

# Apply Kustomize manifests
kubectl apply -k k8s/overlays/dev/
kubectl apply -k k8s/overlays/prod/

# Verify active resources
kubectl get all -n driftlens-dev
kubectl get all -n driftlens-prod

# Get interactive URL endpoints
minikube service dev-driftlens-deep-frontend -n driftlens-dev --url
minikube service prod-driftlens-deep-frontend -n driftlens-prod --url
```

---

## 🧪 Local Test Execution

```bash
cd backend

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full test suite
pytest tests/ -v
```

### Expected Output
```text
tests/test_jaccard.py   - 20 passed ✅
tests/test_cosine.py    - 20 passed ✅
tests/test_tokenizer.py - 15 passed ✅

Total: 55 passed  ✅
```

---

## 🐳 Docker Container Operations

```bash
# Start full application stack
docker-compose up -d

# Stop running containers
docker-compose down

# Tail container logs
docker-compose logs -f

# Rebuild containers after source updates
docker-compose up -d --build
```

---

## 🤖 GitHub Actions Setup

To enable automated Docker image builds and repository publishing, set up the following secrets under **GitHub → Settings → Secrets and variables → Actions**:

```makefile
DOCKER_USERNAME = your-dockerhub-username
DOCKER_PASSWORD = your-dockerhub-token
```

---

## 📈 Sample Results Output

```text
dev vs prod Analysis Output:
┌────────────────────────────────────────┐
│ Jaccard Score:  74.2%  (Key Drift)     │
│ Cosine Score:   83.1%  (Value Drift)   │
│ Combined Score: 75.5%  (Overall)       │
│ Status Level:   MODERATE DRIFT         │
└────────────────────────────────────────┘

Keys Present Only in Production:
  - data.ALERT_EMAIL
  - data.MONITORING_ENABLED
  - data.NEW_FEATURE
  - data.RATE_LIMIT

Value Differences Identified:
  - data.LOG_LEVEL:       debug → warn
  - data.REPLICAS:        1 → 3
  - data.MAX_CONNECTIONS:  10 → 200
  - data.TIMEOUT:         30 → 120
```

---

## 👨‍💻 Built With

| **Technology** | **Purpose** |
|---|---|
| Python 3.12 | Core analysis engine & backend logic |
| FastAPI | REST API framework & OpenAPI generation |
| Next.js 16 | React dashboard framework |
| Tailwind CSS | Styling & UI layout |
| Docker | Containerization and stack composition |
| Kubernetes | Target environment orchestration |
| Kustomize | Kubernetes configuration management |
| GitHub Actions | Automated CI/CD execution pipeline |
| PyTest | Comprehensive unit testing framework |
