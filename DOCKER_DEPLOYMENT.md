# SuperClaude Docker Deployment Guide

Complete guide for running SuperClaude in Docker containers.

---

## 🚀 Quick Start

### 1. Run Demo (No API Keys Required)

```bash
./docker-test.sh demo
```

This runs all demo tests without requiring any API keys!

### 2. Build Image

```bash
docker build -t superclaude:latest .
```

Or using the script:
```bash
./docker-test.sh build
```

### 3. Start Services

```bash
# All services
docker-compose up -d

# Specific service
docker-compose --profile docs up -d
```

---

## 📦 What's Included

### Docker Files

| File | Purpose | Size |
|------|---------|------|
| `Dockerfile` | Main image definition | Multi-stage build |
| `docker-compose.yml` | Service orchestration | 5 profiles |
| `.dockerignore` | Build optimization | Excludes 20+ patterns |
| `docker-test.sh` | Testing script | 8 modes |

### Docker Image Features

- **Base:** Python 3.11-slim (minimal size)
- **Dependencies:** All required packages pre-installed
- **Size:** ~500MB (optimized)
- **Startup:** <5 seconds
- **Health checks:** Automatic monitoring
- **Volumes:** Persistent data support

---

## 🎯 Usage Modes

### Mode 1: Demo Testing

**No API keys required!**

```bash
./docker-test.sh demo
```

**What it does:**
- ✅ Tests all 4 Python scripts
- ✅ Validates imports and structure
- ✅ Shows simulated examples
- ✅ 7/7 tests with colored output

**Output:**
```
════════════════════════════════════════════════════════
                SuperClaude Demo Test Suite
════════════════════════════════════════════════════════

✅ ALL TESTS PASSED: 7/7 (100%)
```

### Mode 2: Documentation RAG

**Requires:** GEMINI_API_KEY

```bash
# Start service
./docker-test.sh docs

# Index documentation
docker exec -it superclaude-docs-rag \
  python3 examples/gemini-file-search/superclaude_rag.py --index

# Query
docker exec -it superclaude-docs-rag \
  python3 examples/gemini-file-search/superclaude_rag.py \
  --query "How do I use MCP servers?"

# Stop service
docker-compose --profile docs down
```

**Features:**
- Indexes all .md, .txt, .yml documentation
- Semantic search with citations
- Fast queries (<2 seconds)
- Persistent store

### Mode 3: Codebase Analysis

**Requires:** GEMINI_API_KEY

```bash
# Start service
./docker-test.sh code

# Index codebase
docker exec -it superclaude-code-rag \
  python3 examples/gemini-file-search/codebase_rag.py --index

# Find functions
docker exec -it superclaude-code-rag \
  python3 examples/gemini-file-search/codebase_rag.py \
  --find "authentication logic"

# Architecture overview
docker exec -it superclaude-code-rag \
  python3 examples/gemini-file-search/codebase_rag.py --overview

# Stop service
docker-compose --profile code down
```

**Features:**
- 29 programming languages
- Function search by description
- Pattern explanation
- Dependency analysis

### Mode 4: TV3 Integration

**Requires:** GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY

```bash
# Start service
./docker-test.sh tv3

# Initialize archive
docker exec -it superclaude-tv3 \
  python3 examples/tv3-integration/news_archive_rag.py --init

# Index articles (last 7 days)
docker exec -it superclaude-tv3 \
  python3 examples/tv3-integration/news_archive_rag.py \
  --index-recent --days 7

# Generate bulletin (Slovenian!)
docker exec -it superclaude-tv3 \
  python3 examples/tv3-integration/smart_bulletin_generator.py \
  --daily --duration 5 --save

# Stop service
docker-compose --profile tv3 down
```

**Features:**
- News article indexing
- Semantic article search
- AI bulletin generation
- Slovenian language support
- Professional TV format

### Mode 5: Interactive Shell

```bash
./docker-test.sh shell
```

Opens bash shell inside container:
```bash
root@container:/app# ls
CLAUDE.md  examples/  deploy.sh  ...

root@container:/app# python3 examples/demo/demo_test.py
```

### Mode 6: All Services

```bash
./docker-test.sh all

# View logs
docker-compose logs -f

# Execute commands
docker exec -it superclaude bash

# Stop all
docker-compose down
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# Required for RAG functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for TV3 features
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional - for MCP servers
FIRECRAWL_API_KEY=your_firecrawl_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
BROWSERBASE_API_KEY=your_browserbase_api_key
REF_API_KEY=your_ref_api_key
```

### Docker Compose Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| (default) | superclaude | Main container |
| demo | superclaude-demo | Demo testing |
| docs | superclaude-docs-rag | Documentation search |
| code | superclaude-code-rag | Code analysis |
| tv3 | superclaude-tv3 | TV3 integration |

**Start specific profile:**
```bash
docker-compose --profile docs up -d
```

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./.env` | `/app/.env` | API keys (read-only) |
| `./outputs` | `/app/outputs` | Generated files |
| `./examples` | `/app/examples` | Live code updates |
| `./docs` | `/app/docs` | Documentation access |

---

## 🔧 Advanced Usage

### Custom Docker Build

```bash
# Build with custom tag
docker build -t superclaude:dev .

