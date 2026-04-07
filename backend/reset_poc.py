import os
import shutil
from pathlib import Path

def reset_poc():
    """
    Safely resets the Cloud Seal PoC to a fresh state.
    Wipes all stored files, blockchain logs, metadata, and keys.
    """
    print(" Starting Cloud Seal PoC System Reset...")
    
    # Define paths to data directories and files
    backend_dir = Path(__file__).parent
    data_dir = backend_dir / "data"
    
    files_to_remove = [
        data_dir / "blockchain.json",
        data_dir / "metadata.json",
        data_dir / "bloom_filter.pkl",
        data_dir / "ai_model.pkl",
        data_dir / "refcounts.json",
        data_dir / "audit_log.json",
        data_dir / "ipfs" / "pins.json"
    ]
    
    dirs_to_wipe = [
        data_dir / "ipfs",
        data_dir / "pqc_keys"
    ]
    
    # 1. Remove individual state files
    for file_path in files_to_remove:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   Removed state file: {file_path.name}")
            except Exception as e:
                print(f"   Error removing {file_path.name}: {e}")

    # 2. Wipe storage directories
    for dir_path in dirs_to_wipe:
        if dir_path.exists():
            try:
                # Remove all contents but keep the directory (or recreate it)
                shutil.rmtree(dir_path)
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   Wiped and recreated directory: {dir_path.name}/")
            except Exception as e:
                print(f"   Error wiping {dir_path.name}/: {e}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created missing directory: {dir_path.name}/")

    print("\n System Reset Complete!")
    print(" IMPORTANT: Please RESTART your Uvicorn server to clear in-memory cache.")
    print("   Command: Control+C then run 'uvicorn app:app --port 8000'")

if __name__ == "__main__":
    reset_poc()
