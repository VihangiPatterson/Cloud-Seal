"""
Configuration settings for Cloud Seal PoC
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# IPFS Configuration
IPFS_HOST = os.getenv('IPFS_HOST', '127.0.0.1')
IPFS_PORT = int(os.getenv('IPFS_PORT', '5001'))

# Bloom Filter Configuration
BLOOM_FILTER_SIZE = 10000  # Expected number of files
BLOOM_FILTER_FP_RATE = 0.01  # 1% false positive rate

# Storage Configuration
DATA_DIR = BASE_DIR / 'data'

# Cloud-Safe Writable Directory Fallback
# Many cloud platforms (like Choreo) have a read-only root filesystem.
try:
    DATA_DIR.mkdir(exist_ok=True)
    # Test if we can actually write to this directory
    test_file = DATA_DIR / '.write_test'
    test_file.touch()
    test_file.unlink()
except (OSError, PermissionError):
    # Use /tmp as it is always writable in Choreo/Serverless environments
    DATA_DIR = Path('/tmp/cloud-seal-data')
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    print(f"[Config] ☁️ Read-only detected. Switching storage to: {DATA_DIR}")

# Blockchain Configuration
BLOCKCHAIN_FILE = DATA_DIR / 'blockchain.json'

# Reference Counter Configuration
REFCOUNT_FILE = DATA_DIR / 'refcounts.json'

# Tenants (for demo purposes)
DEMO_TENANTS = ['tenant_A', 'tenant_B', 'tenant_C']