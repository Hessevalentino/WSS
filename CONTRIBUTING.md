# Contributing to WiFi Scanner Suite

Thank you for your interest in contributing to WiFi Scanner Suite (WSS). This document provides guidelines and information for contributors.

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment for all contributors. By participating, you agree to uphold these standards.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **System information** (Linux distribution, Python version)
- **Log files** or error messages
- **Network configuration** details if relevant

### Suggesting Enhancements

Enhancement suggestions are welcome. Please provide:

- **Clear description** of the proposed feature
- **Use case** or problem it solves
- **Implementation ideas** if you have them
- **Compatibility considerations** with existing functionality

### Pull Requests

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes following the coding standards
4. **Test** your changes thoroughly
5. **Update** documentation if necessary
6. **Submit** a pull request with clear description

## Development Setup

### Prerequisites

- Linux development environment
- Python 3.7 or higher
- NetworkManager and wireless tools
- Git for version control

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/wifi-scanner-suite.git
cd wifi-scanner-suite

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install rich  # Optional but recommended

# Run tests
python3 -m py_compile wifi_scanner_suite.py
python3 wifi_scanner_suite.py --help
```

## Coding Standards

### Python Style Guide

- Follow **PEP 8** guidelines
- Use **4 spaces** for indentation
- Maximum **line length of 88 characters**
- Use **meaningful variable names**
- Include **type hints** where applicable

### Documentation Standards

- **Docstrings** for all functions and classes
- **Inline comments** for complex logic
- **Clear commit messages** following conventional format
- **Update README.md** for new features

### Code Structure

```python
def function_name(param: type) -> return_type:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when raised
    """
    # Implementation
    pass
```

## Testing Guidelines

### Manual Testing

Before submitting changes, test:

- **Basic functionality** with `--scan`, `--auto`, `--continuous`
- **Interactive menu** navigation
- **Export functionality** (JSON and CSV)
- **Error handling** with invalid inputs
- **Different network conditions**

### Test Cases

Include tests for:

- **Network discovery** accuracy
- **Connection attempt** handling
- **Data export** format validation
- **Configuration** loading and validation
- **Error conditions** and recovery

## Architecture Overview

### Core Components

- **WiFiNetwork**: Data class for network information
- **ConnectionAttempt**: Data class for connection results
- **WiFiConfig**: Configuration management
- **WiFiScanner**: Core scanning and connection logic
- **WiFiScannerApp**: User interface and menu system

### Key Design Principles

- **Separation of concerns** between data, logic, and presentation
- **Error handling** with graceful degradation
- **Configuration-driven** behavior
- **Cross-platform** compatibility within Linux ecosystem
- **Minimal dependencies** for broad compatibility

## Feature Development

### Adding New Features

1. **Design** the feature interface
2. **Implement** core functionality
3. **Add** configuration options if needed
4. **Update** menu system if applicable
5. **Test** thoroughly across different scenarios
6. **Document** usage and configuration

### Backward Compatibility

- Maintain **existing API** compatibility
- Provide **migration path** for configuration changes
- **Deprecate** features gracefully with warnings
- **Version** configuration file format appropriately

## Documentation

### Required Documentation Updates

- **README.md** for user-facing changes
- **EXAMPLES.md** for new usage patterns
- **Inline documentation** for code changes
- **Configuration** documentation for new options

### Documentation Style

- **Clear and concise** language
- **Practical examples** with expected output
- **Step-by-step** instructions
- **Troubleshooting** information for common issues

## Release Process

### Version Numbering

- Follow **semantic versioning** (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] Changelog updated
- [ ] Backward compatibility verified
- [ ] Performance impact assessed

## Community Guidelines

### Communication

- **Be respectful** and constructive
- **Ask questions** if requirements are unclear
- **Provide context** for changes and decisions
- **Help others** learn and contribute

### Review Process

- **Code reviews** focus on functionality and maintainability
- **Constructive feedback** with specific suggestions
- **Timely responses** to review comments
- **Collaborative** problem-solving approach

## Getting Help

### Resources

- **GitHub Issues** for bug reports and feature requests
- **Documentation** in README.md and EXAMPLES.md
- **Code comments** for implementation details
- **Commit history** for context on changes

### Contact

For questions about contributing:

1. **Check existing issues** and documentation first
2. **Create an issue** for discussion of major changes
3. **Ask questions** in pull request comments
4. **Be patient** - maintainers volunteer their time

## Recognition

Contributors are recognized through:

- **Git commit history** preserving authorship
- **Release notes** acknowledging contributions
- **GitHub contributors** page
- **Special thanks** for significant contributions

Thank you for contributing to WiFi Scanner Suite and helping make network analysis more accessible to the Linux community.
