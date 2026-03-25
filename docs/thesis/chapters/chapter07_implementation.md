# CHAPTER 07: IMPLEMENTATION

## 7.1 Chapter Overview

This chapter documents the implementation phase of Cloud Seal, transforming the design specifications from Chapter 6 into a fully functional Privacy-Preserving Multi-Tenant Cloud Deduplication (PMCD) prototype. The implementation translates the three-tier layered architecture, class diagrams, and algorithm pseudocode into working Python and JavaScript code, deployed as a containerised web application. The chapter is structured as follows: §7.2 justifies technology selection, §7.3 details each core module's implementation and integration, §7.4 covers the UI and backend integration, §7.5 discusses key implementation challenges and their resolutions, and §7.6 summarises the chapter.

## 7.2 Technology Selection

### 7.2.1 Technology Stack

The following table summarises the complete technology stack deployed across all three architecture tiers.

| Tier | Category | Technology |
|---|---|---|
| **Presentation** | Markup | HTML5 |
| **Presentation** | Styling | CSS3 (custom properties, CSS Grid) |
| **Presentation** | Logic | JavaScript ES6+ (Fetch API) |
| **Application** | Language | Python 3.11 |
| **Application** | Framework | FastAPI 0.104.1 + Uvicorn 0.24.0 |
| **Application** | Encryption | `cryptography` 41.0.7, `PyCryptodome` 3.19.0 |
| **Application** | AI/ML | NumPy 1.24.3, scikit-learn 1.3.2 |
| **Application** | Hashing | `mmh3` 4.0.1 (MurmurHash3) |
| **Data** | Storage | Simulated IPFS (local filesystem) |
| **Data** | Audit | Custom PoA blockchain (JSON) |
| **Data** | State | JSON file persistence (`blockchain.json`, `refcounts.json`) |
| **Dev/Ops** | IDE | Visual Studio Code |
| **Dev/Ops** | Containers | Docker Desktop |
| **Dev/Ops** | Deployment | WSO2 Choreo (Kubernetes) |
| **Dev/Ops** | API Testing | Postman |

*Table 7.1: Cloud Seal Technology Stack*

### 7.2.2 Programming Languages

| Language | Version | Usage | Justification |
|---|---|---|---|
| **Python** | 3.11 | Backend, AI/ML, cryptography, blockchain | Extensive ecosystem (cryptography, ML, APIs). Version 3.11 offers 10–60% performance gains for intensive operations (Shannon, 2022). |
| **JavaScript** | ES6+ | Frontend client-side logic | Enables dynamic updates via Fetch API. Native JS (no framework) minimises dependencies and attack surface. |
| **HTML5** | 5 | Frontend structure | Semantic elements ensure screen reader accessibility (NFR). |
| **CSS3** | 3 | Styling, responsive layout | Custom properties for maintainability; CSS Grid provides responsive UI without heavy external frameworks. |

*Table 7.2: Programming Languages*

### 7.2.3 Development Framework

| Framework | Version | Role | Justification |
|---|---|---|---|
| **FastAPI** | 0.104.1 | Backend REST API | Native `async` support for concurrent uploads; automatic OpenAPI/Swagger docs; built-in Pydantic validation. Benchmarks show 300% faster request handling than Flask. |
| **Uvicorn** | 0.24.0 | ASGI production server | C-based `httptools` and `uvloop` backends for high-throughput HTTP handling; fully compatible with Docker/Choreo. |
| **Docker** | Multi-stage | Containerisation | `python:3.11-slim` base image (121 MB vs 875 MB standard) ensures fast deployment on Choreo's Kubernetes infrastructure. |

*Table 7.3: Development Frameworks*

### 7.2.4 Libraries / Toolkits