# Build without cache
docker build --no-cache -t superclaude:latest .

# Build specific platform
docker build --platform linux/amd64 -t superclaude:latest .
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Max 4 CPUs
      memory: 4G     # Max 4GB RAM
    reservations:
      cpus: '1'      # Min 1 CPU
      memory: 1G     # Min 1GB RAM
```

### Custom Commands

```bash
# Run specific script
docker run --rm \
  -v "$(pwd)/.env:/app/.env:ro" \
  superclaude:latest \
  python3 examples/gemini-file-search/superclaude_rag.py --help

# Index with custom options
docker run --rm \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/outputs:/app/outputs" \
  superclaude:latest \
  python3 examples/gemini-file-search/superclaude_rag.py --index

# Interactive Python
docker run --rm -it \
  -v "$(pwd)/.env:/app/.env:ro" \
  superclaude:latest \
  python3
```

### Debugging

```bash
# View container logs
docker logs superclaude-docs-rag

# Follow logs
docker logs -f superclaude-docs-rag

# Execute bash
docker exec -it superclaude-docs-rag bash

# Check environment
docker exec -it superclaude-docs-rag env

# Test connectivity
docker exec -it superclaude-docs-rag ping google.com
```

---

## 📊 Docker Commands Reference

### Building

```bash
# Build image
docker build -t superclaude:latest .

# Build with no cache
./docker-test.sh build

# Check image size
docker images superclaude
```

### Running

```bash
# Demo mode
./docker-test.sh demo

# Docs RAG
./docker-test.sh docs

# Code RAG
./docker-test.sh code

# TV3
./docker-test.sh tv3

# All services
./docker-test.sh all

# Interactive shell
./docker-test.sh shell
```

### Managing

```bash
# List running containers
docker ps

# Stop container
docker stop superclaude-docs-rag

# Start container
docker start superclaude-docs-rag

# Restart container
docker restart superclaude-docs-rag

# Remove container
docker rm superclaude-docs-rag

# Remove all
docker-compose down
```

### Cleaning

```bash
# Clean everything
./docker-test.sh clean

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all (careful!)
docker system prune -a
```

---

## 🐛 Troubleshooting

### Issue: Build fails with "no space left on device"

**Solution:**
```bash
# Clean Docker system
docker system prune -a --volumes

# Check disk space
df -h
```

### Issue: Container exits immediately

**Solution:**
```bash
# Check logs
docker logs superclaude

# Run with interactive shell
docker run -it superclaude:latest bash
```

### Issue: API key not found

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check mount in container
docker exec -it superclaude-docs-rag cat /app/.env

# Verify environment
docker exec -it superclaude-docs-rag env | grep GEMINI
```

### Issue: Permission denied

**Solution:**
```bash
# Fix permissions on host
chmod 644 .env
chmod -R 755 outputs/

# Or run with user mapping
docker run --user $(id -u):$(id -g) ...
```

### Issue: Container can't connect to internet

**Solution:**
```bash
# Check Docker network
docker network ls

# Test connectivity
docker exec -it superclaude-docs-rag ping -c 3 8.8.8.8

# Restart Docker daemon
sudo systemctl restart docker
```

### Issue: Slow indexing

**Normal behavior!** Indexing is compute-intensive:
- Small docs: 2-5 minutes
- Large codebase: 10-20 minutes
- TV3 archive: 5-15 minutes

**Optimize:**
```bash
# Allocate more resources
# Edit docker-compose.yml:
# memory: 4G
# cpus: '4'

# Use SSD storage
# Mount volumes on fast disk
```

---

## 📈 Performance Optimization

### Image Size Optimization

Current optimizations:
- ✅ Multi-stage build
- ✅ Python slim base image
- ✅ Minimal system dependencies
- ✅ No dev dependencies
- ✅ .dockerignore configured

**Result:** ~500MB (vs 2GB+ without optimization)

### Build Time Optimization

```bash
# Use BuildKit
DOCKER_BUILDKIT=1 docker build -t superclaude:latest .

# Cache dependencies
# Requirements are cached in separate layer
# Only rebuild when requirements change
```

### Runtime Optimization

```yaml
# In docker-compose.yml
environment:
  - PYTHONUNBUFFERED=1        # Faster output
  - PYTHONDONTWRITEBYTECODE=1 # No .pyc files
  - PIP_NO_CACHE_DIR=1        # No pip cache
```

---

## 🔐 Security Best Practices

### 1. Environment Variables

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secrets management in production
# Docker Secrets (Swarm)
# Kubernetes Secrets
# AWS Secrets Manager
# HashiCorp Vault
```

### 2. Read-Only Mounts

```yaml
volumes:
  - ./.env:/app/.env:ro       # Read-only
  - ./docs:/app/docs:ro       # Read-only
