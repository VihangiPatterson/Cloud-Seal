# Evaluation Document of Cloud Seal

**A Privacy-Preserving Multi-Tenant Cloud Deduplication Framework with AI, Blockchain, and Post-Quantum Cryptography**

**Name:** Vihangi Patterson | **Student ID:** W1953064 / 20220011 | **Supervisor:** Mr. Pubudu De Silva
**Degree:** BSc (Hons) Computer Science — IIT, in collaboration with the University of Westminster

---

## The Problem

Cloud deduplication saves 60–70% of storage by detecting and eliminating duplicate files (AWS, 2024; Microsoft, 2024). However, when files are encrypted for privacy — as required by regulations like HIPAA and GDPR — two identical files produce entirely different ciphertext, making deduplication impossible. This is the **deduplication-encryption paradox**. Existing solutions like DupLESS (Bellare et al., 2013) partially address this but introduce a single-point-of-failure key server, cannot detect near-duplicate files, and use classical cryptography vulnerable to future quantum computers. No existing system simultaneously solves all three problems: **secure encrypted deduplication**, **near-duplicate awareness**, and **quantum resistance**.

## Cloud Seal's Solution

Cloud Seal introduces a **six-component architecture** where each component addresses a specific gap. The novelty is their integration into a unified pipeline — no existing system combines all six.

*[Insert System Architecture Diagram here]*

| # | Component | What It Does | Key Innovation |
|---|-----------|-------------|----------------|
| 1 | **Convergent Encryption + Tenant Salting** | Same file → same ciphertext (enables dedup), but per-tenant secrets prevent cross-tenant data leakage | Blocks confirmation attacks without a key server (unlike DupLESS) |
| 2 | **Siamese CNN (AI)** | Detects near-duplicate files by comparing 2048-dim statistical fingerprints of encrypted data; **advisory only** — never auto-deduplicates | First approach to provide near-duplicate awareness on ciphertext without decryption (cf. SimEnc, 2025) |
| 3 | **Bloom Filter** | O(1) probabilistic duplicate lookup in <0.001ms | 11.98 bytes/file — 2.7× more efficient than hash tables |
| 4 | **IPFS Storage** | Content-addressed storage where CID = hash(content); deduplication is built into the storage protocol | No existing dedup framework uses IPFS as backend (Benet, 2014) |
| 5 | **Blockchain Audit Trail** | Every file operation recorded in a PoA hash chain — tamper-proof and immutable | Novel application of blockchain to deduplication audit logging |
| 6 | **Post-Quantum Encryption (Kyber-768 + AES-256)** | Hybrid encryption resistant to quantum attacks | Distinct from SALIGP (Periasamy et al., 2025) and QBDD (Wang et al., 2024) approaches |

**Key design decision:** The AI component operates in **advisory mode** — it flags near-duplicates (e.g., "this file is 92% similar to an existing file") but never auto-deduplicates. Only SHA-256 exact hash matches trigger actual deduplication. This protects data integrity.

---

## Test Results

**Environment:** MacBook Pro M2, 8-core CPU, 16GB RAM | Python 3.11, Docker, FastAPI
**Test suite:** 7 automated scripts producing JSON results — reproducible via `python3 tests/run_all_tests.py`

### Security & Integrity

| Test | Result |
|------|--------|
| Blockchain hash chain validation | ✅ 100% integrity |
| Tamper detection (modified transactions) | ✅ Detected instantly |
| Cross-tenant data isolation (20 tenants) | ✅ Zero leakage |
| Confirmation attack prevention | ✅ Blocked (tenant-salted keys) |
| Key derivation strength | ✅ 46.5% avalanche effect |
| Bloom filter false positive rate | <1.2% across 10K items |

### Performance

| File Size | Upload Pipeline (Total) | Encrypt | Decrypt | Meets NFR (<5s) |
|-----------|------------------------|---------|---------|-----------------|
| 1 KB | 0.11 ms | 0.02 ms | 0.01 ms | ✅ |
| 100 KB | 0.22 ms | 0.10 ms | 0.03 ms | ✅ |
| 1 MB | 1.95 ms | 1.09 ms | 0.26 ms | ✅ |
| 10 MB | — | 10.56 ms | 2.95 ms | ✅ |

### AI Model Evaluation (Siamese CNN)

| Parameter | Value |
|-----------|-------|
| Architecture | 2-layer Siamese CNN (2048→512→128), contrastive loss |
| Training | 44 pairs, 50 epochs, lr=0.01, margin=0.4 |
| **AUC** | **0.797** (vs. 0.500 random baseline) |

| File Category | Score Range | Correct? |
|--------------|-------------|----------|
| Exact duplicates | 0.998 – 1.000 | ✅ |
| Completely different files | 0.073 – 0.319 | ✅ |
| Near-duplicates (small edits) | 0.870 – 1.000 | ✅ (advisory) |

SHA-256 alone achieves only 50% recall (misses all near-duplicates). The CNN achieves **100% recall** with clear score separation. The 0.85 threshold is configurable per deployment.

---

## Limitations & Future Work

| Limitation | Status | Future Enhancement |
|-----------|--------|-------------------|
| AI trained on 44 synthetic pairs | AUC 0.797 achieved | Train on 10,000+ real file pairs |
| IPFS simulated locally | CID-based API identical to production | Connect to live IPFS network |
| Kyber-768 simulated | Workflow demonstrated | Use `liboqs-python` for NIST-certified PQC |
| Tested up to 10MB, single machine | All NFRs passed | Benchmark at 100K+ files, concurrent users |
| No formal security proof | 5 threat categories, 21 tests pass | Game-based/simulation-based formal proof |

---

## References

1. Amazon Web Services (2024). *Amazon S3 Storage Classes and Data Management*. AWS Documentation.
2. Bellare, M., Keelveedhi, S., & Ristenpart, T. (2013). DupLESS: Server-Aided Encryption for Deduplicated Storage. *USENIX Security Symposium*, 179–194.
3. Benet, J. (2014). IPFS - Content Addressed, Versioned, P2P File System. *arXiv:1407.3561*.
4. Bloom, B.H. (1970). Space/time trade-offs in hash coding with allowable errors. *Communications of the ACM*, 13(7), 422–426.
5. Bromley, J., Guyon, I., LeCun, Y., et al. (1993). Signature Verification using a Siamese Time Delay Neural Network. *NeurIPS*, 6.
6. Douceur, J.R., et al. (2002). Reclaiming Space from Duplicate Files in a Serverless Distributed File System. *ICDCS*.
7. Kumar, A., & Singh, P. (2023). Convergent encryption challenges in multi-tenant cloud deduplication systems. *ACM Computing Surveys*, 56(2), 1–29.
8. Microsoft (2024). *Azure Blob Storage redundancy and data management*. Azure Documentation.
9. Periasamy, J.K. et al. (2025). Enhancing cloud security and deduplication efficiency with SALIGP. *Scientific Reports*, 15, 1847.
10. Wang, H., Li, Q., & Zhang, R. (2024). QBDD: Quantum-resistant blockchain-assisted deep data deduplication. *Computer Networks*, 245, 110382.
11. Zhang, L., et al. (2025). SimEnc: Similarity-preserving encryption for encrypted container images. *ACM Transactions on Storage*, 21(1), 1–28.
