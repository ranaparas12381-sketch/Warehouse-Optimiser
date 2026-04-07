CONTRIBUTING TO WAREHOUSE OPTIMIZATION SYSTEM

Thank you for your interest in contributing to the Warehouse Optimization System. This document provides guidelines for contributing to the project.

GETTING STARTED

Prerequisites

* Python 3.11 or higher
* Git for version control
* Basic understanding of reinforcement learning concepts
* Familiarity with Streamlit framework

Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment
4. Install dependencies

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
cd warehouse_openenv
pip install -r requirements.txt

CODE STANDARDS

Python Style Guide

* Follow PEP 8 style guidelines
* Use type hints for function parameters and return values
* Include docstrings for all public functions and classes
* Maximum line length of 120 characters

Code Organization

* Place environment logic in the env/ directory
* Add new tasks in the tasks/ directory
* Implement graders in the graders/ directory
* Dashboard components belong in dashboard/

TESTING

Before submitting changes:

1. Test the dashboard locally
2. Run baseline simulations for all difficulty levels
3. Verify Docker build completes successfully
4. Ensure no regression in existing functionality

PULL REQUEST PROCESS

1. Create a feature branch from main
2. Make your changes with clear commit messages
3. Update documentation as needed
4. Test your changes thoroughly
5. Submit a pull request with a clear description

Commit Message Format

Use descriptive commit messages:

* feat: Add new feature
* fix: Bug fix
* docs: Documentation changes
* refactor: Code refactoring
* test: Test additions or modifications

TYPES OF CONTRIBUTIONS

We welcome various types of contributions:

Code Contributions

* New task implementations
* Enhanced grading algorithms
* Improved baseline policies
* Performance optimizations
* Bug fixes

Documentation

* README improvements
* Code documentation
* Usage examples
* Tutorial content

Testing

* Unit tests
* Integration tests
* Performance benchmarks

REPORTING ISSUES

When reporting issues, please include:

* Clear description of the problem
* Steps to reproduce
* Expected vs actual behavior
* Environment details (OS, Python version)
* Error messages or logs

QUESTIONS AND DISCUSSIONS

For questions or discussions:

* Use GitHub Discussions for general questions
* Use GitHub Issues for bug reports and feature requests

CODE REVIEW PROCESS

All submissions require review before merging:

* Code quality and style compliance
* Functionality correctness
* Documentation completeness
* Test coverage

RECOGNITION

Contributors will be acknowledged in the project documentation.

Thank you for helping improve the Warehouse Optimization System.