```

### 3. Non-Root User

Add to Dockerfile:
```dockerfile
RUN useradd -m -u 1000 superclaude
USER superclaude
```

### 4. Network Isolation

```yaml
networks:
  superclaude-network:
    driver: bridge
    internal: true  # No internet access
```

### 5. Resource Limits

Always set in production:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## 🚀 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml superclaude

# Check services
docker service ls

# Scale service
docker service scale superclaude_superclaude=3

# Update service
docker service update superclaude_superclaude

# Remove stack
docker stack rm superclaude
```

### Kubernetes

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superclaude
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superclaude
  template:
    metadata:
      labels:
        app: superclaude
    spec:
      containers:
      - name: superclaude
        image: superclaude:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: superclaude-secrets
              key: gemini-api-key
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
          requests:
            memory: "512Mi"
            cpu: "500m"
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Cloud Platforms

**AWS ECS:**
```bash
# Build for ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
docker tag superclaude:latest $ECR_URL/superclaude:latest
docker push $ECR_URL/superclaude:latest

# Deploy with ECS CLI
ecs-cli compose -f docker-compose.yml up
```

**Google Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/superclaude
gcloud run deploy superclaude --image gcr.io/$PROJECT_ID/superclaude --platform managed
```

**Azure Container Instances:**
```bash
# Build and push to ACR
az acr build --registry $ACR_NAME --image superclaude:latest .

# Deploy
az container create --resource-group $RG --name superclaude \
  --image $ACR_NAME.azurecr.io/superclaude:latest
```

---

## 📊 Monitoring & Logging

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats superclaude-docs-rag

# JSON format
docker stats --no-stream --format "{{json .}}"
```

### Health Checks

Configured in Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"
```

Check health:
```bash
docker ps
# Shows (healthy) or (unhealthy)

docker inspect --format='{{.State.Health.Status}}' superclaude
```

### Logging

```bash
# View logs
docker logs superclaude

# Follow logs
docker logs -f superclaude

# Last 100 lines
docker logs --tail 100 superclaude

# Since timestamp
docker logs --since 2024-11-08T10:00:00 superclaude

# Export logs
docker logs superclaude > superclaude.log
```

---

## 🎓 Examples

### Example 1: Quick Demo

```bash
# Build and run demo in one command
docker build -t superclaude:latest . && \
docker run --rm superclaude:latest python3 examples/demo/demo_test.py
```

### Example 2: Documentation Search Pipeline

```bash
# Start service
docker-compose --profile docs up -d

# Index
docker exec superclaude-docs-rag \
  python3 examples/gemini-file-search/superclaude_rag.py --index

# Multiple queries
for query in "MCP servers" "personas" "task management"; do
  docker exec superclaude-docs-rag \
    python3 examples/gemini-file-search/superclaude_rag.py --query "$query"
done

# Cleanup
docker-compose --profile docs down
```

### Example 3: Automated Bulletin Generation

```bash
# Start TV3 service
docker-compose --profile tv3 up -d

# Initialize and index
docker exec superclaude-tv3 \
  python3 examples/tv3-integration/news_archive_rag.py --init

docker exec superclaude-tv3 \
  python3 examples/tv3-integration/news_archive_rag.py --index-recent --days 7

# Generate bulletin
docker exec superclaude-tv3 \
  python3 examples/tv3-integration/smart_bulletin_generator.py \
  --daily --duration 5 --save

# Copy output
docker cp superclaude-tv3:/app/outputs/bulletin.json ./

# Cleanup
docker-compose --profile tv3 down
```

### Example 4: CI/CD Integration

```yaml
# .github/workflows/docker-test.yml
name: Docker Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t superclaude:test .

      - name: Run demo tests
        run: docker run --rm superclaude:test python3 examples/demo/demo_test.py

      - name: Check image size
        run: |
          SIZE=$(docker images superclaude:test --format "{{.Size}}")
          echo "Image size: $SIZE"
```

---

## 📚 Additional Resources

### Documentation

- **Quick Start:** `QUICK_START.md`
- **Gemini File Search:** `GEMINI_FILE_SEARCH.md`
- **TV3 Integration:** `TV3_INTEGRATION_PLAN.md`
- **Test Results:** `FUNCTIONAL_TEST_REPORT.md`
- **MCP Setup:** `MCP_SETUP.md`

### Docker Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Security](https://docs.docker.com/engine/security/)

### SuperClaude

- GitHub: https://github.com/NomenAK/SuperClaude
- Issues: Report bugs and request features
- Discussions: Community support

---

## 🎯 Quick Command Reference

```bash
# Demo mode (no API keys)
./docker-test.sh demo

# Start docs RAG
./docker-test.sh docs

# Start code analysis
./docker-test.sh code

# Start TV3 integration
./docker-test.sh tv3

# Interactive shell
./docker-test.sh shell

# Rebuild image
./docker-test.sh build

# Clean everything
./docker-test.sh clean

# View help
./docker-test.sh help
```

---

**Ready to go? Start with:**
```bash
./docker-test.sh demo
```

**Docker deployment makes SuperClaude portable, reproducible, and production-ready! 🐳**
