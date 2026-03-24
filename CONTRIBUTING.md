# Contributing to awesome-vpn

Thank you for your interest in contributing to awesome-vpn! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Describe the behavior you observed and what behavior you expected**
- **Include code samples or screenshots if applicable**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a new branch from `master` for your changes
3. Make your changes
4. Ensure your code follows the existing style
5. Add or update tests as necessary
6. Update documentation as needed
7. Submit a pull request

#### Pull Request Guidelines

- Fill in the required template
- Follow the Python style guide (PEP 8)
- Include appropriate test cases
- Update README.md if your changes affect usage
- End all files with a newline

## Development Setup

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/awesome-vpn/awesome-vpn.git
cd awesome-vpn

# Install dependencies
pip install -r requirements.txt

# Run the crawler
python main.py --validate --workers 24 --validate-workers 50
```

## Style Guidelines

### Python Code

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use docstrings for all public methods

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
feat(parser): add hysteria2 protocol support

Add support for parsing hysteria2:// URLs and converting
to sing-box format. Includes validation for required fields.

Fixes #123
```

## License

By contributing to awesome-vpn, you agree that your contributions will be licensed under the GNU General Public License v3.0.
