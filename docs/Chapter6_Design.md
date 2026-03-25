# Chapter 6: Design

## 6.1 Chapter Overview

This chapter presents the design of **Cloud Seal**, a Privacy-Preserving Multi-Tenant Cloud Deduplication (PMCD) system. The design translates the functional and non-functional requirements identified in the SRS into a concrete software architecture, detailed component designs, and user interface specifications.

The chapter is structured as follows:

- **Section 6.2** defines the design goals derived from the non-functional requirements, establishing the quality attributes that the system must maintain throughout implementation.
- **Section 6.3** presents the high-level system architecture using a layered design, showing how all components interact across tiers.
- **Section 6.4** provides detailed design diagrams including class diagrams, sequence diagrams, and activity diagrams following the Object-Oriented Analysis and Design Methodology (OOADM).
- **Section 6.5** describes the AI/ML algorithm design, presenting the Siamese CNN architecture and the deduplication pipeline pseudocode.
- **Section 6.6** presents the UI wireframes and design considerations for usability and accessibility.
- **Section 6.7** summarises the chapter.

The design follows the **Object-Oriented Analysis and Design Methodology (OOADM)**, selected for its suitability in modelling the system's encapsulated, modular components (encryption, blockchain, AI engine, storage management), each of which maps naturally to object-oriented classes with well-defined interfaces.

---

## 6.2 Design Goals

The design goals are derived directly from the Non-Functional Requirements (NFRs) identified in the SRS chapter. Each goal defines a quality attribute that is maintained system-wide through architectural and implementation decisions.

| Design Goal | NFR Reference | Description | Design Strategy |
|-------------|---------------|-------------|-----------------|
| **Performance** | NFR-01 | The system shall process file uploads with <350ms latency and support >120 files/sec sustained throughput. | Bloom filter provides O(1) duplicate lookups; convergent encryption enables hash-first-then-encrypt pipeline; asynchronous FastAPI endpoints for concurrent request handling. |
| **Security** | NFR-02 | All files shall be encrypted using AES-256 at minimum, with optional Kyber-768 post-quantum protection. | Layered encryption: convergent key derivation → AES-256-CBC encryption → optional Kyber-768 key encapsulation. All operations occur on server-side to prevent plaintext leakage. |
| **Scalability** | NFR-03 | The system shall support 100+ tenants with linear scaling of storage savings. | Reference counting for shared file ownership; Bloom filter sized for 10,000 items; Docker containerisation for horizontal deployment. |
| **Accuracy** | NFR-04 | Deduplication accuracy shall exceed 96%, with Bloom filter false positive rate below 1%. | SHA-256 content hashing for exact matching (100% true positive rate); Bloom filter with mathematically optimised parameters; CNN similarity threshold of 0.85 for near-duplicates. |
| **Usability** | NFR-05 | The dashboard shall provide real-time status updates and require no technical knowledge to operate. | Single-page web application with auto-refreshing dashboard; checkbox-based security options with plain-language descriptions; responsive CSS grid layout. |
| **Reliability** | NFR-06 | System shall maintain 99.9% uptime with <60s recovery from failures. | Persistent JSON storage for reference counts; blockchain saved to disk after each mining operation; graceful error handling with fallback encryption. |
| **Auditability** | NFR-07 | All file operations shall be immutably recorded for compliance verification. | Proof-of-Authority blockchain with tamper-evident hash chains; every upload, delete, and share operation logged with timestamps and tenant IDs. |
| **Privacy** | NFR-08 | Multi-tenant data isolation shall be enforced cryptographically. | Per-tenant convergent keys with tenant-specific salt; reference counter tracks ownership independently; no cross-tenant data access without explicit sharing. |

---

## 6.3 System Architecture Diagram

### 6.3.1 Architecture Overview

