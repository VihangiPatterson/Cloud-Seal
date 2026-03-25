# Chapter 5: Social, Legal, Ethical and Professional Issues (SLEP)

## 5.1 Chapter Overview

This chapter examines the Social, Legal, Ethical, and Professional (SLEP) issues encountered during the development and evaluation of **Cloud Seal**, a Privacy-Preserving Multi-Tenant Cloud Deduplication system. As the system handles sensitive encrypted data across multiple tenants in a shared cloud environment, it raises significant concerns around data privacy, tenant confidentiality, regulatory compliance, and professional responsibility.

All issues identified in this chapter are assessed against the **BCS Code of Conduct** (British Computer Society, 2022), which outlines the professional standards expected of IT practitioners. The BCS Code of Conduct is structured around four key principles:

1. **Public Interest** – Members shall have due regard for public health, privacy, security, and the environment.
2. **Professional Competence and Integrity** – Members shall only undertake to do work within their competence and shall act with integrity.
3. **Duty to Relevant Authority** – Members shall carry out professional responsibilities with due care and diligence in accordance with the relevant authority's requirements.
4. **Duty to the Profession** – Members shall act with integrity and respect in their professional relationships.

Each SLEP issue identified below is mapped to the relevant BCS principle, with specific mitigation strategies that were implemented within the Cloud Seal project.

---

## 5.2 SLEP Issues and Mitigation

### 5.2.1 Social Issues

| Issue | Description | BCS Principle | Mitigation |
|-------|-------------|---------------|------------|
| **Digital Divide in Cloud Security** | Cloud Seal uses advanced Post-Quantum Cryptography (Kyber-768) and AI-based deduplication, which may not be accessible or understandable to all users and organisations, particularly smaller businesses without dedicated IT teams. This could widen the gap between organisations that can adopt quantum-safe security and those that cannot. | Public Interest (1) | The system was designed with a user-friendly web dashboard that abstracts the complex cryptographic operations behind simple UI elements (e.g., a checkbox for "Post-Quantum Encryption"). This ensures that even non-technical users can benefit from advanced security without needing to understand the underlying algorithms. Additionally, all source code is open-source, allowing community adoption and education. |
| **Impact on Cloud Storage Employment** | Automated AI-based deduplication and blockchain auditing reduce the need for manual storage management and compliance auditing roles, potentially affecting employment in cloud operations teams. | Public Interest (1) | The system is positioned as a tool to augment, not replace, human administrators. The Cloud Administrator role remains essential for monitoring system performance, managing tenant onboarding, and making policy decisions. The dashboard provides administrators with real-time insights rather than automating their decision-making entirely. |
| **Multi-Tenant Trust Dynamics** | Organisations sharing the same physical storage infrastructure through Cloud Seal must trust that the system correctly isolates their data. A breach of this trust could have significant social consequences, particularly in industries handling sensitive data (healthcare, finance, legal). | Public Interest (1) | Implemented cryptographic tenant isolation using per-tenant encryption keys derived through convergent encryption. Reference counting ensures no tenant can access another tenant's data. The blockchain audit trail provides transparent, immutable proof of all data operations, allowing tenants to independently verify system integrity. |

### 5.2.2 Legal Issues

