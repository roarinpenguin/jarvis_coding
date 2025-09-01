# Jarvis Coding Project Structure

## Directory Organization

```
jarvis_coding/
├── api/                          # REST API Implementation
│   ├── app/                      # FastAPI Application
│   │   ├── core/                 # Core functionality (auth, config)
│   │   ├── models/               # Request/Response models
│   │   ├── routers/              # API endpoints
│   │   ├── services/             # Business logic
│   │   └── utils/                # Utility functions
│   ├── docs/                     # API Documentation
│   │   ├── acceptance/           # Acceptance reports
│   │   ├── guides/               # API guides and references
│   │   └── reports/              # Implementation reports
│   ├── tests/                    # API Tests
│   │   ├── complex_tests/        # Complex integration tests
│   │   ├── reports/              # Test reports
│   │   └── validation_tests/     # Validation test suites
│   ├── Dockerfile                # Container configuration
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # API documentation
│
├── docs/                         # Project Documentation
│   ├── api/                      # API documentation
│   ├── architecture/             # Architecture docs
│   ├── development/              # Developer guides
│   ├── generators/               # Generator documentation
│   └── parsers/                  # Parser documentation
│
├── event_generators/             # Event Generator Modules
│   ├── cloud_infrastructure/     # AWS, GCP, Azure generators
│   ├── endpoint_security/        # EDR, endpoint generators
│   ├── identity_access/          # IAM, authentication generators
│   ├── email_security/           # Email security generators
│   ├── infrastructure/           # IT infrastructure generators
│   ├── network_security/         # Firewall, network generators
│   ├── web_security/             # WAF, web security generators
│   └── shared/                   # Shared generator utilities
│
├── parsers/                      # Log Parser Configurations
│   ├── community/                # Community parsers
│   └── sentinelone/              # SentinelOne parsers
│
├── scenarios/                    # Attack Scenarios
│   ├── configs/                  # Scenario configurations
│   └── api/                      # Scenario API implementations
│
├── testing/                      # Testing Infrastructure
│   ├── bulk_testing/             # Bulk test utilities
│   ├── results/                  # Test results
│   ├── scripts/                  # Test scripts
│   ├── utilities/                # Testing utilities
│   └── validation/               # Validation tools
│
├── utilities/                    # Utility Scripts
│
├── .gitignore                    # Git ignore configuration
├── docker-compose.yml            # Docker compose configuration
├── README.md                     # Project documentation
├── RELEASE_NOTES.md              # Release notes
├── PROJECT_STRUCTURE.md          # This file
└── detections.conf               # Detection configurations
```

## Key Directories

### `/api`
Complete REST API implementation with FastAPI, including authentication, routers, services, and comprehensive testing.

### `/event_generators`
106+ Python event generators organized by category (cloud, network, endpoint, etc.) with Star Trek themed test data.

### `/parsers`
100+ log parser configurations for security products, supporting JSON, syslog, CSV, and key-value formats.

### `/scenarios`
Attack scenario generators for enterprise security simulations including APT campaigns and incident response.

### `/testing`
Comprehensive testing infrastructure including validation tools, bulk testing utilities, and test results.

### `/docs`
Complete project documentation including API references, architecture guides, and developer tutorials.

## File Organization Guidelines

1. **Code Files**: Organized by functional area in appropriate subdirectories
2. **Documentation**: Markdown files in `/docs` with category-specific subdirectories
3. **Tests**: Test files in `/tests` subdirectories, reports in `/reports`
4. **Configuration**: Root level for project-wide configs
5. **Scripts**: Utility scripts in `/utilities` or category-specific folders

## Excluded from Git

- `.claude/` - Claude AI configuration (local only)
- `agent_force/` - Agent Force system (local only)
- `CLAUDE.md` - AI instructions (local only)
- `.venv/` - Python virtual environment
- `*.pyc`, `__pycache__/` - Python compiled files
- `.env` - Environment variables

## Recent Organization (August 31, 2025)

- Moved API documentation to `/api/docs/` with subcategories
- Organized test files into `/api/tests/` subdirectories
- Moved root-level scripts to appropriate directories
- Created clear separation between code, tests, and documentation
- Established consistent naming conventions across the project