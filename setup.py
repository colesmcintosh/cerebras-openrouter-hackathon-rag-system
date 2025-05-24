"""
Setup configuration for the Cerebras RAG system.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cerebras-rag",
    version="1.0.0",
    author="Cole McIntosh",
    author_email="",
    description="Advanced RAG system for Cerebras documentation with citations and memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/cerebras-openrouter-hackathon",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.23",
            "black>=23.0",
            "isort>=5.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "rich": [
            "rich>=13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cerebras-rag-cli=cerebras_rag.interfaces.cli:main",
            "cerebras-rag-populate=cerebras_rag.utils.populate_vectordb:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 