Cloud Seal follows a **three-tier layered architecture** that separates concerns across Presentation, Application Logic, and Data/Storage tiers. This architecture was chosen for its clear separation of responsibilities, ease of testing, and alignment with the Docker deployment model.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER (Client-Side)                      │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │  index.html   │  │   app.js     │  │        style.css             │  │
│  │  (Structure)  │  │  (Logic)     │  │     (Light Mode UI)          │  │
│  │              │  │              │  │                              │  │
│  │ • Dashboard  │  │ • API calls  │  │ • CSS Grid Layout            │  │
│  │ • Upload     │  │ • DOM update │  │ • Responsive Design          │  │
│  │   Form       │  │ • Tenant     │  │ • Accessibility              │  │
│  │ • File Lists │  │   switching  │  │   Contrast                   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
│                           │                                             │
│                    HTTP REST API (Fetch)                                │
│                           │                                             │
├───────────────────────────┼─────────────────────────────────────────────┤
│                    APPLICATION TIER (Server-Side)                       │
│                           │                                             │
│  ┌────────────────────────┴──────────────────────────────────────────┐  │
│  │                  FastAPI Application (app.py)                      │  │
│  │                                                                    │  │
│  │   Endpoints:                                                       │  │
│  │   POST /upload          GET  /system/status                        │  │
│  │   DELETE /delete/{cid}  GET  /files/all                            │  │
│  │   POST /share           GET  /files/{tenant_id}                    │  │
│  │   GET  /blockchain/log  POST /ai/train                             │  │
│  └──────┬──────────┬──────────┬──────────┬──────────┬────────────────┘  │
│         │          │          │          │          │                   │
│  ┌──────┴──────┐┌──┴───┐┌────┴────┐┌────┴────┐┌───┴──────┐            │
│  │ Encryption  ││Bloom ││   AI    ││  PQC    ││Reference │            │
│  │ Module      ││Filter││ Engine  ││ Kyber   ││ Counter  │            │
│  │             ││      ││         ││         ││          │            │
│  │encryption.py││bloom_││ai_dedup-││pcq_     ││reference_│            │
│  │             ││filter││lication.││kyber.py ││counter.py│            │
│  │             ││.py   ││py       ││         ││          │            │
│  └──────┬──────┘└──┬───┘└────┬────┘└────┬────┘└───┬──────┘            │
│         │          │         │          │         │                    │
├─────────┼──────────┼─────────┼──────────┼─────────┼────────────────────┤
│                    DATA / STORAGE TIER                                  │
│                           │                                             │
│  ┌────────────────────────┼──────────────────────────────────────────┐  │
│  │                        │                                          │  │
│  │  ┌──────────────┐  ┌───┴──────────┐  ┌───────────────────────┐   │  │
│  │  │ IPFS Manager │  │  Blockchain  │  │  JSON Persistent      │   │  │
│  │  │              │  │  (PoA)       │  │  Storage               │   │  │
│  │  │ ipfs_        │  │              │  │                        │   │  │
│  │  │ manager.py   │  │ blockchain_  │  │ • ref_counts.json     │   │  │
│  │  │              │  │ distributed  │  │ • blockchain.json     │   │  │
│  │  │ Encrypted    │  │ .py          │  │ • pqc_keys/           │   │  │
│  │  │ File Storage │  │              │  │ • ipfs/pins.json      │   │  │
│  │  │              │  │ Immutable    │  │                        │   │  │
│  │  │              │  │ Audit Trail  │  │                        │   │  │
│  │  └──────────────┘  └──────────────┘  └───────────────────────┘   │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│                    Docker Container (Dockerfile)                        │
└─────────────────────────────────────────────────────────────────────────┘
```
*Figure 6.1: Three-Tier System Architecture of Cloud Seal*

### 6.3.2 Tier Descriptions

**Tier 1: Presentation Layer**

The Presentation Tier consists of three static files served by the backend:

- **`index.html`** – Defines the UI structure including the dashboard, upload form, tenant selector, security options, and file lists. Uses semantic HTML5 elements for accessibility.
- **`app.js`** – Contains all client-side logic: API communication via Fetch API, DOM manipulation for real-time dashboard updates, tenant switching, file upload handling, and 10-second auto-refresh polling.
- **`style.css`** – Implements a professional light-mode design system with CSS custom properties, responsive CSS Grid layout, and smooth transitions for interactive elements.

Communication between the Presentation and Application tiers occurs through RESTful HTTP requests (JSON payloads) using the Fetch API.

**Tier 2: Application Logic Layer**

The Application Tier is the core of the system, built with **FastAPI** (Python 3). It orchestrates all business logic through six specialised modules:

| Module | Responsibility |
|--------|----------------|
| `encryption.py` | AES-256-CBC encryption with convergent key derivation (SHA-256 based) |
| `bloom_filter.py` | Probabilistic O(1) duplicate detection using MurmurHash3 |
| `ai_deduplication.py` | CNN-based encrypted similarity detection (Siamese architecture) |
| `pcq_kyber.py` | Post-quantum key encapsulation (Kyber-768) and hybrid encryption |
| `reference_counter.py` | Multi-tenant file ownership tracking with safe deletion |
| `app.py` | FastAPI endpoint orchestration and request routing |

**Tier 3: Data/Storage Layer**

The Data Tier manages all persistent state:

- **IPFS Manager** (`ipfs_manager.py`) – Content-addressable storage for encrypted files. Uses SHA-256-based CIDs (Content Identifiers) for deterministic addressing. Simulated for PoC with file system storage, replaceable with real IPFS in production.
- **Distributed Blockchain** (`blockchain_distributed.py`) – Proof-of-Authority blockchain for immutable audit logging. Supports multi-node validation, conflict resolution via longest-valid-chain consensus, and persistent JSON serialisation.
- **JSON Persistent Storage** – Reference counts, blockchain state, PQC keys, and IPFS pin metadata are stored as JSON files for crash recovery and state persistence.

---

## 6.4 Detailed Design

The following detailed design diagrams follow the Object-Oriented Analysis and Design Methodology (OOADM), using UML notation for class, sequence, and activity diagrams.

### 6.4.1 Class Diagram

The class diagram shows the relationships between the system's core classes and their attributes and methods.

```
┌─────────────────────────────────────────────┐
│              FastAPI Application             │
│              (app.py)                        │
│─────────────────────────────────────────────│
│ - bloom: BloomFilter                        │
│ - blockchain: DistributedBlockchain         │
│ - ref_counter: ReferenceCounter             │
│ - ipfs: IPFSManager                         │
│ - pqc_manager: PQCKeyManager               │
│ - hybrid_crypto: HybridEncryption           │
│ - ai_engine: AIDeduplicationEngine          │
│─────────────────────────────────────────────│
│ + upload_file(file, tenant_id, use_pqc,     │
│               use_ai): dict                 │
│ + delete_file(cid, tenant_id): dict         │
│ + list_all_files(): list                    │
│ + list_files_for_tenant(tenant_id): list    │
│ + system_status(): dict                     │
│ + share_file(cid, sender, receiver): dict   │
│ + audit_log(): list                         │
│ + train_ai_model(epochs): dict              │
└──┬────────┬────────┬────────┬────────┬──────┘
   │        │        │        │        │
   │ uses   │ uses   │ uses   │ uses   │ uses
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼

