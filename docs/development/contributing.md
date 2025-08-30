# Contributing to Jarvis Coding

Thank you for your interest in contributing to Jarvis Coding! This guide will help you get started with contributing code, documentation, and ideas to the project.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain the Star Trek theme 🖖

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/jarvis_coding.git
cd jarvis_coding

# Add upstream remote
git remote add upstream https://github.com/natesmalley/jarvis_coding.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r event_generators/shared/requirements.txt
pip install pytest black flake8  # Development tools
```

### 3. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

## 📝 Contribution Types

### 🔧 Event Generators

#### Adding a New Generator

1. **Choose the right category**:
   - `cloud_infrastructure/` - AWS, GCP, Azure
   - `network_security/` - Firewalls, NDR
   - `endpoint_security/` - EDR, AV
   - `identity_access/` - IAM, SSO
   - `email_security/` - Email protection
   - `web_security/` - WAF, proxies
   - `infrastructure/` - DevOps, backup

2. **Follow the template**:

```python
#!/usr/bin/env python3
"""
Vendor Product Name Event Generator
Generates realistic security events with Star Trek themed data
"""

import json
import random
from datetime import datetime, timedelta, timezone

# Star Trek themed data
STAR_TREK_USERS = [
    "jean.picard@starfleet.corp",
    "william.riker@starfleet.corp",
    "data.android@starfleet.corp",
    "worf.security@starfleet.corp",
    "jordy.laforge@starfleet.corp",
    "beverly.crusher@starfleet.corp",
    "deanna.troi@starfleet.corp"
]

STAR_TREK_HOSTS = [
    "ENTERPRISE-BRIDGE-01",
    "ENTERPRISE-ENGINEERING-01",
    "ENTERPRISE-SECURITY-01",
    "ENTERPRISE-MEDICAL-01"
]

def vendor_product_log():
    """Generate a single vendor_product event"""
    current_time = datetime.now(timezone.utc)
    event_time = current_time - timedelta(minutes=random.randint(0, 10))
    
    event = {
        "timestamp": event_time.isoformat(),
        "user": random.choice(STAR_TREK_USERS),
        "host": random.choice(STAR_TREK_HOSTS),
        "source_ip": f"10.0.0.{random.randint(1, 254)}",
        "action": random.choice(["allow", "deny", "alert"]),
        "severity": random.choice(["low", "medium", "high", "critical"])
    }
    
    return event

if __name__ == "__main__":
    # Generate sample event for testing
    print(json.dumps(vendor_product_log(), indent=2))
```

3. **Update hec_sender.py**:

```python
# Add to GENERATOR_MAPPING
"vendor_product": "vendor_product",
```

4. **Test your generator**:

```bash
# Run directly
python event_generators/category/vendor_product.py

# Test with HEC sender
python event_generators/shared/hec_sender.py --product vendor_product --count 5
```

### 📋 Parser Development

#### Adding a New Parser

1. **Create parser directory**:

```bash
mkdir -p parsers/community/vendor_product_description-latest
```

2. **Create parser configuration**:

```json
{
  "name": "Vendor Product Parser",
  "version": "1.0.0",
  "vendor": "Vendor Name",
  "product": "Product Name",
  "input_format": "json",
  "ocsf_version": "1.1.0",
  "field_mappings": {
    "timestamp": "time",
    "user": "actor.user.name",
    "source_ip": "src_endpoint.ip",
    "action": "disposition",
    "severity": "severity_id"
  },
  "value_mappings": {
    "severity": {
      "low": 1,
      "medium": 2,
      "high": 3,
      "critical": 4
    },
    "action": {
      "allow": "Allowed",
      "deny": "Blocked",
      "alert": "Alert"
    }
  }
}
```

3. **Test parser compatibility**:

```bash
python testing/validation/final_parser_validation.py --parser vendor_product
```

### 📖 Documentation

#### Documentation Standards

- Use clear, concise language
- Include code examples
- Follow markdown best practices
- Update table of contents
- Test all code samples

#### Areas Needing Documentation

- Generator implementation details
- Parser configuration guides
- API usage examples
- Deployment procedures
- Troubleshooting guides

### 🧪 Testing

#### Writing Tests

1. **Generator tests** (`tests/test_generators.py`):

```python
def test_vendor_product_generator():
    """Test vendor_product generator"""
    from event_generators.category.vendor_product import vendor_product_log
    
    event = vendor_product_log()
    
    # Check required fields
    assert "timestamp" in event
    assert "user" in event
    assert "@starfleet.corp" in event["user"]
    
    # Check Star Trek theme
    assert any(user in event["user"] for user in ["picard", "riker", "data"])
