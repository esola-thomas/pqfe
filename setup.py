from setuptools import setup, find_packages

setup(
    name="pqfe",
    version="0.1.0",
    author="Ernesto Sola-Thomas",
    author_email="ernesto@solathomas.com",
    description="Post-Quantum File Encryption API with Kyber and hybrid encryption",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/esola-thomas/pqfe",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10.16",
        "Topic :: Security :: Cryptography"
    ],
    python_requires=">=3.8",
)