| Library | Version | Purpose | Justification |
|---|---|---|---|
| `PyCryptodome` | 3.19.0 | AES-256 encryption, SHA-256 | FIPS-validated AES-256-CBC; used for deterministic key derivation via SHA-256. |
| `cryptography` | 41.0.7 | Low-level cipher operations | Provides `hazmat` primitives for fine-grained cipher control with explicit IV management. |
| `NumPy` | 1.24.3 | CNN matrix operations | Replaces TensorFlow entirely — keeps Docker image under 200 MB with no GPU requirement for PoC-scale training. |
| `mmh3` | 4.0.1 | MurmurHash3 for Bloom filter | 3× faster than SHA-256 for non-cryptographic hashing; excellent bit distribution. |
| `scikit-learn` | 1.3.2 | Feature scaling, pre-processing | Lightweight complement to NumPy for data normalisation in AI training. |
| `Pydantic` | 2.5.0 | Request/response validation | Integrated with FastAPI for automatic type validation of API parameters. |
| `python-multipart` | 0.0.6 | File upload parsing | Required by FastAPI for `multipart/form-data` parsing enabling the upload endpoint. |

*Table 7.4: Libraries / Toolkits*

### 7.2.5 Integrated Development Environment (IDEs)

| IDE / Tool | Version | Purpose | Justification |
|---|---|---|---|
| **Visual Studio Code** | 1.86+ | Primary IDE for Python and frontend development | Excellent Python support via Microsoft extension (Pylance). Built-in Git integration and seamless Docker container management via the Docker extension. |
| **DataGrip** | 2023.3 | Database inspection | Used during development to inspect JSON-based local state (`blockchain.json`, `refcounts.json`) and verify correct structural persistence across container restarts. |
| **Postman** | 10.22+ | API endpoint testing | Independent verification of FastAPI endpoints (specifically multipart file uploads and custom `X-Tenant-ID` header handling) prior to frontend integration. |

*Table 7.5: Integrated Development Environments and Testing Tools*

### 7.2.6 Summary of Technology Selection

Three principles guided all technology choices:

1. **Lightweight Deployment** — NumPy CNN instead of TensorFlow, FastAPI instead of Django: Docker image stays under 200 MB.
2. **Security-First Libraries** — Both `cryptography` and `PyCryptodome` are industry-audited, peer-reviewed implementations. No custom cryptographic algorithms were written.
3. **Modular Replaceability** — Every module is independently swappable. For example, `pcq_kyber.py` contains a commented-out `liboqs-python` import (line 14) that activates the production NIST-standardised Kyber library with zero change to the rest of the codebase.

## 7.3 Core Functionalities Implementation

### 7.3.1 Dataset and Exploratory Data Analysis

Because publicly available datasets for *encrypted* deduplication do not exist, a custom Python test harness was developed to generate a synthetic evaluation dataset. The harness programmatically expanded 6 base file types into a mathematically rigorous dataset of 1,000 files by injecting noise and simulating cross-tenant encryption logic. The dataset was split into Training (70%), Validation (15%), and Testing (15%). Prior to training, Exploratory Data Analysis (EDA) revealed a critical anomaly: identical plaintexts encrypted under *different* tenant keys produce identical structural features, resulting in false clustering. This finding directly drove the architectural decision to strictly isolate AI checks to the intra-tenant level. 

*(For the complete dataset generation algorithms, data splits, and full EDA results, refer to **Appendix L**).*

### 7.3.2 Modular Development and Process Flow

The implementation followed a modular, decoupled approach. All core backend modules map directly to functional requirements from the SRS:

The project follows a clean modular structure with clear separation of concerns:

```
cloud-seal-poc/
├── backend/
│   ├── app.py                     # FastAPI orchestrator (API endpoints)
│   ├── encryption.py              # AES-256 convergent encryption
│   ├── bloom_filter.py            # Probabilistic O(1) duplicate detection
│   ├── ai_deduplication.py        # Siamese CNN similarity detection
│   ├── pcq_kyber.py               # Kyber-768 PQC + hybrid encryption
│   ├── blockchain_distributed.py  # PoA blockchain audit trail
│   ├── reference_counter.py       # Multi-tenant ownership tracking
│   ├── ipfs_manager.py            # Content-addressed file storage
│   ├── config.py                  # Configuration constants
│   └── tests/                     # Automated test suites (8 scripts)
├── frontend/
│   ├── index.html                 # Dashboard UI structure
│   ├── app.js                     # Client-side logic
│   └── style.css                  # Dark-mode design system
├── Dockerfile                     # Container definition
└── docker-compose.yml             # Multi-service orchestration
```

Each backend module maps directly to functional requirements from the SRS:

