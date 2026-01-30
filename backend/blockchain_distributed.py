"""
Distributed Blockchain with Consensus Mechanism
Implements Proof-of-Authority (PoA) consensus for access control logging
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import socket
import threading
import pickle


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(
        self,
        index: int,
        timestamp: str,
        transactions: List[Dict[str, Any]],
        previous_hash: str,
        validator: str = "node_0"
    ):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.validator = validator  # PoA: which node validated this block
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash including validator signature"""
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "validator": self.validator,
            },
            sort_keys=True,
        ).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "hash": self.hash,
        }


class DistributedBlockchain:
    """
    Distributed blockchain with Proof-of-Authority consensus
    Features:
    - Multi-node support
    - Consensus voting
    - Automatic conflict resolution
    - Access control transaction validation
    """
    
    def __init__(
        self, 
        node_id: str, 
        storage_file: Path = None,
        authorized_validators: List[str] = None
    ):
        self.node_id = node_id
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.storage_file = storage_file
        self.peers: List[str] = []  # List of peer node addresses
        
        # Proof-of-Authority: Only authorized nodes can validate
        self.authorized_validators = authorized_validators or [node_id]
        self.is_validator = node_id in self.authorized_validators
        
        # Network state
        self.sync_in_progress = False
        
        if self.storage_file and self.storage_file.exists():
            self.load_from_file()
        else:
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            transactions=[{"type": "GENESIS", "message": "Blockchain initialized"}],
            previous_hash="0",
            validator=self.node_id
        )
        self.chain.append(genesis)
        self.save_to_file()
        print(f"[{self.node_id}] Genesis block created: {genesis.hash[:16]}...")
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Add transaction with validation
        Returns True if transaction is valid and added
        """
        # Validate transaction structure
        required_fields = ["action", "tenant_id"]
        if not all(field in transaction for field in required_fields):
            print(f"[{self.node_id}] Invalid transaction: missing required fields")
            return False
        
        # Add timestamp if not present
        if "timestamp" not in transaction:
            transaction["timestamp"] = datetime.utcnow().isoformat()
        
        # Add transaction ID for tracking
        transaction["tx_id"] = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        self.pending_transactions.append(transaction)
        print(f"[{self.node_id}] Transaction added: {transaction['tx_id']}")
        return True
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """
        Mine pending transactions (PoA: only validators can mine)
        Returns new block if successful, None otherwise
        """
        if not self.is_validator:
            print(f"[{self.node_id}] Not authorized to validate blocks")
            return None
        
        if not self.pending_transactions:
            print(f"[{self.node_id}] No pending transactions to mine")
            return None
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash,
            validator=self.node_id
        )
        
        # Validate block before adding
        if self.validate_block(new_block):
            self.chain.append(new_block)
            self.pending_transactions = []
            self.save_to_file()
            
            print(f"[{self.node_id}] Block mined: {new_block.hash[:16]}... "
                  f"({len(new_block.transactions)} transactions)")
            
            # Broadcast to peers
            self.broadcast_block(new_block)
            return new_block
        
        print(f"[{self.node_id}] Block validation failed")
        return None
    
    def validate_block(self, block: Block) -> bool:
        """Validate block integrity"""
        # Check block index
        if block.index != len(self.chain):
            return False
        
        # Check previous hash
        if block.previous_hash != self.get_latest_block().hash:
            return False
        
        # Check validator authorization
        if block.validator not in self.authorized_validators:
            return False
        
        # Verify hash
        if block.hash != block.calculate_hash():
            return False
        
        return True
    
    def validate_chain(self) -> bool:
        """Validate entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify chain link
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def resolve_conflicts(self, peer_chain: List[Block]) -> bool:
        """
        Consensus mechanism: Longest valid chain wins
        Returns True if chain was replaced
        """
        if len(peer_chain) <= len(self.chain):
            return False
        
        # Validate peer chain
        temp_chain = self.chain
        self.chain = peer_chain
        
        if self.validate_chain():
            print(f"[{self.node_id}] Chain replaced with longer valid chain "
                  f"({len(peer_chain)} blocks)")
            self.save_to_file()
            return True
        else:
            # Restore original chain
            self.chain = temp_chain
            print(f"[{self.node_id}] Peer chain validation failed")
            return False
    
    def broadcast_block(self, block: Block):
        """Broadcast new block to all peers (simplified for PoC)"""
        # In production: use actual network sockets
        print(f"[{self.node_id}] Broadcasting block {block.hash[:16]}... to peers")
        # TODO: Implement actual peer-to-peer communication
    
    def get_all_transactions(self) -> List[Dict]:
        """Get all transactions from blockchain"""
        all_tx = []
        for block in self.chain:
            for tx in block.transactions:
                all_tx.append({
                    "block": block.index,
                    "block_timestamp": block.timestamp,
                    "block_hash": block.hash,
                    "validator": block.validator,
                    **tx,
                })
        return all_tx
    
    def query_transactions(
        self, 
        tenant_id: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[Dict]:
        """Query transactions with filters"""
        all_tx = self.get_all_transactions()
        
        if tenant_id:
            all_tx = [tx for tx in all_tx if tx.get("tenant_id") == tenant_id]
        
        if action:
            all_tx = [tx for tx in all_tx if tx.get("action") == action]
        
        return all_tx
    
    def save_to_file(self):
        """Save blockchain to persistent storage"""
        if not self.storage_file:
            return
        
        data = {
            "node_id": self.node_id,
            "chain": [b.to_dict() for b in self.chain],
            "authorized_validators": self.authorized_validators
        }
        
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self):
        """Load blockchain from persistent storage"""
        with open(self.storage_file, "r") as f:
            data = json.load(f)
        
        # Handle both old format (list) and new format (dict with "chain" key)
        if isinstance(data, list):
            # Old format: flat list of blocks
            chain_data = data
        else:
            # New format: dict with "chain" key
            chain_data = data.get("chain", [])
        
        self.chain = []
        for b in chain_data:
            block = Block(
                b["index"],
                b["timestamp"],
                b["transactions"],
                b["previous_hash"],
                b.get("validator", "unknown")
            )
            # Use stored hash for backward compatibility with old blockchain files
            # Old blocks may have different hash calculation (no validator field)
            block.hash = b["hash"]
            self.chain.append(block)
        
        # Handle authorized_validators based on format
        if isinstance(data, dict):
            self.authorized_validators = data.get("authorized_validators", [self.node_id])
        else:
            # Old format doesn't have authorized_validators
            self.authorized_validators = [self.node_id]
        print(f"[{self.node_id}] Blockchain loaded: {len(self.chain)} blocks")
    
    def get_stats(self) -> Dict:
        """Get blockchain statistics"""
        return {
            "node_id": self.node_id,
            "is_validator": self.is_validator,
            "chain_length": len(self.chain),
            "pending_transactions": len(self.pending_transactions),
            "total_transactions": sum(len(b.transactions) for b in self.chain),
            "authorized_validators": self.authorized_validators,
            "chain_valid": self.validate_chain()
        }


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Simulate 3-node network
    validators = ["node_0", "node_1", "node_2"]
    
    # Node 0 (Primary validator)
    node0 = DistributedBlockchain(
        node_id="node_0",
        storage_file=Path("data/blockchain_node0.json"),
        authorized_validators=validators
    )
    
    # Add some transactions
    node0.add_transaction({
        "action": "UPLOAD_NEW",
        "tenant_id": "tenant_A",
        "file_cid": "Qm123abc",
        "file_name": "document.pdf"
    })
    
    node0.add_transaction({
        "action": "ACCESS_GRANT",
        "tenant_id": "tenant_A",
        "target_user": "user_B",
        "file_cid": "Qm123abc"
    })
    
    # Mine block
    block = node0.mine_pending_transactions()
    
    # Query transactions
    print("\nAll transactions:")
    for tx in node0.get_all_transactions():
        action = tx.get("action", tx.get("type", "SYSTEM"))
        tenant = tx.get("tenant_id", "SYSTEM")
        timestamp = tx.get("timestamp", tx.get("block_timestamp"))

        print(f"  - {action} by {tenant} at {timestamp}")

    
    # Show stats
    print("\nBlockchain stats:")
    for key, value in node0.get_stats().items():
        print(f"  {key}: {value}")