┌──────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   BloomFilter    │  │  ReferenceCounter     │  │    IPFSManager       │
│──────────────────│  │──────────────────────│  │──────────────────────│
│ - size: int      │  │ - ref_counts: dict   │  │ - storage_dir: Path  │
│ - hash_count: int│  │ - owners: dict       │  │ - pinned_files: dict │
│ - bit_array: list│  │ - filenames: dict    │  │──────────────────────│
│ - items_added:int│  │ - storage_file: Path │  │ + add_bytes(content) │
│──────────────────│  │──────────────────────│  │   -> str (CID)       │
│ + add(item: str) │  │ + add_reference(cid, │  │ + get_bytes(cid)     │
│ + check(item:str)│  │   tenant, filename)  │  │   -> bytes           │
│   -> bool        │  │   -> str             │  │ + pin_file(cid,      │
│ + get_stats()    │  │ + remove_reference(  │  │   metadata)          │
│   -> dict        │  │   cid, tenant)       │  │ + unpin_file(cid)    │
│                  │  │   -> (int, bool)     │  │ + list_pins() -> dict│
│                  │  │ + get_owners(cid)    │  │                      │
│                  │  │   -> list            │  │                      │
│                  │  │ + is_owner(cid, tid) │  │                      │
│                  │  │   -> bool            │  │                      │
│                  │  │ + get_all_files()    │  │                      │
│                  │  │   -> list            │  │                      │
└──────────────────┘  └──────────────────────┘  └──────────────────────┘


┌──────────────────────────────┐    ┌───────────────────────────────┐
│    DistributedBlockchain     │    │        Block                  │
│──────────────────────────────│    │───────────────────────────────│
│ - node_id: str               │    │ - index: int                  │
│ - chain: List[Block]         │◆───│ - timestamp: str              │
│ - pending_transactions: list │    │ - transactions: list          │
│ - authorized_validators: list│    │ - previous_hash: str          │
│ - storage_file: Path         │    │ - validator: str              │
│──────────────────────────────│    │ - hash: str                   │
│ + add_transaction(txn): bool │    │───────────────────────────────│
│ + mine_pending_txns(): Block │    │ + calculate_hash() -> str     │
│ + validate_block(block): bool│    │ + to_dict() -> dict           │
│ + validate_chain(): bool     │    └───────────────────────────────┘
│ + resolve_conflicts(peer):   │
│   bool                       │
│ + get_all_transactions():    │
│   list                       │
│ + query_transactions(        │
│   tenant, action): list      │
│ + save_to_file()             │
│ + load_from_file()           │
│ + get_stats(): dict          │
└──────────────────────────────┘


┌──────────────────────────┐   ┌───────────────────────────────────┐
│    PQCKeyManager         │   │     HybridEncryption              │
│──────────────────────────│   │───────────────────────────────────│
│ - kyber: SimulatedKyber  │   │ - pqc_manager: PQCKeyManager     │
│ - storage_dir: Path      │◄──│───────────────────────────────────│
│ - tenant_keys: dict      │   │ + encrypt_file_hybrid(content,   │
│──────────────────────────│   │   tenant_id) -> (bytes, dict)    │
│ + generate_tenant_keys(  │   │ + share_file_quantum_safe(       │
│   tenant_id) -> (pk, sk) │   │   hash, sender, receiver)       │
│ + get_tenant_public_key( │   │   -> bytes                       │
│   tenant_id) -> bytes    │   └───────────────────────────────────┘
│ + establish_shared_key(  │
│   sender, receiver)      │   ┌───────────────────────────────────┐
│   -> (ct, shared_key)    │   │     SimulatedKyber                │
│ + derive_encryption_key( │   │───────────────────────────────────│
│   tenant_id, file_hash)  │   │ - security_level: int            │
│   -> bytes               │◆──│───────────────────────────────────│
└──────────────────────────┘   │ + keypair() -> (pk, sk)           │
                               │ + encapsulate(pk) -> (ct, ss)     │
                               │ + decapsulate(sk, ct) -> ss       │
                               └───────────────────────────────────┘


