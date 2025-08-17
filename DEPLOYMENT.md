# Deployment Guide - Semantic Segmentation App

## 🚀 Quick Start

### Local Development
```bash
# Build and run the application
make build-run

# Or step by step
make build
make run

# Check status
make status
make logs
```

### Production Deployment
```bash
# Build production image
make prod-build

# Run production container
make prod-run
```

## 📋 Complete Setup

### 1. Environment Configuration

Create `.env/.env` file:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=eu-west-3

# DVC Configuration
DVC_S3_BUCKET=your-bucket-name

# API Configuration
API_BASE_URL=http://13.36.249.197:8000
```

### 2. DVC Setup
```bash
# Set up DVC with S3
make dvc-setup

# Push data to S3
make dvc-push
```

### 3. Build and Deploy
```bash
# Complete development setup
make setup

# Or manual steps
make build-run
```

## 🛠️ Available Commands

### Core Commands
- `make build` - Build Docker image
- `make run` - Run container
- `make build-run` - Build and run (default)
- `make stop` - Stop container
- `make logs` - Show logs
- `make status` - Show status

### DVC Commands
- `make dvc-setup` - Set up DVC with S3
- `make dvc-push` - Push data to S3
- `make dvc-pull` - Pull data from S3
- `make dvc-status` - Show DVC status

### Development Commands
- `make dev` - Complete development workflow
- `make dev-stop` - Stop development environment
- `make test` - Run tests
- `make test-local` - Test local app

### Production Commands
- `make prod-build` - Build production image
- `make prod-run` - Run production container
- `make ci-build` - Build for CI/CD
- `make ci-deploy` - Deploy for CI/CD

### Utility Commands
- `make clean` - Clean Docker resources
- `make clean-all` - Clean everything
- `make info` - Show build information
- `make health` - Check container health
- `make monitor` - Monitor resources
- `make shell` - Open container shell

## 🔧 Environment Variables

### Local Development
Variables are loaded from `.env/.env` file:
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_DEFAULT_REGION` - AWS region
- `DVC_S3_BUCKET` - S3 bucket name

### CI/CD (GitHub Actions)
Variables are loaded from GitHub secrets:
- `AWS_ACCESS_KEY_ID` - From secrets
- `AWS_SECRET_ACCESS_KEY` - From secrets
- `AWS_REGION` - From secrets
- `DVC_S3_BUCKET` - From secrets

## 🐳 Docker Configuration

### Image Details
- **Base Image**: Python 3.12-slim
- **Size**: ~1.14GB (without data)
- **Data**: Pulled from S3 via DVC
- **Port**: 8501

### Build Process
1. Install system dependencies
2. Install Python packages
3. Install DVC with S3 support
4. Copy application code
5. Create entrypoint script
6. Pull data from S3 at runtime

## ☁️ AWS Integration

### S3 Bucket
- **Purpose**: Store heavy image files
- **Access**: Via DVC
- **Cost**: Much cheaper than Docker registry

### ECR Repository
- **Purpose**: Store Docker images
- **Access**: Via CI/CD pipeline
- **Size**: Lightweight (no data included)

### EC2 Instance
- **Purpose**: Host application
- **Requirements**: Docker installed
- **Port**: 8501 exposed

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
1. **Test**: Validate dependencies
2. **Build**: Create Docker image
3. **Push**: Upload to ECR
4. **Deploy**: Deploy to EC2

### Secrets Required
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `DVC_S3_BUCKET`
- `EC2_HOST`
- `EC2_USERNAME`
- `EC2_SSH_KEY`

## 📊 Monitoring

### Health Checks
```bash
# Check container health
make health

# Monitor resources
make monitor

# View logs
make logs
```

### Troubleshooting
```bash
# Check status
make status

# View detailed info
make info

# Restart container
make restart
```

## 🚀 Performance

### Metrics
- **Docker Image Size**: 1.14GB
- **Data Size**: ~2GB (in S3)
- **Startup Time**: ~30 seconds
- **Memory Usage**: ~1GB RAM

### Benefits
- ✅ Lightweight Docker images
- ✅ Fast deployments
- ✅ Cost-effective storage
- ✅ Scalable architecture
- ✅ Version controlled data

## 🔒 Security

### Best Practices
- Environment variables for secrets
- `.env/` directory excluded from Docker builds
- AWS IAM roles for EC2
- S3 bucket policies
- Docker image scanning

### Access Control
- S3 bucket access via IAM
- ECR access via IAM
- EC2 access via SSH keys
- Application access via port 8501

## 📝 Examples

### Local Development
```bash
# Complete setup
make setup

# Build and run
make build-run

# Access app
open http://localhost:8501
```

### Production Deployment
```bash
# Build production image
make prod-build

# Deploy to production
make prod-run

# Monitor deployment
make monitor
```

### CI/CD Pipeline
```bash
# Push to main branch triggers:
# 1. Tests
# 2. Build
# 3. Push to ECR
# 4. Deploy to EC2
```

## 🆘 Troubleshooting

### Common Issues

1. **DVC data not found**
   ```bash
   make dvc-pull
   ```

2. **Docker build fails**
   ```bash
   make clean
   make build
   ```

3. **Container not starting**
   ```bash
   make logs
   make status
   ```

4. **Environment variables missing**
   ```bash
   # Check .env file
   cat .env/.env
   
   # Or set manually
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

### Support Commands
```bash
# Get help
make help

# Show information
make info

# Check health
make health

# View logs
make logs
```
