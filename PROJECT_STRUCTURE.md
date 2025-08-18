# Project Structure - Separation of Concerns

This document describes the refactored project structure following the separation of concerns principle.

## 📁 Directory Structure

```
Front-Semantic-Image_Segmentation/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application logic
│   ├── config.py                # Configuration management
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── api_service.py       # API communication
│   │   └── data_service.py      # Data management
│   └── components/              # UI components
│       ├── __init__.py
│       └── ui_components.py     # Streamlit UI logic
├── app.py                       # Entry point (minimal)
├── requirements.txt             # Dependencies
├── Dockerfile                   # Container configuration
├── scripts/                     # Utility scripts
│   ├── deploy-to-ec2.sh
│   ├── test-deployment.sh
│   └── verify-deployment.sh
└── .github/workflows/           # CI/CD pipelines
    └── ci-cd-deploy.yml
```

## 🏗️ Architecture Overview

### **1. Configuration Layer (`app/config.py`)**
- **Responsibility**: Centralized configuration management
- **Concerns**: Environment variables, application settings, constants
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

## 📋 Separation of Concerns

### **Configuration Concerns**
- ✅ Environment variables
- ✅ Application settings
- ✅ API endpoints
- ✅ File paths

### **API Communication Concerns**
- ✅ HTTP requests/responses
- ✅ Error handling
- ✅ Response parsing
- ✅ Authentication

### **Data Management Concerns**
- ✅ File operations
- ✅ Directory validation
- ✅ Image loading
- ✅ Data statistics

### **UI Concerns**
- ✅ Streamlit components
- ✅ User interaction
- ✅ Display logic
- ✅ Error messages

### **Application Logic Concerns**
- ✅ Workflow orchestration
- ✅ State management
- ✅ Error handling
- ✅ User experience

## 🚀 Benefits of This Structure

### **1. Maintainability**
- Each module has a single responsibility
- Easy to locate and fix issues
- Clear dependencies between components

### **2. Testability**
- Services can be unit tested independently
- Mock external dependencies easily
- Isolated UI component testing

### **3. Scalability**
- Easy to add new services
- Simple to extend UI components
- Modular configuration management

### **4. Reusability**
- Services can be reused across different parts
- UI components are modular
- Configuration is centralized

### **5. Readability**
- Clear file organization
- Descriptive module names
- Consistent coding patterns

## 🔧 Usage Examples

### **Adding a New Service**
```python
# app/services/new_service.py
class NewService:
    def __init__(self):
        # Service initialization
    
    def do_something(self):
        # Business logic
```

### **Adding a New UI Component**
```python
# app/components/new_ui_components.py
class NewUIComponents:
    @staticmethod
    def create_new_widget():
        # UI logic
```

### **Updating Configuration**
```python
# app/config.py
class Config:
    NEW_SETTING = os.getenv("NEW_SETTING", "default_value")
```

## 🧪 Testing Strategy

### **Unit Tests**
- Test each service independently
- Mock external dependencies
- Test configuration validation

### **Integration Tests**
- Test service interactions
- Test API communication
- Test data flow

### **UI Tests**
- Test UI component rendering
- Test user interactions
- Test error handling

## 📝 Best Practices

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Injection**: Services receive dependencies as parameters
3. **Error Handling**: Consistent error handling across all layers
4. **Documentation**: Clear docstrings and comments
5. **Type Hints**: Use type hints for better code clarity
6. **Constants**: Use configuration for magic numbers and strings

## 🔄 Migration Guide

### **From Monolithic to Modular**
1. Extract configuration to `config.py`
2. Move API logic to `api_service.py`
3. Move data logic to `data_service.py`
4. Extract UI components to `ui_components.py`
5. Create main application orchestrator
6. Update imports and dependencies

This structure provides a solid foundation for future development and maintenance! 🚀