┌────────────────────────────────┐
│   AIDeduplicationEngine        │
│────────────────────────────────│
│ - encoder: BinaryFileEncoder   │
│ - cnn: SimpleCNN               │
│ - model_path: Path             │
│────────────────────────────────│
│ + check_similarity(file1,      │
│   file2, threshold) ->         │◆──┐
│   (bool, float)                │   │
│ + train_on_dataset(pairs,      │   │
│   epochs)                      │   │
│ + save_model(path)             │   │
│ + load_model(path)             │   │
└────────────────────────────────┘   │
                                     │
  ┌──────────────────────────────────┤
  │                                  │
  ▼                                  ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│  BinaryFileEncoder       │  │       SimpleCNN              │
│──────────────────────────│  │──────────────────────────────│
│ - chunk_size: int (256)  │  │ - input_size: int (2048)     │
│ - vector_size: int (2048)│  │ - embedding_size: int (128)  │
│──────────────────────────│  │ - weights_1: ndarray         │
│ + encode_file(content)   │  │ - bias_1: ndarray            │
│   -> ndarray (2048-dim)  │  │ - weights_2: ndarray         │
│ - _calculate_entropy(    │  │ - bias_2: ndarray            │
│   data) -> float         │  │ - is_trained: bool           │
│ - _skewness(data)        │  │──────────────────────────────│
│   -> float               │  │ + forward(x) -> ndarray      │
│ - _kurtosis(data)        │  │ + train(X, y, epochs)        │
│   -> float               │  │ + similarity(x1, x2) -> float│
└──────────────────────────┘  │ + save_model(path)           │
                              │ + load_model(path)           │
                              └──────────────────────────────┘
```
*Figure 6.2: UML Class Diagram of Cloud Seal System*

**Key Relationships:**
- **Composition (◆):** The `DistributedBlockchain` owns `Block` instances; `AIDeduplicationEngine` owns `BinaryFileEncoder` and `SimpleCNN`; `PQCKeyManager` owns `SimulatedKyber`.
- **Association (uses):** The FastAPI application references all major modules but does not own them in the strict OOP sense.
- **Dependency:** `HybridEncryption` depends on `PQCKeyManager` for key operations and delegates to `encryption.py` functions for AES operations.

---

### 6.4.2 Sequence Diagram: File Upload Flow

This sequence diagram shows the interaction between components during a file upload with both PQC and AI enabled.

```
 Data Owner       Frontend         FastAPI        Encryption     Bloom     Reference    AI Engine     Blockchain    IPFS
    │              (app.js)        (app.py)       Module         Filter    Counter                                Manager
    │                │                │              │              │          │            │              │          │
    │  Select File   │                │              │              │          │            │              │          │
    │  + Options     │                │              │              │          │            │              │          │
    │───────────────>│                │              │              │          │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │  POST /upload  │              │              │          │            │              │          │
    │                │  (file, tenant,│              │              │          │            │              │          │
    │                │   pqc=T, ai=T) │              │              │          │            │              │          │
    │                │───────────────>│              │              │          │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │ generate_    │              │          │            │              │          │
    │                │                │ content_hash │              │          │            │              │          │
    │                │                │─────────────>│              │          │            │              │          │
    │                │                │   SHA-256    │              │          │            │              │          │
    │                │                │<─────────────│              │          │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │              │              │          │  check_    │              │          │
    │                │                │              │              │          │ similarity │              │          │
    │                │                │─────────────────────────────────────────────────────>│              │          │
    │                │                │              │              │          │  (is_dup,  │              │          │
    │                │                │<─────────────────────────────────────────────────────│              │          │
    │                │                │              │              │          │   score)   │              │          │
    │                │                │              │  check(hash) │          │            │              │          │
    │                │                │──────────────────────────────>│         │            │              │          │
    │                │                │              │  True/False  │          │            │              │          │
    │                │                │<──────────────────────────────│         │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │              │              │add_      │            │              │          │
    │                │                │              │              │reference │            │              │          │
    │                │                │──────────────────────────────────────────>           │              │          │
    │                │                │              │              │ NEW/DUP  │            │              │          │
    │                │                │<──────────────────────────────────────────           │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │  [IF NEW]    │              │          │            │              │          │
    │                │                │  encrypt_    │              │          │            │              │          │
    │                │                │  file_hybrid │              │          │            │              │          │
    │                │                │─────────────>│              │          │            │              │          │
    │                │                │  (encrypted, │              │          │            │              │          │
    │                │                │   metadata)  │              │          │            │              │          │
    │                │                │<─────────────│              │          │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │              │              │          │            │              │ add_bytes│
    │                │                │──────────────────────────────────────────────────────────────────────────────>│
    │                │                │              │              │          │            │              │   CID   │
    │                │                │<──────────────────────────────────────────────────────────────────────────────│
    │                │                │              │              │          │            │              │          │
    │                │                │              │  add(hash)   │          │            │              │          │
    │                │                │──────────────────────────────>│         │            │              │          │
    │                │                │              │              │          │            │              │          │
    │                │                │              │              │          │            │  add_txn     │          │
    │                │                │──────────────────────────────────────────────────────────────────>│          │
    │                │                │              │              │          │            │  mine_block  │          │
    │                │                │──────────────────────────────────────────────────────────────────>│          │
    │                │                │              │              │          │            │              │          │
    │                │  JSON Response │              │              │          │            │              │          │
    │                │  {status,cid,  │              │              │          │            │              │          │
    │                │   encryption,  │              │              │          │            │              │          │
    │                │   ai_details}  │              │              │          │            │              │          │
    │                │<───────────────│              │              │          │            │              │          │
    │                │                │              │              │          │            │              │          │
    │  Display       │                │              │              │          │            │              │          │
    │  Results       │                │              │              │          │            │              │          │
    │<───────────────│                │              │              │          │            │              │          │
