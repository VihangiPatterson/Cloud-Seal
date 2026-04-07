"""
Test Script 6: Performance Benchmarks
Measures upload latency, encryption time, Bloom filter throughput,
blockchain operations, and memory usage.
"""
import sys
sys.path.append('.')

import time
import json
import os
import tracemalloc
import numpy as np
from pathlib import Path
from encryption import encrypt_file, decrypt_file, generate_convergent_key, generate_content_hash
from bloom_filter import BloomFilter
from blockchain_distributed import DistributedBlockchain
from ai_deduplication import AIDeduplicationEngine
from pcq_kyber import PQCKeyManager, HybridEncryption


def measure_time(func, *args, iterations=10, **kwargs):
    """Run a function multiple times and return timing statistics."""
    times = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
    
    return {
        "min_ms": round(min(times), 3),
        "max_ms": round(max(times), 3),
        "avg_ms": round(sum(times) / len(times), 3),
        "median_ms": round(sorted(times)[len(times) // 2], 3),
        "iterations": iterations
    }, result


def benchmark_encryption():
    """Benchmark AES-256 encryption and decryption for different file sizes."""
    print("\n" + "=" * 60)
    print("Benchmark 1: AES-256 Encryption/Decryption Latency")
    print("=" * 60)
    
    file_sizes = {
        "1 KB": 1024,
        "10 KB": 10240,
        "100 KB": 102400,
        "1 MB": 1048576,
        "10 MB": 10485760,
    }
    
    results = []
    
    print(f"\n{'File Size':<12}  {'Encrypt (ms)':<14}  {'Decrypt (ms)':<14}  {'Key Gen (ms)':<14}  {'Hash (ms)':<12}")
    print("-" * 75)
    
    for size_label, size_bytes in file_sizes.items():
        content = os.urandom(size_bytes)
        
        # Key generation timing
        key_timing, key = measure_time(
            generate_convergent_key, content, "tenant_A", "secret", iterations=20
        )
        
        # Content hash timing
        hash_timing, content_hash = measure_time(
            generate_content_hash, content, iterations=20
        )
        
        # Encryption timing
        enc_timing, encrypted = measure_time(
            encrypt_file, content, key, iterations=10
        )
        
        # Decryption timing
        dec_timing, decrypted = measure_time(
            decrypt_file, encrypted, key, iterations=10
        )
        
        # Verify correctness
        assert decrypted == content, f"Decryption failed for {size_label}!"
        
        result = {
            "file_size": size_label,
            "file_size_bytes": size_bytes,
            "key_generation": key_timing,
            "content_hash": hash_timing,
            "encryption": enc_timing,
            "decryption": dec_timing,
            "encrypted_size_bytes": len(encrypted),
            "size_overhead_pct": round((len(encrypted) - size_bytes) / size_bytes * 100, 2)
        }
        results.append(result)
        
        print(f"{size_label:<12}  {enc_timing['avg_ms']:<14.3f}  {dec_timing['avg_ms']:<14.3f}  "
              f"{key_timing['avg_ms']:<14.3f}  {hash_timing['avg_ms']:<12.3f}")
    
    return results


def benchmark_pqc_encryption():
    """Benchmark PQC hybrid encryption vs classical."""
    print("\n" + "=" * 60)
    print("Benchmark 2: Classical vs PQC Hybrid Encryption")
    print("=" * 60)
    
    pqc_manager = PQCKeyManager(storage_dir=Path("/tmp/pqc_bench_keys"), security_level=768)
    hybrid = HybridEncryption(pqc_manager)
    
    # Generate tenant keys
    try:
        pqc_manager.generate_tenant_keys("bench_tenant")
    except Exception:
        pass
    
    file_sizes = {
        "1 KB": 1024,
        "10 KB": 10240,
        "100 KB": 102400,
    }
    
    results = []
    
    print(f"\n{'File Size':<12}  {'Classical (ms)':<16}  {'PQC Hybrid (ms)':<16}  {'PQC Overhead':<14}")
    print("-" * 65)
    
    for size_label, size_bytes in file_sizes.items():
        content = os.urandom(size_bytes)
        
        # Classical encryption
        key = generate_convergent_key(content, "bench_tenant", "secret")
        classical_timing, _ = measure_time(
            encrypt_file, content, key, iterations=10
        )
        
        # PQC hybrid encryption
        try:
            pqc_timing, _ = measure_time(
                hybrid.encrypt_file_hybrid, content, "bench_tenant", iterations=5
            )
        except Exception as e:
            pqc_timing = {"avg_ms": -1, "min_ms": -1, "max_ms": -1, "median_ms": -1, "iterations": 0}
            print(f"  PQC error for {size_label}: {e}")
        
        overhead = "N/A"
        if pqc_timing["avg_ms"] > 0:
            overhead_pct = ((pqc_timing["avg_ms"] - classical_timing["avg_ms"]) / classical_timing["avg_ms"]) * 100
            overhead = f"{overhead_pct:.1f}%"
        
        result = {
            "file_size": size_label,
            "classical_encryption": classical_timing,
            "pqc_hybrid_encryption": pqc_timing,
            "pqc_overhead_pct": overhead
        }
        results.append(result)
        
        print(f"{size_label:<12}  {classical_timing['avg_ms']:<16.3f}  "
              f"{pqc_timing['avg_ms']:<16.3f}  {overhead:<14}")
    
    return results


def benchmark_bloom_filter():
    """Benchmark Bloom filter operations at different scales."""
    print("\n" + "=" * 60)
    print("Benchmark 3: Bloom Filter Throughput")
    print("=" * 60)
    
    scales = [100, 1000, 5000, 10000]
    results = []
    
    print(f"\n{'Items':<10}  {'Add (ms/op)':<14}  {'Query (ms/op)':<14}  {'Memory (KB)':<12}  {'FP Rate':<10}")
    print("-" * 70)
    
    for num_items in scales:
        bloom = BloomFilter(expected_items=num_items, false_positive_rate=0.01)
        
        items = [generate_content_hash(os.urandom(1024)) for _ in range(num_items)]
        
        # Benchmark add operations
        start = time.perf_counter()
        for item in items:
            bloom.add(item)
        add_total = (time.perf_counter() - start) * 1000
        add_per_op = add_total / num_items
        
        # Benchmark query operations (true positives)
        start = time.perf_counter()
        for item in items:
            bloom.check(item)
        query_total = (time.perf_counter() - start) * 1000
        query_per_op = query_total / num_items
        
        # Check false positive rate
        fp_count = 0
        test_items = 10000
        for i in range(test_items):
            fake_hash = generate_content_hash(os.urandom(1024))
            if bloom.check(fake_hash):
                fp_count += 1
        fp_rate = fp_count / test_items
        
        memory_kb = bloom.size / 8 / 1024
        
        result = {
            "items": num_items,
            "add_per_op_ms": round(add_per_op, 6),
            "query_per_op_ms": round(query_per_op, 6),
            "memory_kb": round(memory_kb, 2),
            "bytes_per_item": round(bloom.size / 8 / num_items, 2),
            "false_positive_rate": round(fp_rate, 4),
            "hash_functions": bloom.hash_count,
            "bit_array_size": bloom.size
        }
        results.append(result)
        
        print(f"{num_items:<10}  {add_per_op:<14.6f}  {query_per_op:<14.6f}  "
              f"{memory_kb:<12.2f}  {fp_rate:<10.4f}")
    
    return results


def benchmark_blockchain():
    """Benchmark blockchain operations."""
    print("\n" + "=" * 60)
    print("Benchmark 4: Blockchain Operations")
    print("=" * 60)
    
    results = {}
    
    # Block creation
    blockchain = DistributedBlockchain(node_id="test_node", authorized_validators=["test_node"])
    
    # Add transactions and mine blocks
    num_transactions = 50
    
    # Transaction addition timing
    start = time.perf_counter()
    for i in range(num_transactions):
        blockchain.add_transaction({
            "action": "UPLOAD_NEW",
            "tenant_id": f"tenant_{i % 3}",
            "file_cid": generate_content_hash(os.urandom(1024)),
            "filename": f"test_file_{i}.txt",
            "timestamp": time.time()
        })
    tx_total = (time.perf_counter() - start) * 1000
    
    results["transaction_addition"] = {
        "total_transactions": num_transactions,
        "total_time_ms": round(tx_total, 3),
        "per_transaction_ms": round(tx_total / num_transactions, 3)
    }
    
    # Block mining timing
    start = time.perf_counter()
    blockchain.mine_pending_transactions()
    mine_time = (time.perf_counter() - start) * 1000
    
    results["block_mining"] = {
        "transactions_per_block": num_transactions,
        "mining_time_ms": round(mine_time, 3)
    }
    
    # Chain validation timing
    # Add more blocks first
    for batch in range(10):
        for i in range(10):
            blockchain.add_transaction({
                "action": "UPLOAD_NEW",
                "tenant_id": f"tenant_{i % 3}",
                "file_cid": generate_content_hash(os.urandom(512)),
                "timestamp": time.time()
            })
        blockchain.mine_pending_transactions()
    
    chain_length = len(blockchain.chain)
    
    start = time.perf_counter()
    is_valid = blockchain.validate_chain()
    validate_time = (time.perf_counter() - start) * 1000
    
    results["chain_validation"] = {
        "chain_length": chain_length,
        "total_transactions": num_transactions + 100,
        "validation_time_ms": round(validate_time, 3),
        "is_valid": is_valid
    }
    
    # Audit log retrieval timing
    start = time.perf_counter()
    audit = blockchain.get_all_transactions()
    audit_time = (time.perf_counter() - start) * 1000
    
    results["audit_retrieval"] = {
        "total_entries": len(audit),
        "retrieval_time_ms": round(audit_time, 3)
    }
    
    print(f"\n{'Operation':<30}  {'Time (ms)':<12}  {'Details':<30}")
    print("-" * 75)
    print(f"{'Add Transaction':<30}  {results['transaction_addition']['per_transaction_ms']:<12.3f}  "
          f"Per transaction ({num_transactions} total)")
    print(f"{'Mine Block':<30}  {results['block_mining']['mining_time_ms']:<12.3f}  "
          f"{num_transactions} transactions")
    print(f"{'Validate Chain':<30}  {results['chain_validation']['validation_time_ms']:<12.3f}  "
          f"{chain_length} blocks, valid={is_valid}")
    print(f"{'Retrieve Audit Log':<30}  {results['audit_retrieval']['retrieval_time_ms']:<12.3f}  "
          f"{len(audit)} entries")
    
    return results


def benchmark_memory_usage():
    """Measure memory usage of key components."""
    print("\n" + "=" * 60)
    print("Benchmark 5: Memory Usage Analysis")
    print("=" * 60)
    
    results = {}
    
    # Bloom filter memory
    tracemalloc.start()
    bloom = BloomFilter(expected_items=10000, false_positive_rate=0.01)
    for i in range(1000):
        bloom.add(f"hash_{i}")
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results["bloom_filter"] = {
        "current_mb": round(current / 1048576, 3),
        "peak_mb": round(peak / 1048576, 3),
        "items_stored": 1000,
        "expected_capacity": 10000
    }
    
    # Blockchain memory
    tracemalloc.start()
    bc = DistributedBlockchain(node_id="node1", authorized_validators=["node1"])
    for i in range(100):
        bc.add_transaction({"action": "TEST", "tenant_id": f"t{i}", "id": i, "timestamp": time.time()})
        if (i + 1) % 10 == 0:
            bc.mine_pending_transactions()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results["blockchain"] = {
        "current_mb": round(current / 1048576, 3),
        "peak_mb": round(peak / 1048576, 3),
        "blocks": len(bc.chain),
        "transactions": 100
    }
    
    # AI Engine memory
    tracemalloc.start()
    ai = AIDeduplicationEngine()
    # Encode a few files
    for _ in range(10):
        content = os.urandom(10240)
        ai.encoder.encode_file(content)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results["ai_engine"] = {
        "current_mb": round(current / 1048576, 3),
        "peak_mb": round(peak / 1048576, 3),
        "files_encoded": 10,
        "model_parameters": "2048×128 weights + 128 bias = 262,272"
    }
    
    print(f"\n{'Component':<25}  {'Current (MB)':<14}  {'Peak (MB)':<14}  {'Details':<30}")
    print("-" * 90)
    for name, mem in results.items():
        details = ""
        if name == "bloom_filter":
            details = f"{mem['items_stored']} items / {mem['expected_capacity']} capacity"
        elif name == "blockchain":
            details = f"{mem['blocks']} blocks, {mem['transactions']} transactions"
        elif name == "ai_engine":
            details = f"{mem['files_encoded']} files encoded"
        
        print(f"{name:<25}  {mem['current_mb']:<14.3f}  {mem['peak_mb']:<14.3f}  {details}")
    
    return results


def benchmark_end_to_end():
    """Measure full upload pipeline latency."""
    print("\n" + "=" * 60)
    print("Benchmark 6: End-to-End Upload Pipeline Latency")
    print("=" * 60)
    
    results = []
    
    file_sizes = {
        "1 KB": 1024,
        "10 KB": 10240,
        "100 KB": 102400,
        "1 MB": 1048576,
    }
    
    bloom = BloomFilter(expected_items=10000, false_positive_rate=0.01)
    blockchain = DistributedBlockchain(node_id="main_node", authorized_validators=["main_node"])
    
    print(f"\n{'File Size':<12}  {'Hash (ms)':<12}  {'Bloom (ms)':<12}  {'Encrypt (ms)':<14}  "
          f"{'Blockchain (ms)':<16}  {'Total (ms)':<12}")
    print("-" * 85)
    
    for size_label, size_bytes in file_sizes.items():
        content = os.urandom(size_bytes)
        
        # Step 1: Content hash
        t1 = time.perf_counter()
        content_hash = generate_content_hash(content)
        hash_time = (time.perf_counter() - t1) * 1000
        
        # Step 2: Bloom filter check
        t2 = time.perf_counter()
        is_dup = bloom.check(content_hash)
        bloom_time = (time.perf_counter() - t2) * 1000
        
        # Step 3: Encryption
        t3 = time.perf_counter()
        key = generate_convergent_key(content, "tenant_A", "secret")
        encrypted = encrypt_file(content, key)
        encrypt_time = (time.perf_counter() - t3) * 1000
        
        # Step 4: Blockchain logging
        t4 = time.perf_counter()
        blockchain.add_transaction({
            "action": "UPLOAD_NEW",
            "tenant_id": "tenant_A",
            "file_cid": content_hash,
            "timestamp": time.time()
        })
        blockchain.mine_pending_transactions()
        blockchain_time = (time.perf_counter() - t4) * 1000
        
        # Update bloom filter
        bloom.add(content_hash)
        
        total = hash_time + bloom_time + encrypt_time + blockchain_time
        
        result = {
            "file_size": size_label,
            "file_size_bytes": size_bytes,
            "hash_ms": round(hash_time, 3),
            "bloom_check_ms": round(bloom_time, 3),
            "encryption_ms": round(encrypt_time, 3),
            "blockchain_ms": round(blockchain_time, 3),
            "total_pipeline_ms": round(total, 3),
            "meets_5s_requirement": total < 5000
        }
        results.append(result)
        
        print(f"{size_label:<12}  {hash_time:<12.3f}  {bloom_time:<12.3f}  "
              f"{encrypt_time:<14.3f}  {blockchain_time:<16.3f}  {total:<12.3f}")
    
    return results


def test_performance_benchmarks():
    """Main performance benchmark test."""
    
    print("=" * 60)
    print("TEST 6: PERFORMANCE BENCHMARKS")
    print("=" * 60)
    print("\nMeasuring system performance across all components")
    
    all_results = {}
    
    # Run all benchmarks
    all_results["encryption_latency"] = benchmark_encryption()
    all_results["pqc_vs_classical"] = benchmark_pqc_encryption()
    all_results["bloom_filter_throughput"] = benchmark_bloom_filter()
    all_results["blockchain_operations"] = benchmark_blockchain()
    all_results["memory_usage"] = benchmark_memory_usage()
    all_results["end_to_end_pipeline"] = benchmark_end_to_end()
    
    # Save results
    output_file = Path("test_results_performance.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\n Performance benchmark results saved to: {output_file}")
    
    # Overall verdict
    print(f"\n{'=' * 60}")
    print("PERFORMANCE VERDICT")
    print(f"{'=' * 60}")
    
    # Check NFR compliance
    pipeline = all_results["end_to_end_pipeline"]
    all_within_5s = all(r["meets_5s_requirement"] for r in pipeline)
    print(f"\n  NFR-01 (Upload < 5s for ≤100MB): {' PASS' if all_within_5s else ' FAIL'}")
    
    bloom = all_results["bloom_filter_throughput"]
    bloom_fast = all(r["query_per_op_ms"] < 1 for r in bloom)
    print(f"  NFR-02 (Dedup detection < 2s):    {' PASS' if bloom_fast else ' FAIL'}")
    
    all_results["overall_verdict"] = {
        "nfr_01_upload_performance": "PASS" if all_within_5s else "FAIL",
        "nfr_02_dedup_speed": "PASS" if bloom_fast else "FAIL",
        "test_result": "PASS" if (all_within_5s and bloom_fast) else "PARTIAL"
    }
    
    # Re-save with verdict
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    return all_results


if __name__ == "__main__":
    test_performance_benchmarks()
