import os
import shutil
from pathlib import Path

def reset_storage():
    """Wipes all local storage for a fresh start"""
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / 'data'
    
    print(f"🧹 Resetting storage in: {data_dir}")
    
    if data_dir.exists():
        try:
            # Remove the whole data directory
            shutil.rmtree(data_dir)
            print(" Data directory removed.")
        except Exception as e:
            print(f" Error removing data directory: {e}")
            return False
    
    # Re-create the necessary structure
    try:
        data_dir.mkdir(exist_ok=True)
        (data_dir / 'ipfs').mkdir(exist_ok=True)
        (data_dir / 'pqc_keys').mkdir(exist_ok=True)
        print(" Directory structure re-created.")
        print(" Storage is now clean and ready for fresh testing!")
        return True
    except Exception as e:
        print(f" Error re-creating directories: {e}")
        return False

if __name__ == "__main__":
    reset_storage()
