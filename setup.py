import os

from setuptools import setup

setup(
    name="fixer-cli",
    version="0.1.0",
    py_modules=["fixer"],
    install_requires=[
        "typer[all]>=0.9.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "gitpython>=3.1.0",
    ],
    entry_points={"console_scripts": ["fixer = fixer:app"]},
    author="Fixer CLI Team",
    author_email="fixer@example.com",
    description="A comprehensive CLI tool for fixing issues and maintaining code quality",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/example/fixer-cli",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    keywords="cli, development, code-quality, git, automation",
)