```
*Figure 6.3: Sequence Diagram – File Upload with PQC and AI Enabled*

---

### 6.4.3 Sequence Diagram: File Deletion Flow

This sequence diagram demonstrates the safe deletion process with reference counting.

```
 Data Owner       Frontend         FastAPI        Reference       Blockchain      IPFS
    │              (app.js)        (app.py)       Counter                        Manager
    │                │                │              │                │             │
    │  Click Delete  │                │              │                │             │
    │───────────────>│                │              │                │             │
    │                │                │              │                │             │
    │                │  DELETE        │              │                │             │
    │                │  /delete/{cid} │              │                │             │
    │                │───────────────>│              │                │             │
    │                │                │              │                │             │
    │                │                │ remove_      │                │             │
    │                │                │ reference    │                │             │
    │                │                │─────────────>│                │             │
    │                │                │              │                │             │
    │                │                │ (count,      │                │             │
    │                │                │  should_del) │                │             │
    │                │                │<─────────────│                │             │
    │                │                │              │                │             │
    │                │                │  [IF count   │                │             │
    │                │                │   == 0]      │                │             │
    │                │                │              │                │  unpin_file │
    │                │                │──────────────────────────────────────────────>
    │                │                │              │                │  (removes   │
    │                │                │              │                │   physical  │
    │                │                │              │                │   file)     │
    │                │                │              │                │             │
    │                │                │  add_txn     │                │             │
    │                │                │  (DELETE)    │                │             │
    │                │                │──────────────────────────────>│             │
    │                │                │  mine_block  │                │             │
    │                │                │──────────────────────────────>│             │
    │                │                │              │                │             │
    │                │  JSON Response │              │                │             │
    │                │  {remaining:n} │              │                │             │
    │                │<───────────────│              │                │             │
    │                │                │              │                │             │
    │  Updated UI    │                │              │                │             │
    │<───────────────│                │              │                │             │
```
*Figure 6.4: Sequence Diagram – File Deletion with Reference Counting*

---

### 6.4.4 Activity Diagram: Upload Pipeline

This activity diagram shows the decision logic in the upload pipeline, covering both the AI and traditional deduplication paths.

```
                    ┌───────────┐
                    │   START   │
                    └─────┬─────┘
                          │
                          ▼
                ┌─────────────────┐
                │  Receive File + │
                │  Tenant ID      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Generate SHA-  │
                │  256 Content    │
                │  Hash (CID)     │
                └────────┬────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  AI Enabled?  │
                 └───┬───────┬───┘
                YES  │       │  NO
                     ▼       │
          ┌──────────────┐   │
          │  Check CNN   │   │
          │  Similarity  │   │
          │  Against     │   │
          │  Existing    │   │
          │  Files       │   │
          └──────┬───────┘   │
                 │           │
                 ▼           │
          ┌──────────────┐   │
          │  Record AI   │   │
          │  Similarity  │   │
          │  Score       │   │
          └──────┬───────┘   │
                 │           │
                 ◄───────────┘
                 │
                 ▼
        ┌────────────────┐
        │  Bloom Filter  │
        │  Check (hash)  │
        └───────┬────────┘
                │
                ▼
       ┌────────────────┐
       │  Add Reference │
       │  (tenant_id,   │
       │   CID)         │
       └───┬────────┬───┘
      NEW  │        │ DUPLICATE
           │        │
           ▼        ▼
  ┌─────────────┐  ┌──────────────────┐
  │ PQC         │  │  Log DUPLICATE   │
  │ Enabled?    │  │  to Blockchain   │
  └──┬──────┬───┘  └───────┬──────────┘
  YES│      │NO            │
     ▼      ▼              │
┌────────┐ ┌────────┐      │
│Hybrid  │ │AES-256 │      │
│Encrypt │ │Encrypt │      │
│(Kyber+ │ │(Conv.  │      │
│AES)    │ │Key)    │      │
└───┬────┘ └───┬────┘      │
    │          │            │
    ◄──────────┘            │
    │                       │
    ▼                       │