```

2. **Run tests**:

```bash
pytest tests/test_generators.py::test_vendor_product_generator -v
```

## 🎨 Code Style

### Python Style Guide

- Follow PEP 8
- Use Black for formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Format Your Code

```bash
# Format with black
black event_generators/

# Check with flake8
flake8 event_generators/ --max-line-length=88

# Sort imports
isort event_generators/
```

### Star Trek Theme Requirements

All test data MUST use Star Trek themed values:

- **Users**: firstname.lastname@starfleet.corp
- **Hosts**: ENTERPRISE-{DEPARTMENT}-{NUMBER}
- **Domains**: starfleet.corp, enterprise.starfleet.corp
- **IPs**: 10.0.0.x range for internal

## 🔄 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Star Trek theme maintained
- [ ] Commit messages are clear

### 2. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New generator
- [ ] New parser
- [ ] Bug fix
- [ ] Documentation
- [ ] Performance improvement

## Testing
- [ ] Generator produces valid events
- [ ] Parser extracts expected fields
- [ ] Tests written and passing
- [ ] Manual testing completed

## Checklist
- [ ] Star Trek theme included
- [ ] Recent timestamps (last 10 minutes)
- [ ] Follows existing patterns
- [ ] Documentation updated
```

### 3. Review Process

1. Submit PR against `main` branch
2. Automated tests will run
3. Maintainer review (1-3 days)
4. Address feedback
5. Merge when approved

## 🐛 Reporting Issues

### Bug Reports

Include:
- Generator/parser name
- Expected behavior
- Actual behavior
- Sample event/error
- Environment details

### Feature Requests

Include:
- Use case description
- Proposed implementation
- Example output
- Related generators/parsers

## 💡 Best Practices

### Generator Development

1. **Keep it simple**: <200 lines of code
2. **Use standard library**: Minimize dependencies
3. **Recent timestamps**: Last 10 minutes
4. **Realistic data**: Valid IPs, domains, etc.
5. **Star Trek theme**: Always include

### Parser Development

1. **OCSF compliance**: Map to standard fields
2. **Handle variations**: Support different formats
3. **Extract maximum fields**: Don't lose data
4. **Performance**: Optimize for speed
5. **Error handling**: Graceful failures

## 🏆 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](../../CONTRIBUTORS.md)
- Release notes
- Documentation credits

## 📚 Resources

### Helpful Links

- [Generator Tutorial](../generators/generator-tutorial.md)
- [Parser Tutorial](../parsers/parser-tutorial.md)
- [OCSF Specification](https://schema.ocsf.io/)
- [Star Trek Memory Alpha](https://memory-alpha.fandom.com/)

### Getting Help

- Open an [issue](https://github.com/natesmalley/jarvis_coding/issues)
- Check [discussions](https://github.com/natesmalley/jarvis_coding/discussions)
- Review existing [PRs](https://github.com/natesmalley/jarvis_coding/pulls)

## 🎯 Priority Areas

Current areas needing contributions:

1. **Generators needed**:
   - Splunk Enterprise Security
   - IBM QRadar
   - Elastic Security
   - Datadog Security

2. **Parser improvements**:
   - Enhanced OCSF compliance
   - Better field extraction
   - Performance optimization

3. **Documentation**:
   - Video tutorials
   - Architecture diagrams
   - Deployment guides

4. **Testing**:
   - Integration tests
   - Performance benchmarks
   - Validation tools

## 🚀 Quick Contribution

Want to contribute quickly? Here's how:

```bash
# 1. Fix a typo in documentation
git checkout -b fix/typo-in-docs
# Make your fix
git add .
git commit -m "Fix typo in generator tutorial"
git push origin fix/typo-in-docs
# Open PR

# 2. Add Star Trek character
# Edit STAR_TREK_USERS in any generator
git checkout -b feature/add-star-trek-character
# Add character
git add .
git commit -m "Add Guinan to Star Trek users"
git push origin feature/add-star-trek-character
# Open PR

# 3. Improve error handling
git checkout -b fix/error-handling
# Add try/except blocks
git add .
git commit -m "Improve error handling in aws_cloudtrail generator"
git push origin fix/error-handling
# Open PR
```

## Thank You! 🖖

Every contribution, no matter how small, helps make Jarvis Coding better. We appreciate your time and effort!

Live long and prosper!