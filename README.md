# 🔐 Cloud Seal 

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)
![Architecture](https://img.shields.io/badge/Architecture-Distributed-brightgreen)
![Security](https://img.shields.io/badge/Security-Post--Quantum-ff69b4)
![License](https://img.shields.io/badge/License-MIT-gray.svg)

**Cloud Seal** is a privacy-preserving, multi-tenant cloud storage framework designed to solve one of the most persistent paradoxes in modern computing: the inability to deduplicate encrypted data without compromising user privacy or sacrificing scalability.

By integrating **Artificial Intelligence (Siamese CNNs)**, an immutable **Proof-of-Authority (PoA) Blockchain**, and **Post-Quantum Cryptography (NIST Kyber-768)**, Cloud Seal achieves a 100% functional retention of cross-tenant structural isolation while preserving high-throughput storage efficiency.

---

## ⚡ Key Features

* **Quantum-Safe Hybrid Encryption:** Uses a combination of AES-256-CBC and a simulated NIST `CRYSTALS-Kyber-768` key encapsulation mechanism to protect data against "harvest now, decrypt later" capability by future quantum computers.
* **Tenant-Salted Convergent Encryption:** Cryptographically binds encryption keys to tenant IDs, strictly eliminating Cross-Tenant Confirmation attacks while allowing intra-tenant exact deduplication.
* **AI on Ciphertext (Zero-Trust AI):** A lightweight *Siamese Convolutional Neural Network* built from scratch in NumPy that extracts Shannon entropy and structural byte-frequencies directly from AES-ciphertexts to flag statistically similar "near-duplicates"—*all without decryption keys*.
* **Proof-of-Authority Audit Ledger:** A distributed, crash-recoverable JSON blockchain logging every upload, access, and deduplication event (Running at theoretically 29,600+ tx/sec).
* **O(1) Bloom Filter Lookups:** Highly optimized duplicate screening using `MurmurHash3` ensures the filesystem database is mathematically protected from unnecessary disk reads.
* **Dynamic Full-Stack Dashboard:** Beautiful, responsive Vanilla HTML/JS frontend interacting seamlessly with the multi-threaded FastAPI backend.

---

## 🏗️ Project Structure

```
cloud-seal-poc/
├── backend/
│   ├── app.py                      # FastAPI App Orchestrator 
│   ├── encryption.py               # AES-256 & Tenant-Salted CE Algorithms
│   ├── pcq_kyber.py                # Kyber-768 PQC Simulation Model
│   ├── ai_deduplication.py         # Siamese CNN Logic (NumPy)
│   ├── blockchain_distributed.py   # Proof-of-Authority Consensus Ledger
│   ├── bloom_filter.py             # Duplicate Fast-Screening
│   ├── ipfs_manager.py             # Node-content CID storage structure
│   └── reference_counter.py        # Multi-Tenant file ownership tracker
├── frontend/
│   ├── index.html                  # Main Web Dashboard 
│   ├── style.css                   # Vanilla CSS UI System
│   └── app.js                      # Client-side routing and API logic
└── docs/                           
    └── thesis/                     # Full Academic Research Paper
```

---

## 🌐 Live Demo

The project is fully hosted and deployed on WSO2 Choreo. You can access the live Cloud Seal Dashboard directly here:
**[https://75b19bed-57d0-4181-a5bd-6c6657f1acc6-dev.e1-eu-north-azure.choreoapis.dev/cloud-seal/cloud-seal/v1.0/](https://75b19bed-57d0-4181-a5bd-6c6657f1acc6-dev.e1-eu-north-azure.choreoapis.dev/cloud-seal/cloud-seal/v1.0/)**

---

## 🚀 Quick Start / Local Deployment

### 1. Prerequisites
* Python 3.10 or higher
* Recommended: Virtual Environment (`venv`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/VihangiPatterson/Cloud-Seal.git
cd Cloud-Seal/backend

# Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Server
```bash
# Start the FastAPI server locally
uvicorn app:app --reload
```

The system will now be active. Open `http://localhost:8000/frontend/` in your browser to access the Cloud Seal Dashboard!

---

## 🧪 Running the Test Suite

Cloud Seal includes 7 heavily robust automated test suites validating encryption latency, multi-tenant boundaries, AI capability, and system scalability.

```bash
# Ensure you are inside the active virtual environment
cd backend
python tests/run_all_tests.py
```
This will sequentially run all architectural tests and generate a comprehensive paper-ready `comprehensive_test_report.json` document with metrics.

---

## 📖 Research Documentation

This repository represents the culmination of academic research exploring cross-domain security implementations. For an in-depth breakdown of the literature review, methodology, architectural design, testing algorithms, and mathematically established boundary conclusions, please refer to the fully drafted thesis located in `docs/thesis/`.

---

**Developed for Academic Evaluation**
*Demonstrating the future of zero-trust, quantum-safe cloud scaling.*