┌─────────────┐             │
│  Store in   │             │
│  IPFS       │             │
│  (Pin File) │             │
└──────┬──────┘             │
       │                    │
       ▼                    │
┌─────────────┐             │
│  Add to     │             │
│  Bloom      │             │
│  Filter     │             │
└──────┬──────┘             │
       │                    │
       ▼                    │
┌─────────────┐             │
│  Log NEW    │             │
│  UPLOAD to  │             │
│  Blockchain │             │
└──────┬──────┘             │
       │                    │
       ◄────────────────────┘
       │
       ▼
┌─────────────┐
│  Return     │
│  Response   │
│  to Client  │
└──────┬──────┘
       │
       ▼
  ┌─────────┐
  │   END   │
  └─────────┘
```
*Figure 6.5: Activity Diagram – Upload Pipeline Decision Logic*

---

## 6.5 Algorithm Design

### 6.5.1 Deduplication Pipeline Algorithm

The following pseudocode describes the core deduplication pipeline, integrating all security and AI components:

```
ALGORITHM: SecureFileUpload
INPUT: file_content (bytes), tenant_id (string), use_pqc (boolean), use_ai (boolean)
OUTPUT: upload_result (dictionary)

BEGIN
    // Step 1: Generate Content Identifier
    content_hash ← SHA-256(file_content)
    
    // Step 2: AI-Enhanced Similarity Check (Optional)
    ai_result ← NULL
    IF use_ai AND cnn_model.is_trained THEN
        FOR EACH existing_file IN reference_counter.get_all_files() DO
            existing_content ← IPFS.get(existing_file.cid)
            IF existing_content ≠ NULL THEN
                (is_similar, score) ← AI_Engine.check_similarity(file_content, existing_content)
                IF is_similar THEN
                    ai_result ← {detected: TRUE, score: score, matched_cid: existing_file.cid}
                    BREAK
                END IF
            END IF
        END FOR
    END IF
    
    // Step 3: Bloom Filter Fast Check
    maybe_duplicate ← BloomFilter.check(content_hash)
    
    // Step 4: Reference Counting
    status ← ReferenceCounter.add_reference(content_hash, tenant_id, filename)
    
    // Step 5: Handle Based on Deduplication Result
    IF status = "NEW" THEN
        // Step 5a: Encrypt File
        IF use_pqc THEN
            encryption_key ← PQC_Manager.derive_encryption_key(tenant_id, content_hash)
            encrypted_file ← AES-256-CBC.encrypt(file_content, encryption_key)
            method ← "AES-256 + Kyber-768"
        ELSE
            convergent_key ← SHA-256(tenant_id + tenant_secret + file_content)
            encrypted_file ← AES-256-CBC.encrypt(file_content, convergent_key)
            method ← "AES-256 (Classical)"
        END IF
        
        // Step 5b: Store Encrypted File
        cid ← IPFS.add_bytes(encrypted_file)
        IPFS.pin_file(cid)
        
        // Step 5c: Update Bloom Filter
        BloomFilter.add(content_hash)
        
        // Step 5d: Log to Blockchain
        Blockchain.add_transaction({action: "UPLOAD_NEW", tenant: tenant_id, cid: content_hash})
        Blockchain.mine_pending_transactions()
        
        RETURN {status: "stored", cid: content_hash, deduplicated: FALSE, encryption: method}
    ELSE
        // Step 6: Duplicate Detected - Link Only
        Blockchain.add_transaction({action: "UPLOAD_DUPLICATE", tenant: tenant_id, cid: content_hash})
        Blockchain.mine_pending_transactions()
        
        RETURN {status: "linked", cid: content_hash, deduplicated: TRUE, ai_details: ai_result}
    END IF
END
```
*Algorithm 6.1: Secure File Upload with Multi-Layer Deduplication*

---

### 6.5.2 CNN Architecture for Encrypted Similarity Detection

The AI component uses a **Siamese Neural Network** architecture to detect similar files even when encrypted. The architecture is designed to learn structural patterns in encrypted binary data without requiring decryption.

```
                        INPUT FILES
                    ┌──────┐  ┌──────┐
                    │File A│  │File B│
                    │(Enc.)│  │(Enc.)│
                    └──┬───┘  └──┬───┘
                       │         │
                       ▼         ▼
              ┌────────────────────────────┐
              │   Binary File Encoder      │
              │                            │
              │   For each 256-byte chunk: │
              │   • Byte frequency (256-d) │
              │   • Shannon entropy        │
              │   • Mean, Std, Skewness    │
              │   • Kurtosis               │
              │   • Byte transitions       │
              │                            │
              │   Output: 2048-dim vector  │
              └──────┬──────────────┬──────┘
                     │              │
              Vector A         Vector B
              (2048-d)         (2048-d)
                     │              │
                     ▼              ▼
    ┌────────────────────────────────────────────┐
    │         SHARED WEIGHTS (Siamese)           │
    │                                            │
    │   ┌──────────────────────────────────┐     │
    │   │  Layer 1: Dense (2048 → 512)     │     │
    │   │  Activation: ReLU                │     │
    │   └────────────┬─────────────────────┘     │
    │                │                           │
    │   ┌────────────┴─────────────────────┐     │
    │   │  Layer 2: Dense (512 → 128)      │     │
    │   │  Activation: ReLU                │     │
    │   └────────────┬─────────────────────┘     │
    │                │                           │
    │         Embedding (128-d)                  │
    └────────┬───────────────────────┬───────────┘
             │                       │
      Embedding A              Embedding B
      (128-dim)                (128-dim)
             │                       │
             └──────────┬────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Cosine          │
              │ Similarity      │
              │                 │
              │      A · B      │
              │ s = ───────     │
              │     |A| |B|    │
              │                 │
              │ Output: [0, 1]  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Threshold      │
              │  (default 0.85) │
              │                 │
              │  s ≥ 0.85 →     │
              │    DUPLICATE    │
              │                 │
              │  s < 0.85 →     │
              │    UNIQUE       │
              └─────────────────┘
