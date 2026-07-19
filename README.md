# CloudShop - Enterprise E-Commerce Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](README.md)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-blue.svg)](https://kubernetes.io/)

A production-grade, cloud-native microservices e-commerce platform built with **Python FastAPI**, **React**, **Kubernetes**, and deployed on **Google Cloud Platform (GCP)** with comprehensive observability, security, and enterprise DevOps practices.

## 🏗️ Architecture Overview

CloudShop is designed to demonstrate enterprise-level DevOps and cloud-native architectural patterns suitable for **10,000+ concurrent users** in production environments.

### Technology Stack

**Backend:**
- Python 3.11+ with FastAPI (async/await)
- PostgreSQL (relational data)
- Redis (caching & sessions)
- RabbitMQ (async messaging)
- JWT Authentication
- SQLAlchemy ORM
- Alembic Migrations

**Frontend:**
- React 18+ with TypeScript
- Material-UI (MUI)
- Redux Toolkit
- Responsive Design
- Dark Mode

**Infrastructure:**
- Google Cloud Platform (GCP)
- Terraform (Infrastructure as Code)
- Kubernetes (GKE)
- Docker (containerization)
- GitHub Actions (CI/CD)

**Observability:**
- Prometheus (metrics)
- Grafana (dashboards)
- Loki (log aggregation)
- Promtail (log shipping)
- AlertManager (alerts)

## 📋 Microservices Architecture

| Service | Purpose | Port | Technology | Database |
|---------|---------|------|-----------|----------|
| **Gateway** | API Gateway, routing, rate limiting, request logging | 8000 | FastAPI | Redis |
| **Auth** | JWT authentication, user registration, role management | 8001 | FastAPI | PostgreSQL |
| **Product** | Product catalog, categories, reviews, ratings | 8002 | FastAPI | PostgreSQL |
| **Cart** | Shopping cart management, wishlist | 8003 | FastAPI | Redis + PostgreSQL |
| **Order** | Order processing, tracking, history | 8004 | FastAPI | PostgreSQL |
| **Payment** | Payment processing (mock gateway), transactions | 8005 | FastAPI | PostgreSQL |
| **Inventory** | Stock management, reservations | 8006 | FastAPI | PostgreSQL |
| **Notification** | Email notifications, SMS alerts | 8007 | FastAPI | PostgreSQL |
| **Frontend** | React SPA with Material-UI | 3000 | React/TypeScript | N/A |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose 20.10+
- kubectl 1.28+
- Terraform 1.5+
- Python 3.11+
- Node.js 18+
- GCP Account with billing enabled

### Local Development with Docker Compose

```bash
# Clone repository
git clone https://github.com/khayumm25-zaD/-CloudShop.git
cd -CloudShop

# Start all services
docker-compose up -d

# Initialize databases and seed data
./scripts/setup.sh

# Access services
- Gateway API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- pgAdmin: http://localhost:5050 (admin@example.com/admin)
```

### Production Deployment on GKE

```bash
# Configure GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp/key.json

# Deploy infrastructure
cd infrastructure/gcp/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Deploy microservices to GKE
cd ../../kubernetes
kubectl apply -f namespaces/
kubectl apply -f configmaps/
kubectl apply -f secrets/
kubectl apply -f deployments/
kubectl apply -f services/
kubectl apply -f ingress/
kubectl apply -f autoscaling/

# Verify deployment
kubectl rollout status deployment/gateway -n cloudshop
kubectl get all -n cloudshop
```

## 📁 Project Structure

```
-CloudShop/
├── backend/                          # Backend microservices
│   ├── services/
│   │   ├── gateway/                  # API Gateway Service
│   │   ├── auth/                     # Authentication Service
│   │   ├── product/                  # Product Service
│   │   ├── cart/                     # Cart Service
│   │   ├── order/                    # Order Service
│   │   ├── payment/                  # Payment Service
│   │   ├── inventory/                # Inventory Service
│   │   └── notification/             # Notification Service
│   ├── shared/                       # Shared utilities & libraries
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── exceptions/
│   ├── tests/                        # Integration & E2E tests
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Multi-stage Dockerfile
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── store/                    # Redux store
│   │   ├── services/                 # API clients
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   ├── gcp/
│   │   ├── terraform/                # GCP infrastructure
│   │   │   ├── vpc/
│   │   │   ├── gke/
│   │   │   ├── databases/
│   │   │   ├── storage/
│   │   │   ├── monitoring/
│   │   │   └── main.tf
│   │   └── scripts/
│   ├── kubernetes/                   # K8s manifests
│   │   ├── namespaces/
│   │   ├── configmaps/
│   │   ├── secrets/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── ingress/
│   │   ├── autoscaling/
│   │   ├── network-policies/
│   │   └── monitoring/
│   └── helm/                         # Helm charts
│       └── cloudshop/
├── ci-cd/
│   └── github/
│       └── workflows/                # GitHub Actions
│           ├── build.yml
│           ├── test.yml
│           ├── deploy.yml
│           └── security-scan.yml
├── docs/                             # Documentation
│   ├── architecture/
│   ├── api/
│   ├── deployment/
│   ├── troubleshooting/
│   ├── testing/
│   └── security/
├── scripts/                          # Utility scripts
│   ├── setup.sh
│   ├── db-init.sh
│   ├── backup.sh
│   └── monitoring-setup.sh
├── load-tests/                       # Load testing
│   ├── k6-scenarios.js
│   └── locust-scenarios.py
├── docker-compose.yml                # Local development
├── docker-compose.prod.yml           # Production-like local setup
├── .dockerignore
├── .gitignore
├── LICENSE
└── CONTRIBUTING.md
```

