"""
IPFS Manager for Distributed Storage
(Simulated for PoC - can be replaced with real IPFS later)
"""
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict
import shutil


class IPFSManager:
    """
    Simulates IPFS functionality for PoC
    (In production, replace with ipfshttpclient)
    """
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(exist_ok=True)
        
        # Track pinned files
        self.pinned_files: Dict[str, dict] = {}
        self.pins_file = storage_dir / 'pins.json'
        
        if self.pins_file.exists():
            with open(self.pins_file, 'r') as f:
                self.pinned_files = json.load(f)
    
    def add_bytes(self, content: bytes) -> str:
        """
        Adds content to IPFS and returns CID
        
        Args:
            content: File bytes
        
        Returns:
            Content Identifier (CID)
        """
        # Generate CID (simulated - real IPFS uses multihash)
        cid = "Qm" + hashlib.sha256(content).hexdigest()[:46]
        
        # Store file
        file_path = self.storage_dir / cid
        with open(file_path, 'wb') as f:
            f.write(content)
        
        print(f"Added to IPFS: {cid} ({len(content)} bytes)")
        return cid
    
    def get_bytes(self, cid: str) -> Optional[bytes]:
        """
        Retrieves content from IPFS
        
        Args:
            cid: Content Identifier
        
        Returns:
            File bytes or None if not found
        """
        file_path = self.storage_dir / cid
        if not file_path.exists():
            return None
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        print(f"Retrieved from IPFS: {cid} ({len(content)} bytes)")
        return content
    
    def pin_file(self, cid: str, metadata: dict = None):
        """
        Pins file to prevent garbage collection
        
        Args:
            cid: Content Identifier
            metadata: Additional file metadata
        """
        self.pinned_files[cid] = {
            'pinned': True,
            'metadata': metadata or {}
        }
        self._save_pins()
        print(f"Pinned: {cid}")
    
    def unpin_file(self, cid: str):
        """
        Unpins file (allows garbage collection)
        
        Args:
            cid: Content Identifier
        """
        if cid in self.pinned_files:
            del self.pinned_files[cid]
            self._save_pins()
            
            # Delete file
            file_path = self.storage_dir / cid
            if file_path.exists():
                file_path.unlink()
            
        print(f"Unpinned and removed: {cid}")

    def list_pins(self) -> Dict[str, dict]:
        """
        Lists all pinned files
        """
        return self.pinned_files

    def _save_pins(self):
        """
        Saves pin metadata
        """
        with open(self.pins_file, 'w') as f:
            json.dump(self.pinned_files, f, indent=2)


# Test function
if __name__ == "__main__":
    storage = Path("./ipfs_storage")
    ipfs = IPFSManager(storage)

    data = b"Hello IPFS PoC"
    cid = ipfs.add_bytes(data)
    ipfs.pin_file(cid, {"owner": "tenant_A"})

    retrieved = ipfs.get_bytes(cid)
    print("Retrieved matches:", retrieved == data)

    ipfs.unpin_file(cid)
