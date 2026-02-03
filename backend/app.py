"""
Cloud Seal PoC - FastAPI Backend
"""
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import asyncio

from config import BASE_DIR, DATA_DIR, BLOCKCHAIN_FILE, REFCOUNT_FILE

from encryption import (
    generate_content_hash,
    generate_convergent_key,
    encrypt_file,
    decrypt_file
)


from bloom_filter import BloomFilter
from blockchain_distributed import DistributedBlockchain
from reference_counter import ReferenceCounter
from ipfs_manager import IPFSManager

# Enhanced components
from ai_deduplication import AIDeduplicationEngine
from pcq_kyber import PQCKeyManager, HybridEncryption

app = FastAPI(title="Cloud Seal PoC", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For PoC (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allows X-Tenant-ID
)

# === Initialize components ===
bloom = BloomFilter()
blockchain = DistributedBlockchain(
    node_id="main_node",
    storage_file=BLOCKCHAIN_FILE,
    authorized_validators=["main_node"]
)
ref_counter = ReferenceCounter(REFCOUNT_FILE)
ipfs = IPFSManager(DATA_DIR / "ipfs")

# AI & PQC initialization
pqc_manager = PQCKeyManager(storage_dir=DATA_DIR / "pqc_keys", security_level=768)
hybrid_crypto = HybridEncryption(pqc_manager)
ai_engine = AIDeduplicationEngine(model_path=DATA_DIR / "ai_model.pkl")

TENANT_SECRET = "demo-secret"  # PoC only


def require_headers(tenant_id: Optional[str]):
    if not tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required")


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_tenant_id: Optional[str] = Header(None),
    use_pqc: bool = False,
    use_ai: bool = False
):
    require_headers(x_tenant_id)

    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Empty file")

    # Content hash (CID base)
    content_hash = generate_content_hash(raw)

    # === AI-Enhanced Duplicate Detection ===
    ai_check_result = None
    if use_ai and ai_engine.cnn.is_trained:
        # Check against existing files using AI
        existing_files = ref_counter.get_all_files()
        for existing in existing_files:
            existing_cid = existing["cid"]
            # Try to get existing content (limited for demo if large)
            existing_content = ipfs.get_bytes("Qm" + existing_cid[:46])
            if existing_content:
                is_similar, similarity = ai_engine.check_similarity(raw, existing_content)
                if is_similar:
                    ai_check_result = {
                        "ai_detected": True, 
                        "similarity_score": similarity, 
                        "matched_cid": existing_cid,
                        "match_type": "SOFT" if existing_cid != content_hash else "HARD"
                    }
                    # In this enhanced version, we ONLY perform hard deduplication if the hashes match.
                    # AI is used for "Similarity Suggestions" and "Near-Duplicate" flagging.
                    # If we wanted "Fuzzy Deduplication", we would set content_hash = existing_cid here.
                    break

    # Bloom filter check (Standard Hard Deduplication)
    maybe_duplicate = bloom.check(content_hash)

    # Reference counter
    status = ref_counter.add_reference(content_hash, x_tenant_id, file.filename)

    if status == "NEW":
        # Encrypt + store
        if use_pqc:
            try:
                # Ensure tenant has keys
                try: pqc_manager.get_tenant_public_key(x_tenant_id)
                except FileNotFoundError: pqc_manager.generate_tenant_keys(x_tenant_id)
                
                encrypted, metadata = hybrid_crypto.encrypt_file_hybrid(raw, x_tenant_id)
                encryption_method = "AES-256 + Kyber-768 (PQC)"
            except Exception as e:
                print(f"PQC failed: {e}")
                key = generate_convergent_key(raw, x_tenant_id, TENANT_SECRET)
                encrypted = encrypt_file(raw, key)
                encryption_method = "AES-256 (Classical)"
        else:
            key = generate_convergent_key(raw, x_tenant_id, TENANT_SECRET)
            encrypted = encrypt_file(raw, key)
            encryption_method = "AES-256 (Classical)"

        cid = ipfs.add_bytes(encrypted)
        ipfs.pin_file(cid, {"owners": [x_tenant_id]})
        bloom.add(content_hash)

        blockchain.add_transaction({
            "action": "UPLOAD_NEW",
            "tenant_id": x_tenant_id,
            "file_name": file.filename,
            "file_cid": content_hash,
            "encryption": encryption_method,
            "ai_enhanced": use_ai,
            "ai_similarity": ai_check_result["similarity_score"] if ai_check_result else None
        })
        blockchain.mine_pending_transactions()

        return {
            "status": "stored",
            "cid": content_hash,
            "deduplicated": False,
            "encryption": encryption_method,
            "ai_details": ai_check_result
        }

    # Duplicate upload (Exact Match)
    blockchain.add_transaction({
        "action": "UPLOAD_DUPLICATE",
        "tenant_id": x_tenant_id,
        "file_name": file.filename,
        "file_cid": content_hash,
        "ai_match": ai_check_result is not None,
        "match_type": "HARD"
    })
    blockchain.mine_pending_transactions()

    return {
        "status": "linked",
        "cid": content_hash,
        "deduplicated": True,
        "ai_details": ai_check_result
    }


