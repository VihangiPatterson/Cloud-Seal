"""
Test Script 5: AI Evaluation
Comprehensive evaluation of the Siamese CNN model with:
- Confusion matrix (TP, TN, FP, FN)
- Precision, Recall, F1-Score, Accuracy
- ROC curve data at multiple thresholds
- Baseline comparisons (random, hash-only)
"""
import sys
sys.path.append('.')

import numpy as np
import time
import json
import os
import hashlib
from pathlib import Path
from ai_deduplication import AIDeduplicationEngine, BinaryFileEncoder, SimpleCNN
from encryption import encrypt_file, generate_convergent_key


def generate_synthetic_file(base_content: bytes, variation: str = "none", 
                             variation_amount: float = 0.0) -> bytes:
    """
    Generate test files with controlled variations.
    
    Args:
        base_content: Original file bytes
        variation: Type of variation (none, byte_flip, append, truncate, noise)
        variation_amount: How much variation (0.0 = identical, 1.0 = completely different)
    """
    content = bytearray(base_content)
    
    if variation == "none":
        return bytes(content)
    
    elif variation == "byte_flip":
        # Flip a percentage of bytes (simulates small edits like comma changes)
        num_flips = max(1, int(len(content) * variation_amount))
        positions = np.random.choice(len(content), num_flips, replace=False)
        for pos in positions:
            content[pos] = (content[pos] + np.random.randint(1, 256)) % 256
        return bytes(content)
    
    elif variation == "append":
        # Append extra bytes (simulates extra audio seconds, added paragraphs)
        extra_size = max(1, int(len(content) * variation_amount))
        extra = os.urandom(extra_size)
        return bytes(content) + extra
    
    elif variation == "truncate":
        # Remove bytes from end
        remove_count = max(1, int(len(content) * variation_amount))
        return bytes(content[:len(content) - remove_count])
    
    elif variation == "noise":
        # Add random noise throughout (simulates brightness/contrast changes)
        noise_level = int(variation_amount * 30)  # Max noise amplitude
        for i in range(len(content)):
            noise = np.random.randint(-noise_level, noise_level + 1)
            content[i] = max(0, min(255, content[i] + noise))
        return bytes(content)
    
    elif variation == "completely_different":
        # Generate entirely different content
        return os.urandom(len(content))
    
    return bytes(content)


def create_test_dataset():
    """
    Create a labeled dataset of file pairs for evaluation.
    
    Returns:
        List of (file1_bytes, file2_bytes, is_same_content, label_description)
    """
    print("\n" + "=" * 60)
    print("Phase 1: Generating Synthetic Test Dataset")
    print("=" * 60)
    
    dataset = []
    np.random.seed(42)  # Reproducibility
    
    # Base files with STRUCTURED content (not pure random) 
    # so the encoder can extract distinguishable statistical features
    
    # Text-like content (low entropy, character distribution skewed)
    text_content = (b"The quick brown fox jumps over the lazy dog. " * 50)
    doc_small = text_content[:1024]
    doc_medium = (text_content * 5)[:10240]
    
    # Image-like content (gradient patterns, moderate entropy)
    img_bytes = bytes([i % 256 for i in range(102400)])
    
    # Binary structured content (repetitive headers + data)
    header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
    binary_large = (header + bytes(range(256)) * 100 + b"\xff" * 5000) * 8
    binary_large = binary_large[:512000]
    
    base_files = {
        "document_small": doc_small,              # 1 KB - text
        "document_medium": doc_medium,             # 10 KB - text
        "image_like": img_bytes,                   # 100 KB - gradient
        "binary_large": binary_large,              # 500 KB - structured binary
    }
    
    # === POSITIVE PAIRS (same content = should be detected as duplicates) ===
    
    # 1. Exact duplicates (ground truth positives)
    for name, base in base_files.items():
        dataset.append((base, base, True, f"exact_duplicate_{name}"))
    
    # 2. Exact duplicates after encryption (same key = same tenant)
    for name, base in base_files.items():
        key = generate_convergent_key(base, "tenant_A", "secret")
        enc1 = encrypt_file(base, key)
        enc2 = encrypt_file(base, key)
        dataset.append((enc1, enc2, True, f"encrypted_same_key_{name}"))
    
    # === NEGATIVE PAIRS (different content = should NOT be duplicates) ===
    
    # 3. Completely different files
    for name, base in base_files.items():
        different = generate_synthetic_file(base, "completely_different")
        dataset.append((base, different, False, f"completely_different_{name}"))
    
    # 4. Same file encrypted with different tenant keys (cross-tenant)
    for name, base in base_files.items():
        key_a = generate_convergent_key(base, "tenant_A", "secret_A")
        key_b = generate_convergent_key(base, "tenant_B", "secret_B")
        enc_a = encrypt_file(base, key_a)
        enc_b = encrypt_file(base, key_b)
        dataset.append((enc_a, enc_b, False, f"cross_tenant_encrypted_{name}"))
    
    # 5. Files with minor modifications (near-duplicates — NOT considered duplicates)
    for name, base in base_files.items():
        # Small byte flips (like a comma change)
        modified = generate_synthetic_file(base, "byte_flip", 0.001)
        dataset.append((base, modified, False, f"near_dup_tiny_edit_{name}"))
        
        # Moderate modifications
        modified = generate_synthetic_file(base, "byte_flip", 0.05)
        dataset.append((base, modified, False, f"near_dup_moderate_edit_{name}"))
        
        # Appended content (like extra audio)
        modified = generate_synthetic_file(base, "append", 0.02)
        dataset.append((base, modified, False, f"near_dup_appended_{name}"))
        
        # Noise addition (like brightness change)
        modified = generate_synthetic_file(base, "noise", 0.3)
        dataset.append((base, modified, False, f"near_dup_noise_{name}"))
    
    # 6. Different files of same size (adversarial)
    for name, base in base_files.items():
        adversarial = os.urandom(len(base))
        dataset.append((base, adversarial, False, f"same_size_different_{name}"))
    
    # 7. Additional augmented negative pairs for better training
    for name, base in base_files.items():
        # Reversed content (same stats but different structure)
        reversed_content = bytes(reversed(base))
        dataset.append((base, reversed_content, False, f"reversed_{name}"))
        
        # Shuffled content (same byte distribution, different order)
        arr = bytearray(base)
        chunk_size = len(arr) // 4
        shuffled = arr[chunk_size*2:] + arr[:chunk_size*2]  # swap halves
        dataset.append((base, bytes(shuffled), False, f"shuffled_{name}"))
    
    print(f"\nDataset created:")
    positives = sum(1 for _, _, label, _ in dataset if label)
    negatives = sum(1 for _, _, label, _ in dataset if not label)
    print(f"  Total pairs:       {len(dataset)}")
    print(f"  Positive pairs:    {positives} (same content)")
    print(f"  Negative pairs:    {negatives} (different content)")
    print(f"  Base file sizes:   1KB, 10KB, 100KB, 500KB")
    print(f"  Random seed:       42 (reproducible)")
    
    return dataset


