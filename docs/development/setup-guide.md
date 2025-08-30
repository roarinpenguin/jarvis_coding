# Detailed Development Environment Setup

This guide provides comprehensive instructions for setting up your development environment for the Jarvis Coding platform.

## 📋 System Requirements

### Minimum Requirements
- **OS**: macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for code + dependencies
- **Network**: Internet connection for API calls

### Recommended Development Tools
- **IDE**: VS Code with Python extension
- **Terminal**: iTerm2 (macOS), Windows Terminal, or default Linux terminal
- **Git GUI**: GitHub Desktop, SourceTree, or GitKraken (optional)
- **API Testing**: Postman or Insomnia (for Phase 2)

## 🐍 Python Environment Setup

### Step 1: Install Python

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
# Output: Python 3.11.x
```

#### Ubuntu/Debian
```bash
# Update packages
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3 --version
```

#### Windows
1. Download from [python.org](https://python.org)
2. Run installer (check "Add Python to PATH")
3. Verify in PowerShell:
```powershell
python --version
```

### Step 2: Set Up Virtual Environment

Virtual environments isolate project dependencies:

```bash
# Navigate to project root
cd jarvis_coding

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Your prompt should now show (.venv)
```

### Step 3: Install Dependencies

```bash
# Core dependencies
pip install -r event_generators/shared/requirements.txt

# Development dependencies (for testing and linting)
pip install pytest pytest-cov black flake8 mypy

# Documentation dependencies (optional)
pip install mkdocs mkdocs-material sphinx
```

### Step 4: Verify Python Path

```bash
# Check Python is from virtual environment
which python
# Should show: /path/to/jarvis_coding/.venv/bin/python

# On Windows:
where python
# Should show: C:\path\to\jarvis_coding\.venv\Scripts\python.exe
```

## 🔐 Environment Configuration

### Create Local Configuration File

```bash
# Create .env file for local settings
cat > .env << 'EOF'
# SentinelOne API Configuration
S1_HEC_TOKEN=1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7
S1_SDL_API_TOKEN=your-sdl-api-token-here

# Environment Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Generator Settings
DEFAULT_EVENT_COUNT=10
DEFAULT_FORMAT=json
STAR_TREK_THEME=true

# API Settings (Phase 2)
API_HOST=localhost
API_PORT=8000
EOF
```

### Load Environment Variables

```bash
# Load manually
export $(cat .env | xargs)

# Or use python-dotenv
pip install python-dotenv

# In your Python scripts:
from dotenv import load_dotenv
load_dotenv()
```

## 🛠️ VS Code Configuration

### Recommended Extensions

Create `.vscode/extensions.json`:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".venv": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

### Launch Configuration

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Generator",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "HEC Sender",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/event_generators/shared/hec_sender.py",
      "args": ["--product", "crowdstrike_falcon", "--count", "5"],
      "console": "integratedTerminal"
    },
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

## 🧪 Testing Setup

### Install Testing Framework

```bash
# Testing dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Create test configuration
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
EOF
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=event_generators --cov-report=html

# Run specific test file
pytest tests/test_generators.py

# Run tests matching pattern
pytest -k "test_crowdstrike"
```

## 🔍 Code Quality Tools

### Set Up Linting

```bash
# Install linters
pip install flake8 black isort mypy

# Create flake8 configuration
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .venv,__pycache__,docs,build,dist
EOF

# Create black configuration
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
EOF
```

### Run Code Quality Checks

```bash
# Format code with black
black event_generators/

# Sort imports
isort event_generators/

# Check with flake8
flake8 event_generators/

# Type checking with mypy
mypy event_generators/
```

## 🐳 Docker Setup (Optional)

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY event_generators/shared/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "event_generators/shared/hec_sender.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  generator:
    build: .
    environment:
      - S1_HEC_TOKEN=${S1_HEC_TOKEN}
      - S1_SDL_API_TOKEN=${S1_SDL_API_TOKEN}
    volumes:
      - ./event_generators:/app/event_generators
      - ./scenarios:/app/scenarios
    command: python event_generators/shared/hec_sender.py --product crowdstrike_falcon --count 10
```

### Run with Docker

```bash
# Build image
docker build -t jarvis-coding .

# Run generator
docker run -e S1_HEC_TOKEN=$S1_HEC_TOKEN jarvis-coding \
  python event_generators/endpoint_security/crowdstrike_falcon.py
```

## 📦 Git Configuration

### Set Up Git Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF

# Install git hooks
pre-commit install
```

## 🔧 Troubleshooting Common Setup Issues

### Python Version Issues

```bash
# Problem: Wrong Python version
# Solution: Use pyenv to manage versions
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv local 3.11.0
```

### Permission Errors

```bash
# Problem: Permission denied installing packages
# Solution: Never use sudo with pip, use virtual environment
deactivate  # If in a venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Module Import Errors

```bash
# Problem: ModuleNotFoundError
# Solution: Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or in .env file:
PYTHONPATH=/path/to/jarvis_coding
```

### SSL Certificate Errors

```bash
# Problem: SSL verification failed
# Solution: Update certificates
pip install --upgrade certifi

# Or temporarily (not recommended for production):
export PYTHONHTTPSVERIFY=0
```

## ✅ Verify Complete Setup

Run this verification script:

```bash
# Create verify_setup.py
cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
import sys
import importlib

def check_setup():
    checks = []
    
    # Check Python version
    py_version = sys.version_info
    checks.append(("Python 3.8+", py_version >= (3, 8)))
    
    # Check required modules
    modules = ['requests', 'json', 'datetime', 'random']
    for module in modules:
        try:
            importlib.import_module(module)
            checks.append((f"Module {module}", True))
        except:
            checks.append((f"Module {module}", False))
    
    # Check generator import
    try:
        from event_generators.endpoint_security.crowdstrike_falcon import crowdstrike_log
        checks.append(("Generator import", True))
    except:
        checks.append(("Generator import", False))
    
    # Print results
    print("Setup Verification:")
    print("-" * 40)
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
    
    return all(passed for _, passed in checks)

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
EOF

# Run verification
python verify_setup.py
```

## 🎉 Setup Complete!

Your development environment is now fully configured with:
- ✅ Python virtual environment
- ✅ All dependencies installed
- ✅ VS Code optimized for Python development
- ✅ Testing framework ready
- ✅ Code quality tools configured
- ✅ Git hooks for code consistency

**Next Steps:**
1. [Create your first generator](../generators/generator-tutorial.md)
2. [Run comprehensive tests](testing-guide.md)
3. [Start contributing](contributing.md)

Need help? Check the [Troubleshooting Guide](../user-guide/troubleshooting.md) or open an issue!