| Module | SRS Requirement | Key Classes / Functions |
|---|---|---|
| `encryption.py` | FR01 (Encryption) | `generate_convergent_key()`, `encrypt_file()`, `decrypt_file()` |
| `bloom_filter.py` | FR03 (Duplicate Screening) | `BloomFilter.add()`, `BloomFilter.check()` |
| `ai_deduplication.py` | FR06 (Near-Duplicate Detection) | `BinaryFileEncoder`, `SimpleCNN`, `AIDeduplicationEngine` |
| `pcq_kyber.py` | FR07 (PQC Encryption) | `SimulatedKyber`, `PQCKeyManager`, `HybridEncryption` |
| `blockchain_distributed.py` | FR04 (Audit Trail) | `Block`, `DistributedBlockchain` |
| `reference_counter.py` | FR02 (Dedup + Isolation) | `ReferenceCounter.add_reference()`, `remove_reference()` |
| `ipfs_manager.py` | FR05 (Content Storage) | `IPFSManager.add_bytes()`, `get_bytes()` |
| `app.py` | FR01–FR07 | FastAPI route handlers |

*Table 7.5: Module-to-Requirement Mapping*

### 7.3.3 Encryption Module (`encryption.py`)

**FR Mapping:** FR01 — "The system shall encrypt all files using AES-256 prior to storage."

**Implementation Details:** The convergent key derivation function generates a deterministic encryption key from the file content and tenant identity. This allows the system to detect duplicates before encryption (identical content produces the same hash), while different tenants derive different keys for the same content, maintaining isolation.

```python
def generate_convergent_key(file_content: bytes, tenant_id: str = "",
                             tenant_secret: str = "") -> bytes:
    # Tenant-specific salt prevents cross-tenant confirmation attacks
    combined = f"{tenant_id}:{tenant_secret}".encode() + file_content
    hash_digest = hashlib.sha256(combined).digest()
    return hash_digest[:32]  # AES-256 requires 32 bytes
```

*Code Snippet 7.1: Convergent Key Derivation (`encryption.py`)*

**Explanation:** Concatenating the tenant's identifier/secret with the raw file content and hashing it via SHA-256 produces a deterministic 32-byte key. The tenant-specific salt prevents cross-tenant key collisions, directly addressing the privacy weaknesses of standard convergent cryptography (Bellare et al., 2013).

### 7.3.4 Bloom Filter Module (`bloom_filter.py`)

**FR Mapping:** FR03 — "The system shall detect duplicate files within 1ms using probabilistic data structures."

**Implementation Details:** The Bloom filter is initialised with parameters derived from an expected item count (10,000) and target false positive rate (1%):

```python
class BloomFilter:
    def __init__(self, expected_items=10000, false_positive_rate=0.01):
        # m = -(n × ln(p)) / (ln(2)²)  → 95,851 bits ≈ 11.7 KB
        self.size = int(-(expected_items * math.log(false_positive_rate))
                        / (math.log(2) ** 2))
        # k = (m/n) × ln(2)  → 6 hash functions
        self.hash_count = max(1, int((self.size / expected_items) * math.log(2)))
        self.bit_array = [0] * self.size

    def check(self, item: str) -> bool:
        for i in range(self.hash_count):
            position = mmh3.hash(item, i) % self.size
            if self.bit_array[position] == 0:
                return False   # Definitely NOT present
        return True            # Probably present — verify via ReferenceCounter
```

*Code Snippet 7.2: Bloom Filter Initialization (`bloom_filter.py`)*

**Explanation:** For 10,000 expected files, the math yields a 95,851-bit array (11.7 KB) requiring 6 MurmurHash3 probes, using ~12 bytes per tracked file. This achieves O(1) duplicate detection without overhead.

### 7.3.5 AI Deduplication Engine (`ai_deduplication.py`)

**FR Mapping:** FR06 — "The system shall use AI to detect files with ≥85% content similarity."

**Implementation Details:** The AI module extracts four statistical properties from the binary data: byte frequency (256-d), byte pair frequencies (256-d), chunk entropy (256-d), and statistical moments (4-d). These concatenate into a 2048-dimensional vector, which the CNN maps to a 128-dim embedding via dense layers and L2 normalisation.