@app.post("/delete/{cid}")
def delete_file(cid: str, x_tenant_id: Optional[str] = Header(None)):
    require_headers(x_tenant_id)

    remaining, should_delete = ref_counter.remove_reference(cid, x_tenant_id)

    blockchain.add_transaction({
        "action": "DELETE",
        "tenant_id": x_tenant_id,
        "file_cid": cid,
        "remaining_refs": remaining
    })
    blockchain.mine_pending_transactions()

    if should_delete:
        ipfs.unpin_file("Qm" + cid[:46])

    return {
        "cid": cid,
        "remaining_refs": remaining,
        "deleted_from_storage": should_delete
    }


@app.get("/files")
def list_all_files():
    return ref_counter.get_all_files()


@app.get("/files/{tenant_id}")
def list_files_for_tenant(tenant_id: str):
    return [
        f for f in ref_counter.get_all_files()
        if tenant_id in f["owners"]
    ]


@app.get("/system/status")
def system_status():
    """Return system status matching frontend expectations"""
    total_files = len(ref_counter.get_all_files())
    # Simulation: IPFS unique files (pins)
    unique_files = len(ipfs.list_pins())
    dedup_ratio = 1 - (unique_files / max(1, total_files))

    return {
        "status": "online",
        "blockchain": {
            "chain_length": len(blockchain.chain),
            "pending_transactions": len(blockchain.pending_transactions),
            "validator": blockchain.node_id,
            "chain_valid": blockchain.validate_chain()
        },
        "storage": {
            "total_files": total_files,
            "unique_files": unique_files,
            "deduplication_ratio": dedup_ratio
        },
        "ai": {
            "trained": ai_engine.cnn.is_trained,
            "status": "active"
        },
        "pqc": {
            "algorithm": f"Kyber-{pqc_manager.kyber.security_level}",
            "status": "active"
        }
    }


@app.get("/audit")
def audit_log():
    return blockchain.get_all_transactions()

@app.get("/blockchain/stats")
def blockchain_stats():
    return blockchain.get_stats()

@app.get("/pqc/info")
def pqc_info():
    return {
        "algorithm": f"Kyber-{pqc_manager.kyber.security_level}",
        "nist_level": 3,
        "quantum_resistant": True,
        "key_size": pqc_manager.kyber.pk_size
    }

@app.get("/ai/stats")
def ai_stats():
    return {
        "trained": ai_engine.cnn.is_trained,
        "model_type": "CNN Siamese Network",
        "input_shape": [256, 1]
    }

@app.post("/ai/train")
async def train_ai_model(epochs: int = 5):
    all_files = ref_counter.get_all_files()
    if len(all_files) < 2:
        raise HTTPException(400, "Not enough files to train")
    
    # Simple simulation of training for PoC
    await asyncio.sleep(2) 
    ai_engine.cnn.is_trained = True
    tp = len(all_files) * 128 # simulated pairs
    return {"status": "trained", "epochs": epochs, "training_pairs": tp}

@app.post("/share")
async def share_file(
    file_cid: str,
    x_sender_id: str = Header(..., alias="X-Sender-ID"),
    x_receiver_id: str = Header(..., alias="X-Receiver-ID")
):
    if not ref_counter.is_owner(file_cid, x_sender_id):
        raise HTTPException(403, "Sender doesn't own file")
    
    # PQ Key Exchange
    ciphertext = hybrid_crypto.share_file_quantum_safe(file_cid, x_sender_id, x_receiver_id)
    ref_counter.add_reference(file_cid, x_receiver_id, "shared_file")
    
    blockchain.add_transaction({
        "action": "SHARE_PQC",
        "tenant_id": x_sender_id, # Required field for blockchain
        "sender": x_sender_id,
        "receiver": x_receiver_id,
        "file_cid": file_cid,
        "pqc_key_encapsulated": True
    })
    blockchain.mine_pending_transactions()
    
    return {"status": "shared", "shared_with": x_receiver_id}

@app.get("/")
async def read_index():
    return FileResponse(BASE_DIR.parent / "frontend" / "index.html")

# Mount static files (CSS, JS, Assets)
app.mount("/frontend", StaticFiles(directory=BASE_DIR.parent / "frontend"), name="frontend")
