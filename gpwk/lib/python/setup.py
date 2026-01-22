"""Setup for gpwk_core package."""
from setuptools import setup, find_packages

setup(
    name="gpwk_core",
    version="0.1.0",
    description="GitHub Personal Work Kit - Core library with OpenTelemetry instrumentation",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api>=1.20.0",
        "opentelemetry-sdk>=1.20.0",
        "opentelemetry-exporter-otlp-proto-grpc>=1.20.0",
        "requests>=2.31.0",
        "PyGithub>=2.1.0",
        "structlog>=23.1.0",
    ],
    python_requires=">=3.8",
)