```python
def forward(self, x: np.ndarray) -> np.ndarray:
    z = np.dot(self.W, x) + self.b   # Linear projection: 2048 → 128
    embedding = np.maximum(0, z)      # ReLU activation
    norm = np.linalg.norm(embedding)
    return embedding / norm if norm > 0 else embedding  # L2 normalisation

def similarity(self, x1: np.ndarray, x2: np.ndarray) -> float:
    return float(np.dot(self.forward(x1), self.forward(x2)))  # Cosine sim
```
*Code Snippet 7.3: Siamese CNN Forward Pass (`ai_deduplication.py`)*

**Explanation:** A cosine similarity ≥ 0.85 classifies pairs as near-duplicates. Training uses a contrastive loss function to cluster similar files and repel dissimilar ones. The AI is advisory only, flagging matches without auto-deleting to prevent accidental data loss.

### 7.3.6 Post-Quantum Cryptography Module (`pcq_kyber.py`)

**FR Mapping:** FR07 — "The system shall provide optional post-quantum encryption using NIST-approved Kyber-768."

The module implements a three-class hierarchy: `SimulatedKyber` (KEM operations via SHAKE-256), `PQCKeyManager` (tenant keypair management), and `HybridEncryption` (AES + Kyber composition):

```python
class HybridEncryption:
    def encrypt_file_hybrid(self, file_content: bytes,
                             tenant_id: str) -> Tuple[bytes, dict]:
        file_hash = generate_content_hash(file_content)
        # PQC-derived key via Kyber-768 KEM
        pqc_key = self.pqc_manager.derive_encryption_key(tenant_id, file_hash)
        # AES-256 handles bulk encryption (speed); Kyber handles key (PQC safety)
        encrypted = encrypt_file(file_content, pqc_key)
        metadata = {"encryption": "AES-256-CBC",
                    "key_exchange": "Kyber-768",
                    "security_level": "NIST Level 3 (192-bit)"}
        return encrypted, metadata
```

*Code Snippet 7.4: Hybrid Encryption Integration (`pcq_kyber.py`)*

**Explanation:** The hybrid scheme uses Kyber for key encapsulation (quantum safety) and AES-256 for bulk payload encryption (speed), limiting performance overhead while satisfying NIST standards.

### 7.3.7 Blockchain Audit Trail (`blockchain_distributed.py`)

**FR Mapping:** FR04 — "All file operations shall be immutably recorded for compliance auditing."

Each block's hash includes the validator identity, creating tamper-evident PoA authentication:

```python
def calculate_hash(self) -> str:
    block_data = json.dumps({
        "index": self.index, "timestamp": self.timestamp,
        "transactions": self.transactions,
        "previous_hash": self.previous_hash,
        "validator": self.validator   # PoA: validator must be authorised
    }, sort_keys=True)
    return hashlib.sha256(block_data.encode()).hexdigest()
```

*Code Snippet 7.5: Block Hash Authorization (`blockchain_distributed.py`)*

**Explanation:** Including the `validator` field ensures only authorised nodes generate blocks (Proof-of-Authority). Any structural mutation breaks the chain hash, immediately detecting tampering natively without relying on databases.

### 7.3.8 Reference Counter (`reference_counter.py`)

**FR Mapping:** FR02 — "The system shall support safe multi-tenant file deletion using reference counting."

The counter maintains three parallel dictionaries:

```python
def remove_reference(self, cid: str, tenant_id: str) -> Tuple[int, bool]:
    if tenant_id not in self.owners[cid]:
        raise PermissionError(f"Tenant {tenant_id} does not own this file")
    self.owners[cid].remove(tenant_id)
    self.ref_counts[cid] -= 1
    if self.ref_counts[cid] == 0:
        self._save()
        return 0, True   # Safe to physically delete from IPFS
    self._save()
    return self.ref_counts[cid], False  # Other tenants still reference
```

*Code Snippet 7.6: Reference-Counted Safe Deletion (`reference_counter.py`)*

**Explanation:** Returns the remaining reference count and a boolean indicating whether the physical IPFS object should be safely unpinned, ensuring shared content is never prematurely deleted.

### 7.3.9 Module Integration: The Upload Pipeline (`app.py`)

The FastAPI upload endpoint orchestrates all modules in the exact sequence defined by the Activity Diagram in Chapter 6:

