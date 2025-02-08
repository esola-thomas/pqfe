# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager
- C compiler (for liboqs)
- CMake 3.5 or higher

## Dependencies

PQFE requires the following main dependencies:
- liboqs-python: Open Quantum Safe's Python bindings
- cryptography: For AES encryption
- pytest: For running tests

## Installation Steps

1. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install build-essential cmake
```

2. Clone the repository:
```bash
git clone https://github.com/your-username/pqfe.git
cd pqfe
```

3. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Verifying Installation

1. Run tests to verify everything is working:
```bash
pytest tests/
```

2. Run benchmarks to check performance:
```bash
python benchmarks/performance_benchmark.py
```

## Troubleshooting

### Common Issues

1. liboqs build fails:
   - Ensure you have the required build tools installed
   - Check CMake version (3.5+ required)
   - Verify compiler is working correctly

2. Import errors:
   - Verify virtual environment is activated
   - Check Python version compatibility
   - Reinstall dependencies if needed

### Getting Help

If you encounter any issues:
1. Check the [GitHub Issues](https://github.com/your-username/pqfe/issues)
2. Review error messages and logs
3. Create a new issue with detailed information about the problem 