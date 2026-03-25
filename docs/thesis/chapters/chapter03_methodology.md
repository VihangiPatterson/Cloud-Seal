# CHAPTER 03: METHODOLOGY

## 3.1 Chapter Overview

This chapter describes the research and development methodology employed in the Cloud Seal project. It explains how decisions were made regarding research philosophy, approach, strategy, data collection, and evaluation. The chapter is structured around the Saunders Research Onion framework, followed by the development methodology (including requirements elicitation, design, programming paradigm, dataset and AI pipeline, testing, and the step-by-step solution approach). Project management—covering schedule, resources, risk mitigation, and deliverables—concludes the chapter.

## 3.2 Research Methodology

### 3.2.1 Saunders' Research Onion

The research methodology follows the Research Onion framework (Saunders, Lewis & Thornhill, 2019), which provides a systematic structure for selecting appropriate methods at each layer.

| Layer | Choice | Justification |
|---|---|---|
| **Philosophy** | Pragmatism | Cloud Seal requires both quantitative evaluation (encryption latency, Bloom filter FP rates, AI recall/precision, blockchain throughput) and qualitative assessment (expert feedback on architectural soundness and FYP-level evaluation). Pragmatism accommodates this mixed approach by focusing on practical outcomes rather than adhering to a single epistemological position (Saunders et al., 2019). |
| **Approach** | Deductive | The research tests specific hypotheses derived from the literature review: (H1) Tenant-salted convergent encryption eliminates cross-tenant information leakage; (H2) A Siamese CNN can detect near-duplicates on encrypted files with >85% recall; (H3) Kyber-768 hybrid encryption introduces <40% overhead; (H4) PoA blockchain achieves >10,000 tx/sec for audit logging. Each hypothesis is tested through controlled experiments. |
| **Methodological Choice** | Mixed Methods | Quantitative methods measure system performance (encryption benchmarks, AI accuracy metrics, blockchain throughput). Qualitative methods capture expert domain feedback through a structured evaluation questionnaire. This mixed approach ensures both technical validity and practical relevance. |
| **Strategy** | Experimental + Survey | **Experimental:** Controlled experiments test each of Cloud Seal's six components under defined conditions (file sizes, tenant configurations, dataset compositions). **Survey:** A structured expert evaluation form (Google Form) collects feedback on architectural soundness, novelty, and FYP-level assessment from domain experts in cloud security, cryptography, and AI/ML. |
| **Time Horizon** | Cross-Sectional | All experiments and evaluations were conducted within a single time period (January–March 2026). The system is evaluated as a snapshot rather than tracked longitudinally, as the PoC is not deployed in a live production environment. |
| **Data Collection** | Primary + Secondary | **Primary:** Expert feedback collected via structured Google Form questionnaire; performance metrics generated from controlled experiments on the Cloud Seal prototype. **Secondary:** Custom generated dummy files (text documents, images, binary blobs) used for AI training and deduplication testing. No sensitive, personal, or public benchmark data was used. |

*Table 3.1: Saunders' Research Onion — Methodology Selections*

### 3.2.2 Research Hypotheses

Based on the research questions defined in Chapter 1 and the gaps identified in Chapter 2, the following hypotheses guide the experimental evaluation:

| ID | Hypothesis | Derived From | Measurement | Result |
|---|---|---|---|---|
| H1 | Tenant-specific convergent encryption achieves 0% cross-tenant information leakage in multi-tenant deduplication scenarios. | RQ2 | Security test: 100 cross-tenant upload attempts. | **Confirmed** — 0% leakage across all tests. |
| H2 | The Siamese CNN achieves ≥85% recall for near-duplicate detection on encrypted files without requiring decryption. | RQ3 | AI evaluation: 500-file dataset with controlled similarity levels. | **Confirmed** — 94% recall achieved. |
| H3 | Kyber-768 hybrid encryption introduces less than 40% overhead compared to classical AES-256, with overhead decreasing proportionally as file size increases. | RQ4 | Performance benchmark: encrypt/decrypt across 1KB–10MB file sizes. | **Confirmed** — 6.3% at 1KB, 38.2% at 100KB, decreasing with larger files. |
| H4 | PoA blockchain audit logging sustains >10,000 transactions per second for deduplication operation recording. | RQ4 | Blockchain stress test: batch transaction mining. | **Confirmed** — 29,608 tx/sec achieved. |
| H5 | Bloom filter duplicate detection operates in O(1) time with a false positive rate within 2% of the target rate (1%). | RQ1 | Bloom filter benchmark: 100–10,000 item insertions and queries. | **Confirmed** — ~0.001ms lookups, 1.1% FP rate. |
| H6 | The end-to-end pipeline (hash → Bloom check → encrypt → blockchain log) completes within 5 seconds for files up to 1MB. | RQ1, RQ4 | Pipeline benchmark: timed end-to-end file processing. | **Confirmed** — 5.11ms for 1MB (well under 5s). |

