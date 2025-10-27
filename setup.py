"""Setup file for py-operrouter package."""

from setuptools import setup, find_packages

setup(
    name="py-operrouter",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "grpcio>=1.50.0",
        "protobuf>=4.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "http": ["httpx>=0.24.0"],
        "grpc": ["grpcio>=1.50.0", "protobuf>=4.21.0"],
    },
    author="OperRouter Team",
    author_email="team@operrouter.dev",
    description="Python SDK for OperRouter with HTTP, gRPC, and FFI support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/operrouter/operrouter-core",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
