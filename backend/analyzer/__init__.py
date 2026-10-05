"""
CodeLens analyzer package.

This package contains the modules responsible for analyzing
source code repositories.

Modules:
    analyzer    - Main analysis orchestrator
    metrics     - Basic repository and code metrics
    smells      - Code smell detection
    complexity  - Complexity analysis
"""

from .analyzer import analyze_repository

__all__ = ["analyze_repository"]