*Table 3.2: Research Hypotheses and Results*

### 3.2.3 Data Collection Methods

#### 3.2.3.1 Quantitative Data Collection

Quantitative data was gathered using automated test scripts executed against the Cloud Seal prototype. The test suite comprises eight specialised scripts:

| Test Script | Purpose | Iterations |
|---|---|---|
| `test_performance_benchmarks.py` | Encryption latency, PQC overhead, pipeline timing | 10–20 runs per metric |
| `test_ai_evaluation.py` | Siamese CNN precision, recall, FP rate, AUC | 500-file controlled dataset |
| `test_bloom_filter_accuracy.py` | FP rate, lookup time, memory consumption | 100–10,000 items |
| `test_blockchain_integrity.py` | Chain validation, transaction throughput | 50–150 transactions |
| `test_deduplication_efficiency.py` | Dedup ratio, storage savings | Multiple file types and sizes |
| `test_multitenant_safety.py` | Cross-tenant leakage, isolation verification | 100 cross-tenant attempts |
| `test_security_threat_model.py` | Confirmation attack, dictionary attack resistance | Automated adversarial tests |
| `run_all_tests.py` | Orchestrates full test suite execution | Complete end-to-end |

*Table 3.3: Quantitative Test Scripts*

All timing measurements use Python's `time.perf_counter()` for nanosecond-precision benchmarking. Each metric is measured across 10–20 iterations to ensure statistical reliability. Results are exported to JSON files (`test_results_performance.json`, `test_results_ai_evaluation.json`, `test_results_security.json`) for reproducible analysis.

#### 3.2.3.2 Qualitative Data Collection

Qualitative data was collected via a structured expert evaluation survey using Google Forms, distributed to domain experts across cloud security, cryptography, and AI/ML. The survey contains:

- **Likert-scale questions (1–5):** Rating novelty, technical soundness, practical viability, and whether the project meets/exceeds undergraduate FYP expectations.
- **Open-ended paragraph responses:** Identifying strengths, weaknesses, critical flaws, and suggestions for improvement.
- **FYP-level assessment:** Experts evaluate whether the scope and technical complexity exceed typical undergraduate expectations.

### 3.2.4 Ethical Considerations

- No personal, sensitive, or confidential data is used in any experiment. All test datasets consist of custom-created dummy files with controlled variations.
- Expert participation in the evaluation survey is voluntary. Name and affiliation fields are optional.
- The study does not engage human subjects in a clinical or behavioural sense; ethical approval is not required per the institution's software engineering research guidelines.

## 3.3 Development Methodology

### 3.3.1 Methodology Selection

The project adopts an **Agile-PRINCE2 hybrid** method—combining the flexibility of Agile with the governance structure of PRINCE2. Agile supports iterative, research-driven development and adapts to feedback from testing each component, while PRINCE2 ensures structured project planning, milestone tracking, and alignment with academic deadlines.

| Methodology | Strengths | Weaknesses | Suitability for Cloud Seal |
|---|---|---|---|
| Waterfall | Clear stages, easy to manage | Inflexible to change, late testing | Low — research requires iteration |
| Agile (Scrum) | Iterative, adaptive, feedback-driven | Lacks formal governance | Medium — needs academic structure |
| PRINCE2 | Strong governance, milestone tracking | Rigid, process-heavy | Medium — too rigid alone |
| **Agile-PRINCE2 Hybrid** | **Iterative + governed, flexible + structured** | **Requires discipline** | **High — best fit** |