```
*Figure 6.6: Siamese CNN Architecture for Encrypted Similarity Detection*

**Training Process:**

The network is trained using **contrastive learning** on pairs of files:

```
ALGORITHM: ContrastiveLearning
INPUT: file_pairs [(file_A, file_B, is_duplicate)], epochs, learning_rate = 0.01
OUTPUT: trained model weights

BEGIN
    FOR epoch = 1 TO epochs DO
        total_loss ← 0
        FOR EACH (file_A, file_B, is_duplicate) IN file_pairs DO
            // Forward pass through shared encoder
            embedding_A ← CNN.forward(Encoder.encode(file_A))
            embedding_B ← CNN.forward(Encoder.encode(file_B))
            
            // Calculate cosine similarity
            similarity ← cosine_similarity(embedding_A, embedding_B)
            
            // Contrastive loss
            IF is_duplicate THEN
                loss ← (1 - similarity)²    // Minimise distance for duplicates
            ELSE
                loss ← max(0, similarity - 0.3)²  // Maximise distance for non-duplicates
            END IF
            
            // Gradient update (simplified)
            gradient ← ∂loss / ∂weights
            weights ← weights - learning_rate × gradient
            total_loss ← total_loss + loss
        END FOR
        
        avg_loss ← total_loss / |file_pairs|
        PRINT "Epoch", epoch, "Loss:", avg_loss
    END FOR
END
```
*Algorithm 6.2: Contrastive Learning Training for Siamese CNN*

---

### 6.5.3 Bloom Filter Algorithm

```
ALGORITHM: BloomFilterOperations
INPUT: expected_items (n), false_positive_rate (p)

INITIALISE:
    // Calculate optimal bit array size
    m ← ⌈-(n × ln(p)) / (ln(2))²⌉
    
    // Calculate optimal hash function count
    k ← ⌈(m / n) × ln(2)⌉
    
    // Create bit array of size m, initialised to 0
    bit_array[0..m-1] ← 0

PROCEDURE ADD(item):
    FOR i = 0 TO k-1 DO
        position ← MurmurHash3(item, seed=i) MOD m
        bit_array[position] ← 1
    END FOR

PROCEDURE CHECK(item) → boolean:
    FOR i = 0 TO k-1 DO
        position ← MurmurHash3(item, seed=i) MOD m
        IF bit_array[position] = 0 THEN
            RETURN FALSE    // Definitely not present
        END IF
    END FOR
    RETURN TRUE    // Probably present (verify with hash comparison)
