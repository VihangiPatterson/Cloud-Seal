from pathlib import Path
import json
import hashlib
from datetime import datetime


class Blockchain:
    def __init__(self, storage_file: Path | None = None):
        self.chain = []
        self.pending_transactions = []
        self.storage_file = storage_file
        self.filenames = {}


        if self.storage_file and self.storage_file.exists():
            self._load()
        else:
            self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": [],
            "previous_hash": "0",
        }
        genesis["hash"] = self._hash_block(genesis)
        self.chain.append(genesis)
        self._save()

    def _hash_block(self, block: dict) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        return hashlib.sha256(
            json.dumps(block_copy, sort_keys=True).encode()
        ).hexdigest()

    def add_transaction(self, tx: dict):
        self.pending_transactions.append(tx)

    def mine_pending_transactions(self):
        last = self.chain[-1]
        block = {
            "index": len(self.chain),
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": self.pending_transactions,
            "previous_hash": last["hash"],
        }
        block["hash"] = self._hash_block(block)
        self.chain.append(block)
        self.pending_transactions = []
        self._save()

    def get_all_transactions(self):
        out = []
        for block in self.chain:
            for tx in block["transactions"]:
                out.append({**tx, "block": block["index"]})
        return out

    def _save(self):
        if self.storage_file:
            with open(self.storage_file, "w") as f:
                json.dump(self.chain, f, indent=2)

    def _load(self):
        with open(self.storage_file, "r") as f:
            self.chain = json.load(f)
