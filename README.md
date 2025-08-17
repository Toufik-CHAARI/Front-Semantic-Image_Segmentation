# Front end Semantic Image Segmentation App

A Streamlit application for testing semantic image segmentation using the Cityscapes dataset and a remote API.

## 🏗️ Architecture

- **Frontend**: Streamlit web application
- **Backend**: Remote API for segmentation
- **Data Storage**: DVC + AWS S3 for heavy image files
- **Deployment**: Docker + AWS EC2 with CI/CD pipeline

## 🚀 Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Front-Semantic-Image_Segmentation
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

## ☁️ AWS Deployment Setup

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **EC2 Instance** with Docker installed
3. **S3 Bucket** for data storage
4. **ECR Repository** for Docker images

### Step 1: Set up S3 Bucket

1. Create an S3 bucket for data storage
2. Configure bucket permissions for DVC access
3. Set the bucket name in your `.env/.env` file:
   ```
   DVC_S3_BUCKET=your-bucket-name
   ```

### Step 2: Set up DVC with S3

1. **Install DVC locally**
   ```bash
   pip install dvc[s3]
   ```

2. **Set AWS credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=your region (us-east-1 for example)
   ```

3. **Initialize DVC and push data**
   ```bash
   chmod +x scripts/setup-dvc.sh
   ./scripts/setup-dvc.sh
   ```

4. **Commit DVC files**
   ```bash
   git add .dvc/
   git commit -m "Add DVC configuration"
   ```

### Step 3: Set up EC2 Instance

1. **Launch EC2 instance** (t3.medium or larger recommended)
2. **Install Docker**
   ```bash
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```

3. **Configure security group** to allow port 8501

### Step 4: Set up GitHub Secrets

Add these secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `EC2_HOST`: Your EC2 public IP
- `EC2_USERNAME`: ec2-user (or your EC2 username)
- `EC2_SSH_KEY`: Your EC2 private key

### Step 5: Deploy

1. **Push to main branch** - CI/CD will automatically deploy
2. **Or deploy manually**:
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

## 📁 Project Structure

```
Front-Semantic-Image_Segmentation/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .dockerignore         # Docker ignore file
├── dvc.yaml             # DVC pipeline configuration
├── .dvcignore           # DVC ignore file
├── .github/
│   └── workflows/
│       └── deploy.yml    # CI/CD pipeline
├── scripts/
│   ├── setup-dvc.sh     # DVC setup script
│   └── deploy.sh        # Deployment script
├── leftImg8bit/         # Original images (tracked by DVC)
└── gtFine/              # Ground truth masks (tracked by DVC)
```

## 🔧 Configuration

### Environment Variables

Create a `.env/.env` file with the following variables:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# DVC Configuration
DVC_S3_BUCKET=your-bucket-name

# API Configuration
API_BASE_URL=http://13.36.249.197:8000
```

### DVC Configuration

The app uses DVC to manage large image files:

- **Data storage**: AWS S3 bucket
- **Version control**: Git tracks `.dvc` files
- **Local cache**: DVC caches data locally for fast access

## 🚀 CI/CD Pipeline

The GitHub Actions workflow:

1. **Test**: Validates dependencies and code
2. **Build**: Creates Docker image and pushes to ECR
3. **Deploy**: Deploys to EC2 instance

## 📊 Features

- **Image Selection**: Choose from Cityscapes dataset
- **Ground Truth Display**: Pre-colored segmentation masks
- **API Integration**: Remote segmentation prediction
- **Real-time Statistics**: Segmentation class percentages
- **Responsive Design**: Works on desktop and mobile

## 🔍 Troubleshooting

### Common Issues

1. **DVC data not found**
   ```bash
   dvc pull  # Pull data from S3
   ```

2. **Docker build fails**
   ```bash
   docker system prune -a  # Clean Docker cache
   ```

3. **EC2 deployment fails**
   - Check security group settings
   - Verify AWS credentials
   - Check Docker logs: `docker logs semantic-segmentation-app`

### Logs

- **Application logs**: `docker logs semantic-segmentation-app`