*Table 3.4: Development Methodology Comparison*

### 3.3.2 Requirement Elicitation Methodology

Requirements for the Cloud Seal framework were gathered using a triangulated methodology:

| Method | Description | Justification |
|---|---|---|
| Literature Review | Systematic review of peer-reviewed articles and standards on secure deduplication, blockchain access control, and PQC (Bellare et al., 2013; Chen et al., 2024; NIST, 2024). | Provides academically validated best practices and identifies state-of-the-art requirements. |
| Semi-Structured Interviews | Conducted with cloud practitioners and security professionals to gather functional/non-functional needs (latency expectations, tenant isolation requirements). | Captures practical constraints and operational realities not found in literature. |
| Expert Evaluation Survey | Online Google Forms questionnaire distributed to domain experts for feedback on architectural decisions. | Ensures quantitative and qualitative validation of requirements across a wider audience. |
| Self-Evaluation | Developer reflection on implementation feasibility based on iterative prototyping and testing. | Identifies practical constraints discovered during hands-on development. |

*Table 3.5: Requirement Elicitation Methods*

### 3.3.3 Design Methodology

**Object-Oriented Analysis and Design Methodology (OOADM)** was selected as the core design strategy, aligned with the modular, component-based architecture of Cloud Seal.

| Evaluation Factor | SSADM Suitability | OOADM Suitability | Selected |
|---|---|---|---|
| System Architecture | Process-centric flows | Component-based microservices | OOADM |
| Design Knowledge | Unknown/exploratory | Known architectural patterns | OOADM |
| Implementation Target | Monolithic systems | Distributed containerised deployment | OOADM |
| Reusability | Limited reuse focus | High modularity and reuse | OOADM |
| Technology Integration | Sequential processing | Multiple interacting services | OOADM |

*Table 3.6: Design Methodology Selection — SSADM vs. OOADM*

**Justification:** Cloud Seal's six components (encryption, AI engine, blockchain, Bloom filter, IPFS manager, PQC key manager) are implemented as independent Python classes with clear interfaces. Each class encapsulates its own state and behaviour—reflecting core OOP principles of encapsulation, abstraction, and modularity. The `app.py` FastAPI application composes these components, demonstrating dependency injection and separation of concerns.

### 3.3.4 Programming Paradigm

| Paradigm | Application in Cloud Seal | Coverage | Example |
|---|---|---|---|
| **Object-Oriented Programming** | Core services, component architecture | ~80% | `SimpleCNN`, `BloomFilter`, `IPFSManager`, `DistributedBlockchain`, `PQCKeyManager` classes |
| **Functional Programming** | Data transformation pipelines, feature extraction | ~15% | NumPy vectorised operations in `BinaryFileEncoder.encode_file()`, hash chain computation |
| **Procedural Programming** | FastAPI route handlers, test scripts | ~5% | `upload_file()`, `delete_file()` endpoint functions |

*Table 3.7: Programming Paradigm Distribution*

### 3.3.5 Dataset and AI Model Pipeline

The Siamese CNN component required a structured pipeline for data preparation, feature engineering, model training, and evaluation.

| Pipeline Stage | Implementation Details | Measurable Targets | Actual Results |
|---|---|---|---|
| **Data Collection** | 500 custom dummy files across categories: text documents, images, binary blobs. Synthetic duplicates created with controlled overlap levels. | Complete category coverage, zero file corruption | ✅ Achieved |
| **Duplicate Pattern Creation** | Three similarity levels: Identical (95–100%), Near-duplicate (>80% overlap), Different (<40% overlap). | Accurate ratio control ±2% | ✅ Achieved |
| **Feature Extraction** | `BinaryFileEncoder` extracts 2048-dimensional vectors: byte frequency distribution (256 bins), byte pair frequencies (256 features), chunk-level Shannon entropy (256 values), statistical moments (mean, std, skewness, kurtosis). Z-score normalisation applied. | Processing speed >50MB/sec | ✅ Achieved |
| **Model Training** | `SimpleCNN` Siamese network with contrastive loss. Two-layer projection (2048→512→128) with Xavier initialisation, ReLU activation, L2 normalisation. Gradient backpropagation with clipping. | 10+ epochs, converging loss | ✅ 20 epochs, loss converged |
| **Evaluation** | Cosine similarity scoring. Threshold at 0.85. Metrics: precision, recall, FP rate, AUC-ROC. | Precision >90%, Recall >85% | ✅ Precision 96%, Recall 94% |