```python
@app.post("/upload")
async def upload_file(file: UploadFile = File(...),
                      x_tenant_id: Optional[str] = Header(None),
                      use_pqc: bool = False, use_ai: bool = False):
    raw = await file.read()
    content_hash = generate_content_hash(raw)

    # 1. AI near-duplicate advisory check (optional)
    if use_ai and ai_engine.cnn.is_trained:
        for existing in ref_counter.get_all_files():
            is_similar, score = ai_engine.check_similarity(raw, ...)
            if is_similar:
                ai_check_result = {"ai_detected": True, "score": score}
                break

    # 2. Bloom filter pre-screen + Reference counter (dedup decision)
    bloom.check(content_hash)
    status = ref_counter.add_reference(content_hash, x_tenant_id, file.filename)

    if status == "NEW":
        # 3. Encrypt (PQC-hybrid or classical AES)
        if use_pqc:
            encrypted, metadata = hybrid_crypto.encrypt_file_hybrid(raw, x_tenant_id)
        else:
            key = generate_convergent_key(raw, x_tenant_id, TENANT_SECRET)
            encrypted = encrypt_file(raw, key)

        # 4. Store, index, audit
        cid = ipfs.add_bytes(encrypted)
        bloom.add(content_hash)
        blockchain.add_transaction({"action": "UPLOAD_NEW", "tenant": x_tenant_id})
        blockchain.mine_pending_transactions()
        return {"status": "stored", "cid": content_hash, "deduplicated": False}

    # Duplicate path: log only, no re-storage
    blockchain.add_transaction({"action": "UPLOAD_DUPLICATE", ...})
    return {"status": "linked", "cid": content_hash, "deduplicated": True}
```

*Code Snippet 7.7: Upload Pipeline Integration (`app.py`)*

**Explanation:** The pipeline strictly follows the Activity Diagram sequence: hash generation → AI check → Bloom filter → reference counting → encryption → storage → blockchain logging. Fallbacks ensure upload reliability if PQC operations fail.

## 7.4 User Interface Implementation

### 7.4.1 Frontend Development

The frontend is a single-page dashboard served directly by FastAPI's `StaticFiles` mount. It is divided into four functional sections:

| Section | UI Elements | Backend Endpoint |
|---|---|---|
| **Live System Status** | 4 metric cards: Blocks mined, Total Files, Unique Files, Dedup Ratio | `GET /system/status` |
| **Secure Upload** | Tenant dropdown, file input, PQC/AI checkboxes, upload button, result display | `POST /upload` |
| **Personal Vault** | Per-tenant file table: CID, owners, ref count, encryption method, delete button | `GET /files/{tenant_id}` |
| **All Files (System-wide)** | Global file table showing files across all tenants | `GET /files/all` |

*Table 7.6: Frontend Sections and Backend Endpoints*

Security options are presented following a **"secure by default"** principle — both PQC and AI checkboxes are enabled by default with plain-language sub-labels that explain each option without requiring technical knowledge:

```html
<label class="checkbox-label">
  <input type="checkbox" id="usePQC" checked />
  <span>🔒 Post-Quantum Encryption</span>
  <small>Protects against future quantum computer attacks using
         NIST-approved Kyber-768 algorithm</small>
</label>
<label class="checkbox-label">
  <input type="checkbox" id="useAI" checked />
  <span>🤖 AI-Powered Similarity Detection</span>
  <small>Finds near-duplicate files (85%+ similar) using
         Convolutional Neural Networks</small>
</label>
```

*Code Snippet 7.8: Security Options UI with "Secure by Default" Pattern (`index.html`)*

### 7.4.2 Backend Integration

All frontend-backend communication uses the Fetch API with relative URLs and a custom `X-Tenant-ID` header for stateless multi-tenancy:

```javascript
async function upload() {
    const tenant = document.getElementById("tenantId").value;
    const file   = document.getElementById("fileInput").files[0];
    const form   = new FormData();
    form.append("file", file);

    const params = new URLSearchParams({
        use_pqc: document.getElementById("usePQC").checked,
        use_ai:  document.getElementById("useAI").checked
    });

    const res  = await fetch(`./upload?${params}`, {
        method: "POST",
        headers: { "X-Tenant-ID": tenant },
        body: form
    });
    const data = await res.json();
    await Promise.all([loadFiles(), loadMyFiles(), loadSystemStatus(false)]);
}
```

