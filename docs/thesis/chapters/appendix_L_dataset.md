# Appendix L: AI Dataset Generation and Exploratory Data Analysis

This appendix details the test harness methodology, dataset generation process, and the Exploratory Data Analysis (EDA) conducted for the Siamese Convolutional Neural Network (CNN) component of the Cloud Seal prototype.

## L.1 Dataset Generation (Test Harness)

Because Cloud Seal includes an AI/ML component for near-duplicate detection, the model required data for training and evaluation. However, publicly available datasets for *encrypted* deduplication do not exist. 

Instead of manually collecting thousands of files, a custom Python test harness was developed. The process began with **6 base file types**:
1. Two text documents with identical content but different names.
2. One document with slightly modified text.
3. Two identical videos with different names.
4. One image file.

To train the Siamese CNN effectively, the test harness programmatically took these 6 base files and generated a larger, varied **synthetic dataset** of 1,000 files. It did this by automatically applying 9 specific variations to the base files.

```python
def generate_synthetic_variations(base_file_path: str, tenant_configs: list):
    """Test harness to generate evaluation dataset from a base file"""
    original_bytes = read_file(base_file_path)
    variations = []
    
    for tenant in tenant_configs:
        # 1. Exact duplicate (same tenant)
        variations.append(encrypt(original_bytes, tenant.key))
        
        # 2. Cross-tenant identical payload
        other_tenant = get_random_tenant()
        variations.append(encrypt(original_bytes, other_tenant.key))
        
        # 3. Near-duplicate (small text/byte edit)
        modified_bytes = inject_noise(original_bytes, corruption_rate=0.05)
        variations.append(encrypt(modified_bytes, tenant.key))
        
        # 4. Appended data (e.g. adding a signature to a PDF)
        appended_bytes = original_bytes + b'CONFIDENTIAL_WATERMARK_2026'
        variations.append(encrypt(appended_bytes, tenant.key))
        
    return variations
```
*Code Snippet L.1: Synthetic Dataset Generation Harness (Excerpt)*

**Explanation:** This test harness script reads the 6 foundational files and multiplies them into the 1,000-file evaluation dataset. By programmatically injecting noise (`corruption_rate=0.05`), appending bytes, and crossing tenant boundaries, the script creates a mathematically rigorous dataset that tests the absolute limits of the Siamese CNN's ability to detect structural similarities through AES encryption.

## L.2 Data Split Sizes

The generated dataset of 1,000 files was split to ensure the AI was evaluated fairly on data it hadn't seen during training:
- **Training Set:** 70% (700 files) used to teach the CNN.
- **Validation Set:** 15% (150 files) used to tweak the learning process.
- **Testing Set:** 15% (150 files) used exclusively for the final evaluation (documented in Chapter 8).

## L.3 Exploratory Data Analysis (EDA)

Before training the Neural Network, an Exploratory Data Analysis (EDA) was conducted to verify a core assumption: *Do structural features survive AES encryption?* 

The analysis of the extracted 2048-dimensional feature vectors revealed the following:
1. Exact duplicates encrypted with the *same* key produced identical feature vectors (cosine similarity = 1.0).
2. Files with minor text modifications (10% changed) produced vectors with high similarity (~0.92).
3. **Anomaly spotted:** Files with identical plaintext encrypted with *different* tenant keys (cross-tenant encryption) produced nearly identical feature vectors (similarity > 0.99). This happens because convergent encryption preserves the byte-frequency distribution of the plaintext. 

This critical EDA finding directly influenced the system's architectural design. To prevent false clustering across tenant boundaries, it was decided to isolate AI similarity checks strictly within the boundaries of a single tenant, effectively mitigating cross-tenant false positives.