*Table 3.8: AI Model Pipeline — Cloud Seal Siamese CNN*

### 3.3.6 Metrics and Evaluation Formulae

The following metrics were used to evaluate Cloud Seal's performance:

**1. Deduplication Ratio**
```
Dedup_Ratio = (Logical_Size_Before − Physical_Size_After) / Logical_Size_Before
```

**2. Storage Savings (%)**
```
Storage_Savings (%) = 100 × (1 − Physical_Size_After / Logical_Size_Before)
```
*Cloud Seal achieved 42–55% storage savings in testing.*

**3. AI Similarity Score**
```
Cosine_Similarity = dot(embedding_1, embedding_2) / (‖embedding_1‖ × ‖embedding_2‖)
```
*Scores >0.85 flag near-duplicates for human review.*

**4. Bloom Filter False Positive Rate**
```
Theoretical_FP = (1 − e^(−k×n/m))^k
```
*Where k = hash functions (6), n = items inserted, m = bit array size (95,850 for 10K items).*

**5. Blockchain Throughput**
```
Throughput (tx/sec) = Total_Transactions / Total_Time_Seconds
```
*Cloud Seal achieved 29,608 tx/sec.*

**6. PQC Overhead**
```
PQC_Overhead (%) = 100 × (PQC_Time − Classical_Time) / Classical_Time
```
*Measured at 6.3% (1KB) to 38.2% (100KB), decreasing with larger files.*

### 3.3.7 Testing Methodology

Testing followed a layered approach, with each Cloud Seal component tested independently before integration testing.

| Testing Layer | Scope | Tools | Key Metrics |
|---|---|---|---|
| **Unit Testing** | Individual component functions (encryption, hashing, Bloom filter ops, blockchain transactions) | PyTest | Correctness, edge cases |
| **Component Testing** | Full component behaviour (`AIDeduplicationEngine`, `DistributedBlockchain`, `PQCKeyManager`) | PyTest + custom scripts | Accuracy, throughput |
| **Integration Testing** | End-to-end pipeline (upload → hash → Bloom check → encrypt → store → blockchain log) | `run_all_tests.py` | Pipeline latency, correctness |
| **Security Testing** | Cross-tenant leakage, confirmation attacks, dictionary attacks | `test_security_threat_model.py` | 0% leakage rate |
| **Performance Testing** | Encryption latency, PQC overhead, blockchain throughput across file sizes (1KB–10MB) | `test_performance_benchmarks.py` | Latency targets met |
| **AI Model Evaluation** | Precision, recall, FP rate, AUC-ROC on 500-file controlled dataset | `test_ai_evaluation.py` | 94% recall, 96% precision |

*Table 3.9: Testing Methodology Layers*

### 3.3.8 Solution Methodology

The Cloud Seal PoC was developed in a phased approach, with each phase building upon the validated output of the previous phase.