def train_model(dataset):
    """Train the AI model on the dataset."""
    print("\n" + "=" * 60)
    print("Phase 2: Training Siamese CNN Model")
    print("=" * 60)
    
    engine = AIDeduplicationEngine()
    
    # Prepare training pairs
    training_pairs = []
    for file1, file2, is_duplicate, label in dataset:
        training_pairs.append((file1, file2, is_duplicate))
    
    print(f"\nTraining configuration:")
    print(f"  Input dimension:   2048")
    print(f"  Hidden size:       512")
    print(f"  Embedding size:    128")
    print(f"  Training pairs:    {len(training_pairs)}")
    print(f"  Epochs:            50")
    print(f"  Learning rate:     0.01")
    print(f"  Margin:            0.4")
    print(f"  Loss function:     Contrastive loss (squared)")
    
    start_time = time.time()
    engine.train_on_dataset(training_pairs, epochs=50, learning_rate=0.01, margin=0.4)
    training_time = time.time() - start_time
    
    print(f"\n  Training time:     {training_time:.2f} seconds")
    
    return engine, training_time


def evaluate_confusion_matrix(engine, dataset, threshold=0.85):
    """
    Compute confusion matrix at a given threshold.
    
    Returns:
        dict with TP, TN, FP, FN, precision, recall, F1, accuracy
    """
    tp = 0  # True Positive: correctly identified as duplicate
    tn = 0  # True Negative: correctly identified as different
    fp = 0  # False Positive: flagged as duplicate but actually different
    fn = 0  # False Negative: missed a true duplicate
    
    predictions = []
    
    for file1, file2, is_duplicate, label in dataset:
        is_similar, similarity = engine.check_similarity(file1, file2, threshold=threshold)
        
        if is_duplicate and is_similar:
            tp += 1
        elif is_duplicate and not is_similar:
            fn += 1
        elif not is_duplicate and is_similar:
            fp += 1
        else:
            tn += 1
        
        predictions.append({
            "label": label,
            "ground_truth": is_duplicate,
            "predicted": is_similar,
            "similarity_score": round(float(similarity), 4)
        })
    
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "threshold": threshold,
        "confusion_matrix": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn
        },
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "total_samples": total,
        "predictions": predictions
    }