| Issue | Description | BCS Principle | Mitigation |
|-------|-------------|---------------|------------|
| **GDPR Compliance (Data Protection Act 2018)** | Cloud Seal processes and stores encrypted files on behalf of multiple tenants, potentially including personal data subject to GDPR. Article 17 (Right to Erasure) requires that personal data be deleted upon request, which conflicts with deduplication where multiple tenants may reference the same physical file. | Duty to Relevant Authority (3) | The reference counting mechanism ensures GDPR compliance. When a tenant requests deletion, their reference is removed immediately. The physical file is only deleted when the last reference reaches zero, ensuring no tenant retains access to another's data while respecting the right to erasure. The blockchain audit trail provides a tamper-proof record proving that the deletion request was processed. |
| **Data Sovereignty and Cross-Border Storage** | Cloud Seal is deployed on Choreo (Azure EU North), meaning data is stored in EU data centres. Tenants from different jurisdictions may have conflicting data residency requirements. | Duty to Relevant Authority (3) | The system's deployment region was carefully chosen (EU North) to comply with GDPR's data residency requirements. The deployment configuration is documented, and the Dockerised architecture allows redeployment to region-specific cloud infrastructure if tenants require data to remain within specific jurisdictions. |
| **Intellectual Property of Stored Files** | The deduplication process means that a file uploaded by Tenant A may be physically linked to the same storage location as a file uploaded by Tenant B. This raises questions about intellectual property ownership when two parties independently upload identical content. | Duty to Relevant Authority (3) | Each tenant maintains independent ownership metadata tracked via the reference counting system. The blockchain ledger records exactly which tenant uploaded which file and when, providing a timestamped proof of ownership. Physical storage linkage does not imply shared ownership—each tenant's access is independently managed through their own encryption keys and access control lists. |
| **Computer Misuse Act 1990** | As a security-focused system, Cloud Seal must ensure it does not facilitate or become vulnerable to unauthorised access, which would constitute an offence under the Computer Misuse Act. | Public Interest (1) | AES-256 encryption ensures files are unreadable without proper keys. Kyber-768 post-quantum key encapsulation protects against future quantum computing attacks. The Bloom filter and hash-based deduplication never expose plaintext data during the duplicate checking process, ensuring all operations occur on encrypted data only. |

### 5.2.3 Ethical Issues

| Issue | Description | BCS Principle | Mitigation |
|-------|-------------|---------------|------------|
| **AI Transparency and Bias** | The CNN-based similarity detection model makes automated decisions about whether files are "similar enough" to deduplicate. This raises ethical concerns about algorithmic transparency—tenants may not understand why their files were flagged as duplicates or how the AI reaches its decisions. | Professional Competence and Integrity (2) | The system implements AI similarity detection as a "suggestion" rather than an automatic action. The dashboard clearly displays similarity scores (e.g., "94% similar") and allows administrators to review and approve deduplication decisions. The CNN model architecture, training process, and accuracy metrics (92% accuracy, 3% false positive rate) are fully documented in the project's technical documentation. |
| **Informed Consent for Deduplication** | When a tenant uploads a file that is deduplicated against another tenant's upload, the original uploader was not explicitly informed that their file's hash is being compared against future uploads. This raises consent issues. | Professional Competence and Integrity (2) | The deduplication process operates entirely on encrypted hashes—no plaintext data is ever compared. Tenants are informed during onboarding that the system performs privacy-preserving deduplication using cryptographic techniques. The Bloom filter only checks hash membership without revealing the content of any file, ensuring that the process is privacy-preserving by design. |
| **Data Integrity and Accountability** | If the blockchain audit trail contains incorrect entries (due to software bugs), it could falsely implicate or exonerate a tenant in a compliance audit. The immutability of blockchain means such errors cannot be easily corrected. | Professional Competence and Integrity (2) | Comprehensive testing was conducted on the blockchain module, achieving 100% tamper detection rate and 29,608 transactions per second in benchmark testing. The Proof-of-Authority consensus mechanism ensures only authorised validator nodes can write to the chain. Additionally, the system logs both the blockchain entry and a parallel application log, providing dual verification. |

### 5.2.4 Professional Issues

