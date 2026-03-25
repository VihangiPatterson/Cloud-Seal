# CHAPTER 01: INTRODUCTION

## 1.1 Chapter Overview

This chapter outlines the foundation for Cloud Seal, a privacy-preserving multi-tenant cloud deduplication framework. It introduces the problem background and definition, establishes the research motivation, and reviews existing literature to identify critical research gaps. The chapter then defines the project’s contribution to knowledge, challenges, research questions, aims, and objectives, before detailing the project scope and technical requirements.

## 1.2 Problem Background

Enterprise cloud adoption increases by roughly 25% per year (Gartner, 2023). Within such environments, storage deduplication—the process of eliminating redundant data—can reduce storage consumption by up to 90% (Dell Technologies, 2022). However, encryption introduces a fundamental paradox: conventional deduplication compares file contents to identify duplicates, yet encrypted files appear entirely different even when derived from identical plaintext. This forces organisations into an unacceptable trade-off between sacrificing encryption for deduplication, or sacrificing storage efficiency for security. Multi-tenant infrastructures amplify this: identical files uploaded by different tenants cannot be detected as duplicates under standard encryption securely.

Convergent encryption (CE) attempts to solve this by deriving the key deterministically from the file content. While CE enables deduplication, it introduces severe vulnerabilities, particularly confirmation attacks and cross-tenant privacy leaks, allowing adversaries to verify if a file exists (Bellare et al., 2013). Furthermore, the looming threat of quantum computing, highlighted by NIST's 2024 finalisation of post-quantum cryptography (PQC) standards, means existing systems relying on classical cryptography (RSA/ECC) are vulnerable to "harvest now, decrypt later" attacks. 

## 1.3 Problem Definition

Current cloud storage systems fail to securely deduplicate encrypted data in multi-tenant environments while simultaneously providing post-quantum readiness and near-duplicate detection. Existing solutions impose high computational complexity, lack quantum resistance, and rely on exact-matching only, rendering them inadequate for large-scale, enterprise multi-tenant deployments.

### 1.3.1 Problem Statement

The inefficiency of existing cloud deduplication models to securely process encrypted multi-tenant data while maintaining post-quantum resilience and near-duplicate detection accuracy is the key problem addressed in this project.

## 1.4 Research Motivation

With the increasing adoption of cloud storage in regulated sectors (such as healthcare and finance), enterprises require robust deduplication systems that can detect encrypted near-duplicates in real-time without compromising strict multi-tenant security or falling victim to future quantum computer attacks.

## 1.5 Existing Work

| Citation | Summary | Limitation | Contribution |
|---|---|---|---|
| Periasamy et al. (2025) | Investigated genetic programming for secure storage. | Exponential time complexity; no quantum resistance. | Blockchain-based access control integration. |
| Niu et al. (2024) | Proposed blockchain-based deduplication for cloud storage. | Uses classical RSA; lacks near-duplicate detection capability. | First attempt to frame deduplication securely using blockchain. |
| Li et al. (2025) | Similarity-preserving encryption for container images. | Operates solely on metadata; cannot process encrypted content bytes. | Novel semantic hashing approach. |
| Chen et al. (2024) | Lightweight cloud deduplication with access control. | Limited scalability in multi-tenant settings; no post-quantum considerations. | Enhanced lightweight key management for exact duplicates. |

Most deduplication models prioritize either encryption strength or storage efficiency, but very few balance both effectively in multi-tenant environments. Although blockchain and convergent encryption techniques have shown promising results in access control, deep learning algorithms have been heavily underexplored to improve near-duplicate accuracy directly on encrypted ciphertexts, and post-quantum readiness is absent from production systems.

## 1.6 Research Gap 

A critical gap exists in integrating AI, blockchain, and post-quantum cryptography into a single deduplication framework. All surveyed systems are limited to exact-duplicate detection (ignoring 30–50% of storage waste from minor document edits), and lack the dynamic access control necessary for multi-tenant isolation. No existing system performs AI-powered near-duplicate detection directly on encrypted files without requiring decryption.

## 1.7 Contribution to Body of Knowledge 

**Problem Domain Contribution:** This research addresses the encryption-deduplication paradox by providing an operational framework that achieves 42–55% storage savings and prevents cross-tenant data leakage, offering practical benefits to regulated cloud environments.

**Research Domain Contribution:** We propose using Siamese Convolutional Neural Networks (CNNs) to extract statistically significant features from encrypted byte patterns for near-duplicate detection, integrated with a Kyber-768 hybrid key encapsulation mechanism to advance post-quantum storage research.