## 🔐 Security Features

- ✅ **HTTPS/TLS** with Let's Encrypt
- ✅ **JWT Authentication** with RS256
- ✅ **Role-Based Access Control (RBAC)**
- ✅ **Secrets Management** with Google Secret Manager
- ✅ **Network Policies** for pod-to-pod communication
- ✅ **IAM** with least privilege principle
- ✅ **Container Scanning** in CI/CD pipeline
- ✅ **Dependency Scanning** for vulnerabilities
- ✅ **Rate Limiting** on API Gateway
- ✅ **Input Validation** on all endpoints
- ✅ **CORS** properly configured
- ✅ **SQL Injection** prevention with SQLAlchemy ORM
- ✅ **XSS** prevention with Content Security Policy

## 📊 Observability & Monitoring

### Metrics
- Prometheus scrapes metrics from all services
- Custom business metrics (orders, revenue, cart abandonment)
- Infrastructure metrics (CPU, memory, network, disk)
- Request latency and error rates

### Logging
- Structured JSON logging across all services
- Centralized logging with Loki
- Request correlation IDs for tracing
- Log rotation and retention policies

### Dashboards
Grafana dashboards for:
- Application performance (requests/sec, latency, errors)
- Business metrics (orders, revenue, user activity)
- Infrastructure health (node status, pod health)
- Database performance (query times, connections)

### Alerting
- Prometheus AlertManager
- Slack integration for notifications
- Email alerts for critical issues
- PagerDuty integration for on-call

## 🧪 Testing Strategy

```bash
# Unit Tests (Pytest)
pytest backend/services/*/tests/unit -v --cov

# Integration Tests
pytest backend/tests/integration -v

# End-to-End Tests (Playwright)
npm run e2e --prefix frontend

# Load Testing (K6)
k6 run load-tests/k6-scenarios.js

# Load Testing (Locust)
locust -f load-tests/locust-scenarios.py
```

## 📈 Performance Features

- **Caching Strategy**: Multi-layer caching (HTTP, Redis, DB query)
- **Async Processing**: RabbitMQ for background jobs
- **Circuit Breaker**: Graceful degradation on failures
- **Retry Mechanisms**: Exponential backoff with jitter
- **Pagination**: Cursor-based pagination for large datasets
- **Database Indexing**: Optimized indexes on all key columns
- **Connection Pooling**: Efficient database connection management
- **CDN**: Static assets served via Cloud CDN

## 🔄 Deployment Strategies

- **Rolling Updates**: Gradual service updates with zero downtime
- **Blue-Green Deployment**: Complete environment switches
- **Canary Deployment**: Risk-free rollouts with traffic splitting
- **Feature Flags**: Controlled feature releases
- **Automated Rollback**: On deployment failure

## 📚 Documentation

- [Architecture & Design Patterns](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Terraform Guide](infrastructure/gcp/terraform/README.md)
- [Kubernetes Guide](infrastructure/kubernetes/README.md)
- [Security Implementation](docs/security/README.md)
- [Troubleshooting Guide](docs/troubleshooting/README.md)
- [Testing Strategy](docs/testing/README.md)

## 💻 Development

### Code Standards
- Python: PEP 8, Black formatter, isort
- React: ESLint, Prettier, TypeScript strict mode
- Pre-commit hooks for code quality

### Contributing
1. Create feature branch from `develop`
2. Follow clean code principles and SOLID
3. Add unit tests (minimum 80% coverage)
4. Submit PR with detailed description
5. Code review required before merge

## 🚢 CI/CD Pipeline

GitHub Actions workflow:
1. **Lint** - Code style and formatting
2. **Unit Tests** - Run test suite
3. **Integration Tests** - End-to-end testing
4. **Security Scan** - Dependency and container scanning
5. **Build** - Docker image creation
6. **Push** - Push to Artifact Registry
7. **Deploy** - Deploy to GKE
8. **Smoke Tests** - Verify deployment
9. **Notify** - Slack notification

## 📊 Enterprise Features

✅ Microservices Architecture  
✅ Cloud-Native Design  
✅ Infrastructure as Code (Terraform)  
✅ Kubernetes Orchestration  
✅ CI/CD Pipeline  
✅ Comprehensive Monitoring  
✅ Centralized Logging  
✅ Enterprise Security  
✅ High Availability  
✅ Auto-Scaling  
✅ Disaster Recovery  
✅ API Rate Limiting  
✅ Authentication & Authorization  
✅ Graceful Shutdown  
✅ Health Checks  
✅ Load Testing  
✅ Production Ready  

## 🛠️ Infrastructure as Code

All infrastructure provisioned with Terraform:

```bash
cd infrastructure/gcp/terraform
terraform init
terraform plan
terraform apply
```

Provisioned resources:
- VPC with custom subnets
- Cloud NAT for secure egress
- GKE cluster with node pools
- Cloud SQL (PostgreSQL)
- Cloud Memorystore (Redis)
- Cloud Artifact Registry
- Cloud Load Balancer
- Cloud DNS
- IAM roles and service accounts

## 📞 Support & Contact

For questions or feedback: khayumm25@example.com

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

**Project Status**: ✅ Production Ready  
**Last Updated**: 2026-07-19  
**Version**: 1.0.0  
**Supported Python**: 3.11+  
**Supported Node**: 18+  
**Kubernetes Version**: 1.28+
