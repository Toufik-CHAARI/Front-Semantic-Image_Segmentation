# 🏗️ Project Architecture - Technical Details

This document provides detailed technical information about the modular architecture and implementation patterns used in the Semantic Image Segmentation application.

## 📁 Detailed Directory Structure

```
Front-Semantic-Image_Segmentation/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application orchestrator (269 lines)
│   ├── config.py                # Centralized configuration (51 lines)
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── api_service.py       # API communication layer (142 lines)
│   │   └── data_service.py      # Data management layer (191 lines)
│   └── components/              # UI components
│       ├── __init__.py
│       └── ui_components.py     # Streamlit UI logic (230 lines)
├── app.py                       # Entry point (9 lines)
├── requirements.txt             # Python dependencies (142 lines)
├── Dockerfile                   # Container configuration (75 lines)
├── Makefile                     # Build automation (339 lines)
├── scripts/                     # Utility scripts
│   ├── build-and-run.sh        # Docker build and run
│   ├── deploy-to-ec2.sh        # EC2 deployment
│   ├── test-deployment.sh      # Deployment testing
│   └── verify-deployment.sh    # Deployment verification
├── tests/                       # Test suite
│   ├── test_api_service.py     # API service tests (196 lines)
│   ├── test_data_service.py    # Data service tests (235 lines)
│   └── test_config.py          # Configuration tests (69 lines)
├── .github/workflows/           # CI/CD pipelines
│   └── ci-cd-deploy.yml        # GitHub Actions workflow
├── leftImg8bit/                 # Original images (DVC tracked)
└── gtFine/                      # Ground truth masks (DVC tracked)
```

## 🏛️ Architecture Patterns

### **1. Layered Architecture**
The application follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────┐
│           UI Layer                  │  ← Streamlit Components
├─────────────────────────────────────┤
│        Application Layer            │  ← Main Orchestrator
├─────────────────────────────────────┤
│         Service Layer               │  ← Business Logic
├─────────────────────────────────────┤
│      Configuration Layer            │  ← Settings & Constants
└─────────────────────────────────────┘
```

### **2. Service-Oriented Design**
Each service has a single responsibility and can be tested independently:

- **APIService**: Handles all external HTTP communications
- **DataService**: Manages file operations and data access
- **UIComponents**: Provides reusable UI elements

### **3. Dependency Injection**
Services receive their dependencies through configuration:

```python
# Example: APIService uses config for settings
class APIService:
    def __init__(self) -> None:
        self.base_url = config.API_BASE_URL
        self.timeout = config.REQUEST_TIMEOUT
```

## 🔄 Data Flow Architecture

### **Request Flow**
```
1. User Input → UI Components
2. UI Components → Main App
3. Main App → Services
4. Services → External Systems (API, File System)
5. External Systems → Services
6. Services → Main App
7. Main App → UI Components
8. UI Components → User Display
```

### **Error Handling Flow**
```
Exception → Service Layer → Main App → UI Components → User
```

## 📋 Module Responsibilities

### **Configuration Module (`app/config.py`)**
```python
class Config:
    # API Configuration
    API_BASE_URL = "http://13.36.249.197:8000"
    
    # Data Paths
    ORIGINAL_IMAGES_DIR = "leftImg8bit/val/frankfurt"
    GROUND_TRUTH_DIR = "gtFine/val/frankfurt"
    
    # Application Settings
    MAX_FILE_SIZE_MB = 10
    REQUEST_TIMEOUT = 60
```

**Responsibilities:**
- ✅ Environment variable management
- ✅ Application constants
- ✅ Configuration validation
- ✅ URL construction utilities

### **API Service (`app/services/api_service.py`)**
```python
class APIService:
    def check_health(self) -> bool
    def predict_mask(self, image_path: str) -> Tuple[Image, Dict]
```

**Responsibilities:**
- ✅ HTTP request/response handling
- ✅ API health monitoring
- ✅ Error handling and retry logic
- ✅ Response parsing and validation
- ✅ File upload management

### **Data Service (`app/services/data_service.py`)**
```python
class DataService:
    def get_available_images(self) -> List[str]
    def load_image(self, image_path: str) -> Optional[Image]
    def validate_data_directories(self) -> Tuple[bool, List[str]]