END
```
*Algorithm 6.3: Bloom Filter for O(1) Duplicate Detection*

---

## 6.6 UI Design

### 6.6.1 Low-Fidelity Wireframes

The following wireframes represent the initial design concepts for the Cloud Seal dashboard interface, designed prior to implementation.

**Wireframe 1: Main Dashboard**

```
┌──────────────────────────────────────────────────────────────┐
│  🔐 Cloud Seal Enhanced                                      │
│  Privacy-Preserving Multi-Tenant Deduplication               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📊 Live System Status                    [LIVE]     │   │
│  │                                                      │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │📦 Blocks │ │📂 Total  │ │💎 Unique │ │♻️ Dedup│ │   │
│  │  │          │ │ Files    │ │ Files    │ │ Ratio  │ │   │
│  │  │   12     │ │   8      │ │   5      │ │ 37.5%  │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │   │
│  │                                                      │   │
│  │  [🔄 Refresh Dashboard]                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📤 Secure Upload                                    │   │
│  │                                                      │   │
│  │  Upload files securely with quantum-resistant         │   │
│  │  encryption and AI-powered duplicate detection.       │   │
│  │                                                      │   │
│  │  Current Tenant ▼        Receiver Tenant ▼           │   │
│  │  [Tenant A     ]        [Tenant B       ]           │   │
│  │                                                      │   │
│  │  Advanced Security Options                           │   │
│  │  ┌────────────────────────────────────────────────┐ │   │
│  │  │ ☑ 🔒 Post-Quantum Encryption                  │ │   │
│  │  │   Protects against future quantum attacks      │ │   │
│  │  │                                                │ │   │
│  │  │ ☑ 🤖 AI-Powered Similarity Detection          │ │   │
│  │  │   Finds near-duplicate files using CNN         │ │   │
│  │  └────────────────────────────────────────────────┘ │   │
│  │                                                      │   │
│  │  [Choose File]                                       │   │
│  │  [🚀 Upload File]                                   │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────┐        │   │
│  │  │  Upload Result:                         │        │   │
│  │  │  Status: ✅ NEW FILE                    │        │   │
│  │  │  CID: QmXyZ123abc...                    │        │   │
│  │  │  Encryption: AES-256 + Kyber-768        │        │   │
│  │  └─────────────────────────────────────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📄 My Files (Personal Vault)                        │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 📄 report.pdf    QmXyZ... Refs:2  [🗑️ Delete]│  │   │
│  │  │ 📄 data.csv      QmAbc... Refs:1  [🗑️ Delete]│  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  📚 All Files (System-wide)                          │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 📄 report.pdf  QmXyZ... Owners: A,B  Refs:2  │  │   │
│  │  │ 📄 data.csv    QmAbc... Owners: A    Refs:1  │  │   │
│  │  │ 📄 image.png   QmDef... Owners: B,C  Refs:2  │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│  Cloud Seal Enhanced – Built with AI + Blockchain + PQC     │
└──────────────────────────────────────────────────────────────┘
```
*Figure 6.7: Low-Fidelity Wireframe – Main Dashboard*

### 6.6.2 Design Considerations for Usability and Accessibility

The UI design incorporates several considerations to improve usability and accessibility:

**Usability:**

| Consideration | Implementation |
|---------------|----------------|
| **Progressive Disclosure** | Advanced security options are grouped under a collapsible heading, reducing cognitive load for basic uploads. |
| **Real-Time Feedback** | The dashboard auto-refreshes every 10 seconds. The "Refresh Dashboard" button shows "⏳ Refreshing..." during manual refresh to indicate activity. |
| **Error Prevention** | Empty file uploads are rejected with clear error messages. Tenant selection defaults to "Tenant A" to prevent null submissions. |
| **Plain Language** | Security options use descriptive subtitles (e.g., "Protects your files against future quantum computer attacks") instead of technical jargon. |
| **Visual Status Indicators** | Upload results use emoji-enhanced status messages (✅ NEW, 🔗 DEDUPLICATED) for instant comprehension. |
| **Consistent Layout** | All sections follow the same card-based layout pattern with consistent heading styles, creating a predictable navigation experience. |

**Accessibility:**

| Consideration | Implementation |
|---------------|----------------|
| **Colour Contrast** | The light-mode design uses a primary blue (#0066cc) on white backgrounds, exceeding WCAG 2.1 AA contrast requirements (7.04:1 ratio). |
| **Semantic HTML** | The interface uses `<header>`, `<main>`, `<section>`, `<footer>`, `<label>`, and `<select>` elements for screen reader compatibility. |
| **Font Sizing** | Base font size of 16px with relative sizing (`rem` units) allows browser-level font scaling without layout breakage. |
| **Form Labels** | All form inputs have associated `<label>` elements, ensuring screen readers can identify input purposes. |
| **Keyboard Navigation** | All interactive elements (buttons, checkboxes, dropdowns, file inputs) are natively keyboard-accessible via standard HTML elements. |
| **Responsive Design** | CSS Grid with `grid-template-columns: 1fr 1fr` adapts to different screen widths, maintaining usability on tablets and smaller displays. |

---

## 6.7 Chapter Summary

This chapter presented the complete design of the Cloud Seal system, translating requirements into a concrete software architecture.

The **three-tier layered architecture** (Presentation → Application → Data) provides clear separation of concerns, enabling independent development and testing of each tier. The Application Tier's modular design, with six specialised Python modules, allows each security component to be developed, tested, and upgraded independently.

The **detailed design** using OOADM included:
- A **class diagram** (Figure 6.2) showing 11 classes with their attributes, methods, and relationships (composition, association, dependency).
- **Sequence diagrams** (Figures 6.3–6.4) illustrating the upload and deletion workflows across all system components.
- An **activity diagram** (Figure 6.5) mapping the decision logic in the upload pipeline.

The **algorithm design** (Section 6.5) formalised three core algorithms:
1. The secure upload pipeline (Algorithm 6.1) integrating encryption, Bloom filter, reference counting, AI detection, and blockchain logging.
2. The Siamese CNN contrastive learning process (Algorithm 6.2) for encrypted similarity detection.
3. The Bloom filter operations (Algorithm 6.3) providing O(1) probabilistic duplicate detection.

The **UI design** (Section 6.6) prioritised usability through progressive disclosure, real-time feedback, and plain language, while meeting accessibility standards through semantic HTML, adequate colour contrast, and keyboard navigability.

These design artefacts collectively ensure that the implementation phase has clear, traceable specifications to follow, and that the resulting system meets the quality attributes defined in the design goals.
