# Contributing to Network Intrusion Detection System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Error messages or logs

### Suggesting Enhancements

For feature requests:
- Describe the feature and its benefits
- Provide use cases
- Suggest implementation approach if possible

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   python test_api.py
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add: feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Describe what you changed and why
   - Reference any related issues

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/network-intrusion-detection.git
cd network-intrusion-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_api.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

## Areas for Contribution

### High Priority
- [ ] Add more attack types
- [ ] Improve minority class detection
- [ ] Add real-time packet capture
- [ ] Create Docker Compose setup
- [ ] Add authentication to API

### Medium Priority
- [ ] Add more visualization options
- [ ] Implement model versioning
- [ ] Add batch processing optimization
- [ ] Create CLI tool
- [ ] Add more test cases

### Documentation
- [ ] Add more API examples
- [ ] Create video tutorials
- [ ] Improve deployment guides
- [ ] Add architecture diagrams

## Questions?

Feel free to open an issue for any questions about contributing!