```

**Responsibilities:**
- ✅ File system operations
- ✅ Image loading and validation
- ✅ Directory structure validation
- ✅ Data statistics and metadata
- ✅ Path management

### **UI Components (`app/components/ui_components.py`)**
```python
class UIComponents:
    @staticmethod
    def setup_page() -> None
    @staticmethod
    def display_header() -> None
    @staticmethod
    def create_image_selector(images: List[str]) -> Optional[str]
```

**Responsibilities:**
- ✅ Streamlit page configuration
- ✅ UI component creation
- ✅ User interaction handling
- ✅ Display logic and formatting
- ✅ Error message presentation

### **Main Application (`app/main.py`)**
```python
def main() -> None:
    initialize_app()
    check_system_status()
    handle_image_selection()
    perform_segmentation()
    display_results()
```

**Responsibilities:**
- ✅ Application orchestration
- ✅ Workflow management
- ✅ State coordination
- ✅ Error handling coordination
- ✅ User experience flow

## 🧪 Testing Architecture

### **Test Structure**
```
tests/
├── test_api_service.py     # API service unit tests
│   ├── test_check_health()
│   ├── test_predict_mask()
│   └── test_error_handling()
├── test_data_service.py    # Data service unit tests
│   ├── test_get_available_images()
│   ├── test_load_image()
│   └── test_validate_directories()
└── test_config.py          # Configuration tests
    ├── test_config_validation()
    └── test_url_construction()
```

### **Testing Patterns**
- **Unit Tests**: Test individual service methods
- **Mocking**: External dependencies are mocked
- **Integration Tests**: Test service interactions
- **Configuration Tests**: Validate settings and constants

## 🔧 Configuration Management

### **Environment Variables**
```bash
# Required for deployment
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=eu-west-3
DVC_S3_BUCKET=your-bucket-name
API_BASE_URL=http://13.36.249.197:8000

# Optional with defaults
MAX_FILE_SIZE_MB=10
REQUEST_TIMEOUT=60
HEALTH_CHECK_TIMEOUT=10
```

### **Configuration Validation**
```python
@classmethod
def validate_config(cls) -> bool:
    required_vars = [
        cls.API_BASE_URL,
        cls.ORIGINAL_IMAGES_DIR,
        cls.GROUND_TRUTH_DIR,
    ]
    return all(var for var in required_vars)
```

## 🚀 Deployment Architecture

### **Docker Configuration**
```dockerfile
# Multi-stage build for optimization
FROM python:3.12-slim as builder
# ... build dependencies

FROM python:3.12-slim as runtime
# ... runtime configuration
```

### **Makefile Automation**
```makefile
# Development commands
make build-run    # Build and run container
make test         # Run test suite
make clean        # Clean resources

# Production commands
make prod-build   # Build production image
make prod-run     # Run production container
```

## 📊 Code Quality Metrics

### **Lines of Code by Module**
- **main.py**: 269 lines (Application orchestration)
- **api_service.py**: 142 lines (API communication)
- **data_service.py**: 191 lines (Data management)
- **ui_components.py**: 230 lines (UI logic)
- **config.py**: 51 lines (Configuration)
- **Total Application Code**: 883 lines

### **Test Coverage**
- **API Service**: 196 lines of tests
- **Data Service**: 235 lines of tests
- **Configuration**: 69 lines of tests
- **Total Test Code**: 500 lines

## 🔄 Migration Patterns

### **From Monolithic to Modular**
1. **Extract Configuration**: Move settings to `config.py`
2. **Create Services**: Separate business logic into service classes
3. **Extract UI Components**: Move UI logic to component classes
4. **Create Main Orchestrator**: Centralize application flow
5. **Update Imports**: Refactor import statements
6. **Add Tests**: Create comprehensive test suite

### **Benefits Achieved**
- ✅ **Maintainability**: Each module has single responsibility
- ✅ **Testability**: Services can be unit tested independently
- ✅ **Scalability**: Easy to add new services and components
- ✅ **Reusability**: Services can be reused across different parts
- ✅ **Readability**: Clear file organization and naming

## 🎯 Best Practices Implemented

### **1. Single Responsibility Principle**
Each module has one clear purpose and responsibility.

### **2. Dependency Injection**
Services receive dependencies through configuration rather than creating them.

### **3. Error Handling**
Consistent error handling patterns across all layers.

### **4. Type Hints**
Comprehensive type hints for better code clarity and IDE support.

### **5. Documentation**
Clear docstrings and comments explaining complex logic.

### **6. Testing**
Comprehensive test coverage with mocking of external dependencies.

This architecture provides a solid foundation for future development and maintenance! 🚀