## 1.8 Research Challenges

One of the main challenges is maintaining a balance between real-time deduplication performance and the high computational overhead imposed by both post-quantum cryptographic operations and AI similarity feature extraction.

## 1.9 Research Questions

- **RQ1:** How effectively can encrypted deduplication with Bloom filters and tenant-specific convergent encryption reduce storage redundancy in a multi-tenant cloud environment?
- **RQ2:** What are the security trade-offs introduced by convergent encryption, and how can they be mitigated to maintain cross-tenant isolation?
- **RQ3:** How can deep learning architectures (Siamese CNNs) be optimised to detect near-duplicates on encrypted files without decryption?
- **RQ4:** What architectural modifications are required to integrate post-quantum encryption (Kyber-768) and blockchain-based audit logging without prohibitive performance overhead?

## 1.10 Research Aim

The aim of this research is to analyse, design, develop, and evaluate a privacy-preserving multi-tenant cloud deduplication system using hybrid machine learning and post-quantum cryptographic models.

## 1.11 Research Objectives 

| Objectives | Research Objective Description | LOs Mapped | RQ Mapped |
|---|---|---|---|
| **Problem Identification** | RO1: To identify the research gaps in secure multi-tenant deduplication and quantum readiness. | L02 | RQ1, RQ2 |
| **Literature Review** | RO2: To conduct an in-depth literature survey on encrypted deduplication and post-quantum threats. <br> RO3: To review the best available ML-based techniques for near-duplicate ciphertext detection. | L01, L04 | RQ2, RQ3 |
| **Requirement Elicitation** | RO4: To identify the stakeholder requirements for developing a secure cloud deduplication system. <br> RO5: To identify the system requirements to build a post-quantum AI deduplication model. | L03 | RQ1, RQ4 |
| **System Design** | RO6: To design a unified AI–Blockchain–PQC architecture for securely identifying redundant files. | L01 | RQ1–RQ4 |
| **Implementation** | RO7: To completely implement a Siamese CNN hybrid machine learning model for ciphertext similarity detection. <br> RO8: To implement real-time deduplication mechanisms using Bloom filters and a PoA blockchain. | L01 | RQ3, RQ4 |
| **Testing** | RO9: To rigorously evaluate the accuracy, efficiency, and security isolation of the implemented prototype model against established targets. | L01, L03 | RQ1–RQ4 |
| **Documentation** | RO10: To comprehensively document the methodology, design, implementation, and evaluation findings of the research. | L04 | RQ1–RQ4 |

## 1.12 Project Scope

### 1.12.1 In Scope
The system will process standard binary and text data up to 1MB per file for performance testing. It will fully implement tenant-specific convergent encryption, O(1) Bloom filter detection, Siamese CNN similarity evaluations on 2048-dimensional encrypted byte features, Proof-of-Authority blockchain auditing, and Kyber-768 hybrid key encapsulation within a containerised multi-tenant environment.

### 1.12.2 Out Scope
The system will not implement a multi-node distributed blockchain network across distinct geographic servers; blockchain consensus is handled in a single-node implementation for the PoC. Live IPFS network integration is excluded (IPFS is simulated locally) and dynamic smart-contract key revocation is deferred to future work. The AI model will not be trained on highly sensitive or classified human data, using generated synthetic datasets instead.

## 1.13 Hardware and Software Requirements

| Category | Requirement Specification |
|---|---|
| **Hardware (Development)** | Apple M2 Chip (8-core CPU, 10-core GPU, 16 GB RAM), 100 GB SSD storage |
| **Backend & ML Environment** | Python 3.11, FastAPI 0.104.1, Uvicorn 0.24.0, NumPy 1.24.3 |
| **Cryptography & Algorithms** | `cryptography` (AES-256), `hashlib` (SHA-256), `mmh3` (MurmurHash3) |
| **Deployment / DB** | Docker Desktop, Simulated local IPFS, Local JSON (Blockchain) |

## 1.14 Chapter Summary

This chapter established the context for Cloud Seal by examining the exact conflict between encryption and deduplication in cloud storage, compounded by quantum threats and the limitation of exact-match detection. After reviewing recent literature, the critical gap was defined: no prior work securely integrates AI similarity detection, blockchain auditing, and PQC into one multi-tenant framework. To address this, the project’s aims, mapping of research objectives to learning outcomes, and precise scope criteria were systematically detailed to guide the system's subsequent design and implementation phases.