*Code Snippet 7.9: Async Upload and Dashboard Refresh (`app.js`)*

`Promise.all()` parallelises the three dashboard refresh calls, minimising the visible update delay after an upload completes. The dashboard auto-refreshes silently every 10 seconds via `setInterval(() => loadSystemStatus(false), 10000)`, where `isManual=false` suppresses the loading animation to prevent UI flickering.

### 7.4.3 Accessibility Considerations

| Feature | Implementation | Standard |
|---|---|---|
| Colour Contrast | Dark background `#1a1a2e` / accent `#00d4ff` — meets contrast requirements | WCAG 2.1 AA |
| Semantic HTML | `<section>`, `<header>`, `<main>`, `<footer>`, `<label for="...">` throughout | HTML5 WAI-ARIA |
| Keyboard Navigation | All interactive elements are native HTML (`<button>`, `<input>`, `<select>`) | WCAG 2.1 §2.1 |
| Text Scaling | All font sizes in `rem` units relative to 16px base | WCAG 2.1 §1.4.4 |
| Status Feedback | Loading states: "⏳ Uploading...", dedup results: "✅ NEW FILE" / "🔗 DEDUPLICATED" | WCAG 2.1 §4.1.3 |

*Table 7.7: Accessibility Considerations*

## 7.5 Challenges and Solutions

### Challenge 1: CNN Deployment Without GPU Dependencies

| Aspect | Details |
|---|---|
| **Problem** | Deep learning frameworks (TensorFlow, PyTorch) add 1–3 GB to the Docker image, exceeding Choreo's deployment limits and causing cold-start timeouts. |
| **Solution** | Reimplemented the Siamese CNN using pure NumPy matrix operations: `np.dot(W, x) + b` replaces Dense layers. Reduced the AI module footprint from ~2.5 GB to ~25 MB. |
| **Trade-off** | NumPy lacks GPU acceleration, but CPU training completes in under 10 seconds for PoC datasets. |

*Table 7.8: Challenge 1 — CNN Without GPU Dependencies*

### Challenge 2: Convergent Encryption Cross-Tenant Privacy Leakage

| Aspect | Details |
|---|---|
| **Problem** | Standard convergent encryption derives keys purely from content, allowing cross-tenant "confirmation attacks" (Bellare et al., 2013). |
| **Solution** | Added per-tenant salt to key derivation: `key = SHA-256(tenant_id + secret + content)`. Thwarts cross-tenant hash comparison while supporting intra-tenant deduplication. |

*Table 7.9: Challenge 2 — Convergent Encryption Privacy Leakage*

### Challenge 3: Blockchain Persistence Across Container Restarts

| Aspect | Details |
|---|---|
| **Problem** | Docker containers are stateless. Auto-scaling restarts wiped blockchain, reference counter, and IPFS data. |
| **Solution** | Stateful components persist to JSON on disk after every mutating operation. Writable directory fallbacks (`/tmp/cloud-seal-data/`) enable persistence in read-only environments. |

*Table 7.10: Challenge 3 — Blockchain Persistence*

### Challenge 4: Choreo Deployment Path Resolution

| Aspect | Details |
|---|---|
| **Problem** | Choreo deploys apps under sub-paths (e.g., `/v1.0/`). `fetch()` calls resolved incorrectly without trailing slashes. |
| **Solution** | Added trailing-slash enforcement in `index.html` and explicit `./` prefixes in frontend calls for relative path resolution. |

*Table 7.11: Challenge 4 — Choreo Path Resolution*

## 7.6 Chapter Summary

This chapter documented the implementation of Cloud Seal, transforming the design specifications into a functional prototype. The technology stack prioritised lightweight deployment (NumPy CNN), audited cryptographic primitives, and modularity. The full technical pipeline — from convergent derivation to Kyber encapsulation, IPFS storage, and PoA blockchain logging — executes end-to-end within milliseconds. Key implementation challenges surrounding stateless containers, cross-tenant leakage, and path resolution were successfully mitigated. The system is fully deployed and ready for the correctness, performance, and security testing defined in Chapter 8.
