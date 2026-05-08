"""
Setup configuration for Todo Manager CLI.

This module configures the installation and entry points for the todo_manager package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="todo-manager",
    version="1.0.0",
    author="Todo Manager Team",
    description="A modular Python CLI todo manager with SQLite persistence, priority/category support, and CSV export",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/todo-manager",
    py_modules=[
        "models",
        "database",
        "export",
        "cli",
        "main",
    ],
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "todo=main:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    keywords="cli todo task manager sqlite productivity",
)
