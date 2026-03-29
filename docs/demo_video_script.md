# Cloud Seal: Demonstration Video Script & Guide

This is the exact step-by-step script and pacing guide to record your final demonstration video based on your presentation slides and local codebase. 

---

## 🛑 Getting Ready Before You Record
1. Start your backend server in your terminal: `uvicorn app:app --reload`
2. Have your PowerPoint Slides open on your screen.
3. Have your frontend dashboard open in your browser (`http://localhost:8000/frontend/`).
4. Have your code editor (like VS Code) open with `encryption.py` and `ai_deduplication.py` ready to show.

---

## 🎬 Part 1: Problem & Research Gap (1-2 Minutes)
*Visual: Start by presenting your first few introductory slides.*

**🗣️ Speaking Script:**
> "Hello, my name is Vihangi, and today I will be demonstrating my thesis project: **Cloud Seal**. 
> 
> **The Problem:** Today, cloud providers and enterprises are trapped in a paradox regarding data privacy and storage efficiency. If users encrypt their data locally before uploading it to protect their privacy, the cloud server receives unreadable ciphertext. Because the server cannot read the data, it cannot detect when identical files are uploaded, preventing data deduplication and wasting massive amounts of expensive storage space.
>
> **The Research Gap:** Existing systems attempt to solve this via 'Convergent Encryption', but they fall victim to severe security flaws like Cross-Tenant Confirmation attacks, and they are completely vulnerable to future quantum computing. Furthermore, there is no existing architecture that successfully integrates Post-Quantum Cryptography, AI similarity detection, and Blockchain auditing into a single framework. Cloud Seal is designed to fill this exact gap."

---

## 🎬 Part 2: Solution & Technical Design (2 Minutes)
*Visual: Switch to your Architecture / Components Slide.*

**🗣️ Speaking Script:**
> "To solve this, I designed a three-tier architecture that operates strictly under Zero-Trust principles. Our framework relies on three core technologies:
> 1. A custom **Siamese Convolutional Neural Network** built entirely from scratch in NumPy. It identifies file similarity by extracting statistical byte-distributions directly from encrypted data without ever decrypting it.
> 2. A **Proof-of-Authority Blockchain** that creates an immutable, tamper-proof audit log of every upload and deduplication event.
> 3. **Post-Quantum Cryptography** utilizing NIST's CRYSTALS-Kyber-768 standard to secure file sharing against 'harvest now, decrypt later' quantum attacks."

*Visual: Switch to your Code Editor (VS Code).*

**🗣️ Speaking Script:**
> "Here is a brief walkthrough of the codebase. 
> - In `encryption.py`, you can see the **Tenant-Salted Convergent Key algorithm**. By mixing a tenant-specific salt with the file's bytes, we ensure that every user generates a unique key, structurally eliminating cross-tenant leakage.
> - Over in `ai_deduplication.py`, you can see our feature extraction matrix. Instead of looking at plaintext words, the system extracts Shannon entropy and statistical moments from raw encrypted bytes to feed into the Siamese neural network.
> - And in `blockchain_distributed.py`, every transaction is cryptographically chained to the previous block's SHA-256 hash to ensure absolute immutability."

---

## 🎬 Part 3: System Demonstration (3-4 Minutes)
*Visual: Open the Web Dashboard (`index.html`).*

**🗣️ Speaking Script:**
> "Now, let's look at the live system."

### ✅ Positive Test Case 1: Standard Secured Upload
*Visual: Type `User_A` into the Session ID box. Select a file (e.g., a PDF or image). Ensure Post-Quantum and AI boxes are checked. Click Upload.*

**🗣️ Speaking Script:**
> "First, I am logging in as **User A**. I will upload a new file to the secure bucket. The system processes the upload, and as you can see on the dashboard, it is recognized as a **NEW FILE**. The global storage metrics have updated. Behind the scenes, the file was routed through Kyber-768 hybrid encryption, logged to the blockchain, and stored in our IPFS-simulated vault. The absolute pipeline latency is exceptionally fast—around 5 milliseconds."

### ✅ Positive Test Case 2: Multi-Tenant Encrypted Deduplication
*Visual: Change the Session ID to `User_B`. Select the EXACT SAME file. Click Upload.*

**🗣️ Speaking Script:**
> "Now, let's simulate a different tenant. I will switch my session context to **User B**. I am now uploading the exact same file. Notice what happens: The system instantly flags this as **DEDUPLICATED**.
> 
> Because of our Convergent Encryption and Bloom Filter gate, the server recognized the duplicate and securely linked User B to the existing storage block without uploading the payload again. Storage is saved, yet User B has absolutely no way to access User A's private encryption keys."

### ❌ Negative Test Case: Security & Tampering Defense
*Visual: Open your terminal. Stop the server, and run `python tests/run_all_tests.py`.*

**🗣️ Speaking Script:**
> "Finally, let's look at how the system handles negative testing and adversarial threats. I will execute the master automated test suite.
>
> Watch the **Blockchain Integrity test**. The system automatically simulates an attacker attempting to modify a single byte deep inside an old transaction log to rewrite history. Because of the Proof-of-Authority hash chain, the system instantly detects the mismatch, rejects the chain, and alerts administrators. 
> 
> Furthermore, the **Security Threat models** execute confirmation attacks against the deduplication layer to verify cross-tenant boundaries. As you can see, the test results show **0% Data Leakage**, passing all 21 threat vectors flawlessly."

## 🎬 Wrap-up (30 seconds)
*Visual: Switch back to your final Summary PowerPoint slide.*

**🗣️ Speaking Script:**
> "In conclusion, the system successfully scored a 100% pass rate across functional benchmarks while maintaining cryptographic integrity. Cloud Seal proves that enterprises no longer have to choose between strict data privacy and efficient storage utilization—they can have both, securely wrapped in a quantum-resistant architecture. Thank you for your time."