| Issue | Description | BCS Principle | Mitigation |
|-------|-------------|---------------|------------|
| **Professional Competence in Cryptography** | Implementing post-quantum cryptography (Kyber-768) and convergent encryption requires specialised knowledge. Incorrect implementation could create false confidence in the system's security while leaving it vulnerable to attack. | Professional Competence and Integrity (2) | The implementation follows NIST-approved standards for Kyber-768 (FIPS 203). Well-established Python libraries (PyCryptodome for AES-256) were used rather than custom cryptographic implementations. The encryption module was validated through 1,000+ test vectors with 100% pass rate and >10MB/sec throughput, as documented in the testing methodology. |
| **Honest Representation of System Capabilities** | As a Proof-of-Concept (PoC), Cloud Seal demonstrates capabilities at a smaller scale. There is a professional obligation not to overstate the system's production readiness. | Duty to the Profession (4) | The project is clearly labelled as a "PoC" (Proof of Concept) in all documentation and the repository name (`cloud-seal-poc`). Performance benchmarks are presented with their specific test conditions (e.g., "29,608 tx/sec on a single-node blockchain"). Limitations such as the CNN's 3% false positive rate and the requirement for further scalability testing are explicitly documented. |
| **Responsible Use of Open-Source Dependencies** | Cloud Seal relies on multiple open-source libraries (FastAPI, PyCryptodome, TensorFlow). There is a professional responsibility to ensure these dependencies are properly licensed and do not introduce security vulnerabilities. | Duty to the Profession (4) | All dependencies are documented in `requirements.txt` with version pinning. Only libraries with permissive open-source licences (MIT, Apache 2.0, BSD) were selected. The Docker containerisation provides an additional security boundary, isolating the application from the host system. |
| **Testing Rigour and Academic Integrity** | The test results presented in this project must accurately reflect the system's performance. Fabricating or selectively reporting results would violate both academic integrity and professional standards. | Professional Competence and Integrity (2) | Four dedicated test suites were developed: Blockchain Integrity (29,608 tx/sec, 100% tamper detection), Bloom Filter Accuracy (100% true positive, 0% false positive), Multi-Tenant Safety (100% isolation), and Deduplication Efficiency. All results are saved as reproducible JSON files and the test scripts are included in the repository for independent verification. |

---

### Summary Table: SLEP Issues at a Glance

| **Social** | **Legal** |
|-------------|-----------|
| • Digital divide in quantum-safe security adoption | • GDPR Article 17 compliance with deduplication |
| • Impact on cloud storage management employment | • Data sovereignty across jurisdictions |
| • Multi-tenant trust and data isolation confidence | • IP ownership of deduplicated files |
| | • Computer Misuse Act compliance |

| **Ethical** | **Professional** |
|-------------|------------------|
| • AI transparency in similarity detection decisions | • Competence in PQC implementation |
| • Informed consent for hash-based deduplication | • Honest representation of PoC limitations |
| • Data integrity of immutable blockchain records | • Responsible use of open-source dependencies |
| | • Testing rigour and academic integrity |

---

## 5.3 Chapter Summary

This chapter has examined the Social, Legal, Ethical, and Professional issues relevant to the Cloud Seal project, with each issue mapped to the appropriate principle of the BCS Code of Conduct (British Computer Society, 2022).

**Socially**, the project addresses the challenge of making advanced cryptographic security accessible to all organisations, while acknowledging the potential impact on cloud operations employment and the importance of maintaining trust in multi-tenant environments.

**Legally**, the system's reference counting mechanism was specifically designed to address GDPR compliance challenges inherent in deduplication systems, and the blockchain audit trail provides tamper-proof evidence of regulatory compliance.

**Ethically**, the AI similarity detection module was implemented with transparency in mind, providing explainable similarity scores rather than opaque automated decisions, and the entire deduplication process operates on encrypted data to preserve privacy by design.

**Professionally**, the project adheres to BCS standards by using NIST-approved cryptographic implementations, honestly representing the system as a Proof of Concept with documented limitations, and ensuring all test results are reproducible and verifiable.

The mitigation strategies implemented throughout the project demonstrate a commitment to responsible innovation, ensuring that the technological advancements in Cloud Seal are balanced against the legitimate concerns of all stakeholders.

---

### References

British Computer Society (2022) *BCS Code of Conduct*. Available at: https://www.bcs.org/membership-and-registrations/become-a-member/bcs-code-of-conduct/ (Accessed: 14 February 2026).

UK Government (2018) *Data Protection Act 2018*. Available at: https://www.legislation.gov.uk/ukpga/2018/12/contents/enacted (Accessed: 14 February 2026).

UK Government (1990) *Computer Misuse Act 1990*. Available at: https://www.legislation.gov.uk/ukpga/1990/18/contents (Accessed: 14 February 2026).

European Parliament (2016) *General Data Protection Regulation (GDPR)*. Regulation (EU) 2016/679. Available at: https://gdpr-info.eu/ (Accessed: 14 February 2026).
