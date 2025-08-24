# 🎯 Semantic Image Segmentation App

A modern Streamlit application for semantic image segmentation using the Cityscapes dataset and a remote API. Built with a modular architecture following separation of concerns principles.

## 🏗️ Architecture Overview

- **Frontend**: Streamlit web application with modular UI components
- **Backend**: Remote API for segmentation processing
- **Data Storage**: DVC + AWS S3 for heavy image files
- **Deployment**: Docker + AWS EC2 with CI/CD pipeline
- **Architecture**: Modular design with clear separation of concerns

## 📁 Project Structure

```
Front-Semantic-Image_Segmentation/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application orchestrator
│   ├── config.py                # Centralized configuration
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── api_service.py       # API communication layer
│   │   └── data_service.py      # Data management layer
│   └── components/              # UI components
│       ├── __init__.py
│       └── ui_components.py     # Streamlit UI logic
├── app.py                       # Entry point (minimal)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── Makefile                     # Build and deployment automation
├── scripts/                     # Utility scripts
│   ├── build-and-run.sh        # Docker build and run
│   ├── deploy-to-ec2.sh        # EC2 deployment
│   ├── test-deployment.sh      # Deployment testing
│   └── verify-deployment.sh    # Deployment verification
├── tests/                       # Test suite
│   ├── test_api_service.py     # API service tests
│   ├── test_data_service.py    # Data service tests
│   └── test_config.py          # Configuration tests
├── .github/workflows/           # CI/CD pipelines
│   └── ci-cd-deploy.yml        # GitHub Actions workflow
├── leftImg8bit/                 # Original images (DVC tracked)
└── gtFine/                      # Ground truth masks (DVC tracked)
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Front-Semantic-Image_Segmentation
   ```

2. **Set up environment**
   ```bash
   # Create virtual environment
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Direct execution
   streamlit run app.py
   
   # Or using Docker
   make build-run
   ```

### Docker Development

```bash
# Build and run with Docker
make build-run

# Or step by step
make build
make run

# Check status
make status
make logs
```

## 🏗️ Modular Architecture

### **1. Configuration Layer (`app/config.py`)**
- **Responsibility**: Centralized configuration management
- **Features**: Environment variables, application settings, constants
- **Benefits**: Single source of truth, easy configuration changes

### **2. Service Layer (`app/services/`)**
- **API Service** (`api_service.py`): Handles all external API communications
- **Data Service** (`data_service.py`): Manages file operations and data access
- **Benefits**: Reusable business logic, testable components

### **3. UI Components Layer (`app/components/`)**
- **UI Components** (`ui_components.py`): Streamlit interface elements
- **Benefits**: Reusable UI components, consistent styling

### **4. Application Layer (`app/main.py`)**
- **Responsibility**: Orchestrates all components
- **Benefits**: Clean separation, easy to understand flow

## 🔄 Data Flow

```
User Input → UI Components → Main App → Services → External Systems
                ↓              ↓         ↓
            Display Results ← Main App ← Services
```

## ☁️ AWS Deployment Setup

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **EC2 Instance** with Docker installed
3. **S3 Bucket** for data storage
4. **ECR Repository** for Docker images

### Step 1: Environment Configuration

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

### Step 2: DVC Setup
```bash
# Set up DVC with S3
make dvc-setup

# Push data to S3
make dvc-push
```

### Step 3: Deploy

#### Automatic Deployment (Recommended)
```bash
# Push to main branch triggers CI/CD
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### Manual Deployment
```bash
# Build production image
make prod-build

# Run production container
make prod-run
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

## 🔧 Configuration

### Environment Variables

The application uses centralized configuration in `app/config.py`:

```python
# API Configuration
API_BASE_URL = "http://13.36.249.197:8000"

# Data Paths
ORIGINAL_IMAGES_DIR = "leftImg8bit/val/frankfurt"
GROUND_TRUTH_DIR = "gtFine/val/frankfurt"

# AWS Configuration
AWS_REGION = "eu-west-3"
DVC_S3_BUCKET = "frontend-semantic-image-segmentation"

# Application Settings
MAX_FILE_SIZE_MB = 10
REQUEST_TIMEOUT = 60
HEALTH_CHECK_TIMEOUT = 10
```

### DVC Configuration

The app uses DVC to manage large image files:
- **Data storage**: AWS S3 bucket
- **Version control**: Git tracks `.dvc` files
- **Local cache**: DVC caches data locally for fast access

## 🧪 Testing

### Test Structure
```
tests/
├── test_api_service.py     # API service unit tests
├── test_data_service.py    # Data service unit tests
└── test_config.py          # Configuration validation tests
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_api_service.py

# Run with coverage
pytest --cov=app tests/
```

## 📊 Features

- **Modular Architecture**: Clean separation of concerns
- **Image Selection**: Choose from Cityscapes dataset
- **File Upload**: Upload custom images for segmentation
- **Ground Truth Display**: Pre-colored segmentation masks
- **API Integration**: Remote segmentation prediction
- **Real-time Statistics**: Segmentation class percentages
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Comprehensive error management
- **Health Monitoring**: API and data directory validation

## 🚀 CI/CD Pipeline

The GitHub Actions workflow:

1. **Test**: Validates dependencies and code
2. **Build**: Creates Docker image and pushes to ECR
3. **Deploy**: Deploys to EC2 instance

### Required Secrets
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `DVC_S3_BUCKET`
- `EC2_HOST`
- `EC2_USERNAME`
- `EC2_SSH_KEY`

## 🔍 Troubleshooting

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

3. **API connection issues**
   ```bash
   make health
   make logs
   ```

4. **Environment variables missing**
   ```bash
   # Check .env file
   cat .env/.env
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

## 📈 Performance Metrics

- **Docker Image Size**: ~1.14GB
- **Data Size**: ~2GB (stored in S3)
- **Startup Time**: ~30 seconds
- **Memory Usage**: ~1GB RAM
- **Response Time**: <5 seconds for segmentation

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

## 🤝 Contributing

1. Follow the modular architecture principles
2. Add tests for new functionality
3. Update documentation as needed
4. Use the existing service patterns
5. Follow the established coding standards

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Streamlit, Docker, and AWS**