| Phase | Key Activities | Deliverables | Success Criteria | Timeline |
|---|---|---|---|---|
| **1. Requirements & Architecture** | Consolidate elicited requirements, define acceptance criteria, design six-component architecture | Prioritised use cases, system architecture diagram, PoC acceptance criteria | Clear component interfaces, measurable NFRs defined | Weeks 1–2 |
| **2. Core Encryption & Dedup** | Implement AES-256-CBC encryption, SHA-256 tenant-salted convergent key derivation, Bloom filter with MurmurHash3 | `encryption.py`, `bloom_filter.py`, unit tests | <1% FP rate, correct encrypt/decrypt cycle, tenant key isolation | Weeks 3–4 |
| **3. Storage & Audit** | Implement simulated IPFS (content-addressed storage with CID generation, pinning), PoA blockchain (block creation, chain validation, transaction logging) | `ipfs_manager.py`, `blockchain_distributed.py` | Immutable storage, valid chain integrity, >10K tx/sec | Weeks 5–6 |
| **4. AI & PQC** | Implement Siamese CNN (`BinaryFileEncoder` + `SimpleCNN` with contrastive loss), Kyber-768 key encapsulation (`SimulatedKyber` + `PQCKeyManager` + `HybridEncryption`) | `ai_deduplication.py`, `pcq_kyber.py` | >85% recall on encrypted files, <40% PQC overhead | Weeks 7–8 |
| **5. Integration & API** | FastAPI backend integration (`app.py`), HTML/CSS/JS frontend, Docker containerisation | Complete web application, Dockerfile | Full upload→dedup→store→audit pipeline working | Weeks 9–10 |
| **6. Testing & Evaluation** | Execute full test suite (8 scripts), collect expert feedback (Google Form), generate evaluation metrics | Test results (JSON), expert feedback data | All 6 hypotheses confirmed, expert validation received | Weeks 11–12 |

*Table 3.10: Solution Methodology — Phased Development*

#### Technical Implementation Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.11 | Core backend implementation |
| Web Framework | FastAPI | Latest | RESTful API with async support |
| Encryption | `cryptography` library (AES-256-CBC) | Latest | File encryption and decryption |
| Hashing | `hashlib` (SHA-256), `mmh3` (MurmurHash3) | Built-in / Latest | Convergent key derivation, Bloom filter hashing |
| AI/ML | NumPy | Latest | Siamese CNN, feature vector computation |
| PQC | SHAKE-256 (simulated Kyber-768) | Built-in | Post-quantum key encapsulation |
| Blockchain | Custom PoA implementation | N/A | Distributed audit logging |
| Storage | Simulated IPFS (local filesystem) | N/A | Content-addressed file storage |
| Containerisation | Docker Desktop | Latest | Isolated, reproducible deployment |
| Frontend | HTML, CSS, JavaScript | N/A | Web-based user interface |
| Testing | PyTest | Latest | Unit, component, and integration testing |
| Deployment | WSO2 Choreo | Cloud | Production staging and hosting |
| Version Control | Git / GitHub | Latest | Source code management |

*Table 3.11: Technical Implementation Stack*

## 3.4 Project Management Methodology

### 3.4.1 Methodology Selection

The project uses an **Agile-PRINCE2 hybrid** method—combining the iterative flexibility of Agile with the governance structure of PRINCE2. Agile supported research-driven development with rapid feedback loops (each component was tested immediately after implementation), while PRINCE2 ensured alignment with academic deadlines, milestone tracking, and structured deliverable management.

### 3.4.2 Deliverables Schedule

| Deliverable | Date |
|---|---|
| Project Proposal | 18th Aug 2025 |
| Literature Review | 24th Aug 2025 |
| Software Requirement Specification | 20th Aug 2025 |
| Project Proposal – Initial Draft | 26th Sep 2025 |
| Project Proposal and Requirement Specification – Final | 13th Nov 2025 |
| Proof of Concept | 14th Nov 2025 |
| Design Document | 20th Nov 2025 |
| Prototype (All 6 Components) | 2nd Feb 2026 |
| Interim Project Demo | 2nd Feb 2026 |
| Full Implementation (AI + PQC + Blockchain) | 10th Feb 2026 |
| Testing (Full Test Suite — 8 Scripts) | 15th Feb 2026 |
| Expert Evaluation (Google Form Collection) | 3rd Mar 2026 |
| Thesis Submission | 1st Apr 2026 |
| Minimum Viable Product | 1st Apr 2026 |

*Table 3.12: Deliverables Schedule*

### 3.4.3 Resource Management

#### 3.4.3.1 Hardware

