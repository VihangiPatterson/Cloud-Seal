"""
Reference Counter for Multi-Tenant File Ownership
"""
import json
from typing import Tuple, List, Dict
from pathlib import Path


class ReferenceCounter:
    """
    Tracks how many tenants own each file
    Prevents premature deletion in multi-tenant deduplication
    """
    
    def __init__(self, storage_file: Path = None):
        self.ref_counts: Dict[str, int] = {}  # {cid: count}
        self.owners: Dict[str, List[str]] = {}  # {cid: [tenant_ids]}
        self.storage_file = storage_file
        self.filenames: Dict[str, Dict[str, str]] = {}
# cid -> { tenant_id: filename }

        # Load existing data
        if storage_file and storage_file.exists():
            self.load_from_file()
    
    def add_reference(self, cid: str, tenant_id: str, filename: str) -> str:

        """
        Adds tenant as file owner
        
        Args:
            cid: Content Identifier (file hash)
            tenant_id: Tenant identifier
        
        Returns:
            'NEW' if first upload, 'DUPLICATE' if file exists
        """
        if cid not in self.ref_counts:
                self.ref_counts[cid] = 1
                self.owners[cid] = [tenant_id]
                self.filenames[cid] = {tenant_id: filename}
                self._save()
                return "NEW"
        else:
            if tenant_id not in self.owners[cid]:
                self.ref_counts[cid] += 1
                self.owners[cid].append(tenant_id)
                self.filenames[cid][tenant_id] = filename
                self._save()
                return "DUPLICATE"

    
    def remove_reference(self, cid: str, tenant_id: str) -> Tuple[int, bool]:
        """
        Removes tenant as file owner
        
        Args:
            cid: Content Identifier
            tenant_id: Tenant identifier
        
        Returns:
            (remaining_count, should_delete)
        
        Raises:
            ValueError: If CID not found
            PermissionError: If tenant is not owner
        """
        if cid not in self.owners:
            raise ValueError(f"CID {cid} not found in reference counter")
        
        if tenant_id not in self.owners[cid]:
            raise PermissionError(f"Tenant {tenant_id} is not owner of {cid}")
        
        # Remove tenant
        self.owners[cid].remove(tenant_id)
        self.ref_counts[cid] -= 1
        
        # Check if file should be deleted
        if self.ref_counts[cid] == 0:
            del self.owners[cid]
            del self.ref_counts[cid]
            self._save()
            return 0, True  # Delete file
        else:
            self._save()
            return self.ref_counts[cid], False  # Keep file
    
    def get_count(self, cid: str) -> int:
        """
        Gets reference count for file
        """
        return self.ref_counts.get(cid, 0)
    
    def get_owners(self, cid: str) -> List[str]:
        """
        Gets list of tenants who own file
        """
        return self.owners.get(cid, [])
    
    def is_owner(self, cid: str, tenant_id: str) -> bool:
        """
        Checks if tenant owns file
        """
        return tenant_id in self.owners.get(cid, [])
    
    def get_all_files(self):
     return [
        {
            "cid": cid,
            "ref_count": self.ref_counts[cid],
            "owners": self.owners[cid],
            "filenames": self.filenames.get(cid, {})
        }
        for cid in self.ref_counts
    ]

    
    def _save(self):
        """
        Saves reference counts to file
        """
        if not self.storage_file:
            return
        
        data = {
    "ref_counts": self.ref_counts,
    "owners": self.owners,
    "filenames": self.filenames
}

        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self):
        """
        Loads reference counts from file
        """
        if not self.storage_file or not self.storage_file.exists():
            return
        
        with open(self.storage_file, 'r') as f:
            data = json.load(f)
        
        self.ref_counts = data.get('ref_counts', {})
        self.owners = data.get('owners', {})
        self.filenames = data.get("filenames", {})

        
        print(f"Reference counter loaded: {len(self.ref_counts)} files tracked")


# Test function
if __name__ == "__main__":
    # Create reference counter
    rc = ReferenceCounter()
    
    # Tenant A uploads file
    print("Tenant A uploads file...")
    status = rc.add_reference('Qm123abc', 'tenant_A')
    print(f"Status: {status}, RefCount: {rc.get_count('Qm123abc')}")
    
    # Tenant B uploads SAME file (duplicate)
    print("\nTenant B uploads same file...")
    status = rc.add_reference('Qm123abc', 'tenant_B')
    print(f"Status: {status}, RefCount: {rc.get_count('Qm123abc')}")
    
    # Tenant C also uploads
    print("\nTenant C uploads same file...")
    status = rc.add_reference('Qm123abc', 'tenant_C')
    print(f"Status: {status}, RefCount: {rc.get_count('Qm123abc')}")
    
    # Check owners
    print(f"\nOwners: {rc.get_owners('Qm123abc')}")
    
    # Tenant A deletes
    print("\nTenant A deletes file...")
    count, should_delete = rc.remove_reference('Qm123abc', 'tenant_A')
    print(f"RefCount: {count}, Should Delete: {should_delete}")
    
    # Tenant B deletes
    print("\nTenant B deletes file...")
    count, should_delete = rc.remove_reference('Qm123abc', 'tenant_B')
    print(f"RefCount: {count}, Should Delete: {should_delete}")
    
    # Tenant C deletes (last one)
    print("\nTenant C deletes file...")
    count, should_delete = rc.remove_reference('Qm123abc', 'tenant_C')
    print(f"RefCount: {count}, Should Delete: {should_delete}")