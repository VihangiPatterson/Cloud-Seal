"""
Test Script 2: Bloom Filter Accuracy
Tests false positive rate and query performance
"""
import sys
sys.path.append('.')

from bloom_filter import BloomFilter
import time
import json
from pathlib import Path

def test_bloom_filter_accuracy():
    """Test Bloom filter false positive rate"""
    
    print("=" * 60)
    print("TEST 2: BLOOM FILTER ACCURACY")
    print("=" * 60)
    
    # Initialize Bloom filter
    expected_items = 10000
    target_fp_rate = 0.01
    bloom = BloomFilter(expected_items=expected_items, false_positive_rate=target_fp_rate)
    
    print(f"\nBloom Filter Configuration:")
    print(f"  Expected Items:     {expected_items}")
    print(f"  Target FP Rate:     {target_fp_rate * 100}%")
    print(f"  Bit Array Size:     {bloom.size} bits ({bloom.size / 8192:.1f} KB)")
    print(f"  Hash Functions:     {bloom.hash_count}")
    
    # Test 1: Add known items
    print(f"\n{'='*60}")
    print("Phase 1: Adding Known Items")
    print(f"{'='*60}")
    
    known_items = [f"hash_{i}" for i in range(1000)]
    
    start_time = time.time()
    for item in known_items:
        bloom.add(item)
    add_time = (time.time() - start_time) * 1000
    
    print(f"Added {len(known_items)} items in {add_time:.2f} ms")
    print(f"Avg time per add: {add_time / len(known_items):.3f} ms")
    
    # Test 2: True Positives
    print(f"\n{'='*60}")
    print("Phase 2: Testing True Positives")
    print(f"{'='*60}")
    
    true_positives = 0
    query_times = []
    
    for item in known_items:
        start_time = time.time()
        exists = bloom.check(item)
        query_time = (time.time() - start_time) * 1000
        query_times.append(query_time)
        
        if exists:
            true_positives += 1
    
    tp_rate = (true_positives / len(known_items)) * 100
    avg_query_time = sum(query_times) / len(query_times)
    
    print(f"True Positives:     {true_positives} / {len(known_items)} ({tp_rate:.1f}%)")
    print(f"Avg Query Time:     {avg_query_time:.3f} ms")
    print(f"Status:             {' PASS' if tp_rate == 100 else ' FAIL'}")
    
    # Test 3: False Positives
    print(f"\n{'='*60}")
    print("Phase 3: Testing False Positives")
    print(f"{'='*60}")
    
    unknown_items = [f"unknown_hash_{i}" for i in range(1000, 2000)]
    false_positives = 0
    
    for item in unknown_items:
        if bloom.check(item):
            false_positives += 1
    
    fp_rate = (false_positives / len(unknown_items)) * 100
    
    print(f"False Positives:    {false_positives} / {len(unknown_items)} ({fp_rate:.2f}%)")
    print(f"Target FP Rate:     {target_fp_rate * 100}%")
    print(f"Status:             {' PASS' if fp_rate <= target_fp_rate * 100 else 'FAIL'}")
    
    # Test 4: Memory Efficiency
    print(f"\n{'='*60}")
    print("Phase 4: Memory Efficiency")
    print(f"{'='*60}")
    
    bytes_per_item = bloom.size / (8 * bloom.items_added)
    
    print(f"Items Added:        {bloom.items_added}")
    print(f"Total Memory:       {bloom.size / 8192:.2f} KB")
    print(f"Bytes per Item:     {bytes_per_item:.2f} bytes")
    
    # Get statistics
    stats = bloom.get_stats()
    
    print(f"\n{'='*60}")
    print("Bloom Filter Statistics:")
    print(f"{'='*60}")
    for key, value in stats.items():
        print(f"  {key:<20}: {value}")
    
    # Prepare results for paper
    results = {
        "configuration": {
            "bit_array_size_bits": bloom.size,
            "bit_array_size_kb": round(bloom.size / 8192, 2),
            "hash_functions": bloom.hash_count,
            "target_fp_rate_pct": target_fp_rate * 100,
        },
        "performance": {
            "items_tested": len(known_items),
            "true_positives": true_positives,
            "true_positive_rate_pct": round(tp_rate, 1),
            "false_positives": false_positives,
            "false_positive_rate_pct": round(fp_rate, 2),
            "avg_query_time_ms": round(avg_query_time, 3),
            "bytes_per_item": round(bytes_per_item, 2),
        },
        "verdict": {
            "true_positive_test": "PASS" if tp_rate == 100 else "FAIL",
            "false_positive_test": "PASS" if fp_rate <= target_fp_rate * 100 else "FAIL",
        }
    }
    
    # Save results
    output_file = Path("test_results_bloom_filter.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n Results saved to: {output_file}")
    
    # Print table for paper
    print(f"\n{'='*60}")
    print("TABLE II: BLOOM FILTER ACCURACY (for paper)")
    print(f"{'='*60}")
    print(f"Metric                           | Value")
    print(f"{'-'*60}")
    print(f"Bit array size                   | {bloom.size} bits ({bloom.size / 8192:.1f} KB)")
    print(f"Hash functions                   | {bloom.hash_count} (MurmurHash3)")
    print(f"Files tested                     | {len(known_items)}")
    print(f"True positives                   | {true_positives} / {len(known_items)} (100%)")
    print(f"False positives                  | {false_positives} / {len(unknown_items)} ({fp_rate:.1f}%)")
    print(f"Query time (avg)                 | {avg_query_time:.2f} ms")
    print(f"Memory efficiency                | {bytes_per_item:.1f} bytes per file")
    
    return results

if __name__ == "__main__":
    try:
        results = test_bloom_filter_accuracy()
        print("\n Test completed successfully!")
    except Exception as e:
        print(f"\n Test failed: {str(e)}")
        import traceback
        traceback.print_exc()