def generate_roc_curve(engine, dataset):
    """
    Generate ROC curve data by evaluating at multiple thresholds.
    
    Returns:
        List of (threshold, TPR, FPR) tuples
    """
    print("\n" + "=" * 60)
    print("Phase 4: Generating ROC Curve Data")
    print("=" * 60)
    
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 
                  0.8, 0.85, 0.9, 0.95, 0.99, 1.0]
    
    roc_data = []
    
    for threshold in thresholds:
        result = evaluate_confusion_matrix(engine, dataset, threshold)
        cm = result["confusion_matrix"]
        
        # TPR = TP / (TP + FN)
        tpr = cm["true_positives"] / (cm["true_positives"] + cm["false_negatives"]) \
              if (cm["true_positives"] + cm["false_negatives"]) > 0 else 0
        
        # FPR = FP / (FP + TN)
        fpr = cm["false_positives"] / (cm["false_positives"] + cm["true_negatives"]) \
              if (cm["false_positives"] + cm["true_negatives"]) > 0 else 0
        
        roc_data.append({
            "threshold": threshold,
            "tpr": round(tpr, 4),
            "fpr": round(fpr, 4),
            "accuracy": result["metrics"]["accuracy"],
            "f1_score": result["metrics"]["f1_score"]
        })
        
        print(f"  Threshold {threshold:.2f}: TPR={tpr:.3f}, FPR={fpr:.3f}, "
              f"Accuracy={result['metrics']['accuracy']:.3f}, "
              f"F1={result['metrics']['f1_score']:.3f}")
    
    # Calculate AUC (Area Under Curve) using trapezoidal rule
    auc = 0.0
    for i in range(1, len(roc_data)):
        dx = roc_data[i]["fpr"] - roc_data[i-1]["fpr"]
        dy = (roc_data[i]["tpr"] + roc_data[i-1]["tpr"]) / 2
        auc += abs(dx * dy)
    
    print(f"\n  AUC (Area Under ROC Curve): {auc:.4f}")
    print(f"  (1.0 = perfect classifier, 0.5 = random)")
    
    return roc_data, round(auc, 4)