| Component | Specification | Purpose |
|---|---|---|
| Development Machine | Apple MacBook Pro M2 (8-core CPU, 10-core GPU, 16 GB RAM, 512 GB SSD) | Development, testing, containerised deployment |
| Storage | ≥100 GB free space | Test datasets, encrypted objects, Docker images, AI model weights |
| Network | Localhost / LAN + Choreo cloud staging | API communication and cloud deployment testing |

*Table 3.13: Hardware Resources*

#### 3.4.3.2 Data

| Aspect | Description |
|---|---|
| Data Type | Custom-generated dummy files and synthetic data |
| Data Volume | 500+ files across text, images, binary blobs (KB to MB scale) |
| Data Characteristics | Controlled duplicate ratios: identical, near-duplicate (>80% overlap), and unique files created by modifying base dummy files |
| Source | Generated locally by the author — no human, personal, sensitive, or public benchmark data |
| Usage Purpose | AI model training/evaluation, deduplication accuracy testing, encryption benchmarking |

*Table 3.14: Data Resources*

#### 3.4.3.3 Skills

| Skill Area | Application in Cloud Seal |
|---|---|
| Python Programming | Core backend (FastAPI, encryption, AI, blockchain implementations) |
| Machine Learning | Siamese CNN architecture, contrastive loss, feature engineering |
| Cryptography | AES-256-CBC, SHA-256, SHAKE-256, Kyber-768 KEM concepts |
| Cloud & Storage | Docker containerisation, IPFS concepts, Choreo deployment |
| Blockchain | PoA consensus, chain validation, transaction logging |
| Web Development | HTML/CSS/JS frontend, FastAPI REST API design |

*Table 3.15: Skills Requirements*

### 3.4.4 Risk Management

Risk assessment employs quantitative analysis: **Risk Exposure = Probability × Impact** (each scored 1–5, maximum exposure = 25).

| Risk | Probability (1–5) | Impact (1–5) | Risk Score | Mitigation Strategy |
|---|---|---|---|---|
| PQC algorithm performance overhead exceeds acceptable limits | 4 | 5 | 20 | Implemented hybrid classical-quantum approach; Kyber-768 simulation keeps overhead to 6–38% |
| AI model training data insufficiency | 5 | 4 | 20 | Developed synthetic dataset generation with controlled similarity levels; 500-file evaluation corpus |
| Blockchain scalability limitations under high load | 4 | 5 | 20 | Selected PoA consensus (low latency, deterministic finality); achieved 29,608 tx/sec |
| Integration complexity exceeding timeline | 4 | 4 | 16 | Adopted modular development with independent component testing; each module has standalone `__main__` demo |
| Production Kyber library (liboqs) compatibility issues | 3 | 4 | 12 | Used SHAKE-256 simulation for PoC; documented migration path to liboqs for production |
| Cloud deployment environment restrictions | 3 | 3 | 9 | Implemented fallback storage paths in `config.py` for read-only filesystem environments (Choreo) |
| Stakeholder requirement changes | 3 | 3 | 9 | Agile methodology with regular stakeholder communication and iterative requirement validation |

*Table 3.16: Risk Assessment and Mitigation*

## 3.5 Chapter Summary

This chapter has presented the pragmatic, mixed-methods research methodology underpinning the Cloud Seal project. The Saunders Research Onion framework guided selections at each methodological layer, with pragmatism as the research philosophy, a deductive approach testing six specific hypotheses, and an experimental-plus-survey strategy combining quantitative benchmarking with qualitative expert feedback.

Development followed an Agile-PRINCE2 hybrid methodology with OOADM as the design approach and OOP as the primary programming paradigm. The six-component architecture was implemented in phased sprints, with each component independently tested before integration. The Siamese CNN pipeline—from data collection through feature extraction, contrastive learning, and cosine-similarity evaluation—was documented alongside the evaluation formulae used to measure all system metrics.

All six hypotheses were confirmed through controlled experimentation: 0% cross-tenant leakage (H1), 94% AI recall on encrypted files (H2), 6–38% PQC overhead (H3), 29,608 blockchain tx/sec (H4), ~0.001ms Bloom filter lookups at 1.1% FP rate (H5), and sub-6ms end-to-end pipeline for 1MB files (H6). The following chapters present these results in detail.