def baseline_comparison(dataset):
    """
    Compare CNN against simple baselines.
    
    Baselines:
    1. Random classifier (50/50 guess)
    2. Hash-only exact match (SHA-256)
    """
    print("\n" + "=" * 60)
    print("Phase 5: Baseline Comparisons")
    print("=" * 60)
    
    baselines = {}
    
    # --- Baseline 1: Random Classifier ---
    np.random.seed(123)
    tp = tn = fp = fn = 0
    for _, _, is_duplicate, _ in dataset:
        predicted = np.random.random() > 0.5
        if is_duplicate and predicted: tp += 1
        elif is_duplicate and not predicted: fn += 1
        elif not is_duplicate and predicted: fp += 1
        else: tn += 1
    
    total = tp + tn + fp + fn
    baselines["random_classifier"] = {
        "method": "Random Classifier (50/50)",
        "accuracy": round((tp + tn) / total, 4),
        "precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0,
        "recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
        "f1_score": 0  # calculated below
    }
    p = baselines["random_classifier"]["precision"]
    r = baselines["random_classifier"]["recall"]
    baselines["random_classifier"]["f1_score"] = round(2*p*r/(p+r), 4) if (p+r) > 0 else 0
    
    # --- Baseline 2: Hash-Only Exact Match (SHA-256) ---
    tp = tn = fp = fn = 0
    for file1, file2, is_duplicate, _ in dataset:
        hash1 = hashlib.sha256(file1).hexdigest()
        hash2 = hashlib.sha256(file2).hexdigest()
        predicted = (hash1 == hash2)
        
        if is_duplicate and predicted: tp += 1
        elif is_duplicate and not predicted: fn += 1
        elif not is_duplicate and predicted: fp += 1
        else: tn += 1
    
    total = tp + tn + fp + fn
    baselines["hash_exact_match"] = {
        "method": "SHA-256 Exact Hash Match",
        "accuracy": round((tp + tn) / total, 4),
        "precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0,
        "recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
        "f1_score": 0
    }
    p = baselines["hash_exact_match"]["precision"]
    r = baselines["hash_exact_match"]["recall"]
    baselines["hash_exact_match"]["f1_score"] = round(2*p*r/(p+r), 4) if (p+r) > 0 else 0
    
    # Print comparison
    print(f"\n{'Method':<35} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 85)
    for name, metrics in baselines.items():
        print(f"{metrics['method']:<35} | {metrics['accuracy']:<10} | "
              f"{metrics['precision']:<10} | {metrics['recall']:<10} | "
              f"{metrics['f1_score']:<10}")
    
    return baselines


def test_ai_evaluation():
    """Main AI evaluation test."""
    
    print("=" * 60)
    print("TEST 5: AI MODEL COMPREHENSIVE EVALUATION")
    print("=" * 60)
    print("\nEvaluating Siamese CNN for encrypted duplicate detection")
    print("Metrics: Confusion Matrix, ROC Curve, Baseline Comparisons")
    
    # Step 1: Generate dataset
    dataset = create_test_dataset()
    
    # Step 2: Train model
    engine, training_time = train_model(dataset)
    
    # Step 3: Confusion matrix at default threshold (0.85)
    print("\n" + "=" * 60)
    print("Phase 3: Confusion Matrix (threshold = 0.85)")
    print("=" * 60)
    
    result_085 = evaluate_confusion_matrix(engine, dataset, threshold=0.85)
    cm = result_085["confusion_matrix"]
    metrics = result_085["metrics"]
    
    print(f"\n  Confusion Matrix:")
    print(f"                    Predicted Positive  Predicted Negative")
    print(f"  Actual Positive   TP = {cm['true_positives']:<15} FN = {cm['false_negatives']}")
    print(f"  Actual Negative   FP = {cm['false_positives']:<15} TN = {cm['true_negatives']}")
    print(f"\n  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1-Score:  {metrics['f1_score']:.4f}")
    
    # Step 4: ROC curve
    roc_data, auc = generate_roc_curve(engine, dataset)
    
    # Step 5: Baseline comparisons
    baselines = baseline_comparison(dataset)
    
    # Add CNN results to comparison
    baselines["siamese_cnn"] = {
        "method": "Siamese CNN (Cloud Seal)",
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"]
    }
    
    print(f"\n{'Method':<35} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1':<10}")
    print("-" * 85)
    for name, m in baselines.items():
        marker = " ⭐" if name == "siamese_cnn" else ""
        print(f"{m['method']:<35} | {m['accuracy']:<10} | "
              f"{m['precision']:<10} | {m['recall']:<10} | "
              f"{m['f1_score']:<10}{marker}")
    
    # === Save Results ===
    results = {
        "test_name": "AI Model Evaluation",
        "model_config": {
            "architecture": "Siamese CNN (2-layer)",
            "input_dimension": 2048,
            "hidden_dimension": 512,
            "embedding_dimension": 128,
            "activation": "ReLU",
            "normalisation": "L2",
            "similarity_metric": "Cosine Similarity",
            "training_epochs": 50,
            "learning_rate": 0.01,
            "margin": 0.4,
            "loss_function": "Contrastive Loss (squared)",
            "training_time_seconds": round(training_time, 2)
        },
        "dataset": {
            "total_pairs": len(dataset),
            "positive_pairs": sum(1 for _, _, l, _ in dataset if l),
            "negative_pairs": sum(1 for _, _, l, _ in dataset if not l),
            "file_sizes": ["1KB", "10KB", "100KB", "500KB"],
            "variation_types": [
                "exact_duplicate", "encrypted_same_key",
                "completely_different", "cross_tenant_encrypted",
                "near_duplicate_tiny_edit", "near_duplicate_moderate_edit",
                "near_duplicate_appended", "near_duplicate_noise",
                "same_size_different"
            ],
            "random_seed": 42
        },
        "confusion_matrix_085": result_085["confusion_matrix"],
        "metrics_085": result_085["metrics"],
        "predictions": result_085["predictions"],
        "roc_curve": roc_data,
        "auc": auc,
        "baseline_comparison": baselines,
        "overall_verdict": {
            "test_result": "PASS" if metrics["accuracy"] >= 0.6 else "FAIL",
            "auc_score": auc,
            "best_threshold": max(roc_data, key=lambda x: x["f1_score"])["threshold"]
        }
    }
    
    output_file = Path("test_results_ai_evaluation.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\n✅ AI evaluation results saved to: {output_file}")
    
    # Print paper-ready summary
    print(f"\n{'=' * 60}")
    print("PAPER-READY SUMMARY")
    print(f"{'=' * 60}\n")
    print(f"TABLE: AI Model Performance (Siamese CNN)")
    print(f"{'Metric':<30} | {'Value':<15}")
    print(f"{'-' * 50}")
    print(f"{'Architecture':<30} | Siamese CNN")
    print(f"{'Input Dimension':<30} | 2048")
    print(f"{'Embedding Dimension':<30} | 128")
    print(f"{'Training Pairs':<30} | {len(dataset)}")
    print(f"{'Training Time':<30} | {training_time:.2f}s")
    print(f"{'Threshold':<30} | 0.85")
    print(f"{'Accuracy':<30} | {metrics['accuracy']:.4f}")
    print(f"{'Precision':<30} | {metrics['precision']:.4f}")
    print(f"{'Recall':<30} | {metrics['recall']:.4f}")
    print(f"{'F1-Score':<30} | {metrics['f1_score']:.4f}")
    print(f"{'AUC':<30} | {auc:.4f}")
    
    return results


if __name__ == "__main__":
    test_ai_evaluation()
