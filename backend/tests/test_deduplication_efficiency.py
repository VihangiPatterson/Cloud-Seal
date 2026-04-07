"""
Test Script 1: Deduplication Efficiency
Measures storage savings across different duplicate rates
"""
import sys
import os
sys.path.append('.')

import time
import json
from pathlib import Path
import random
import string
import io

# Import app components directly for testing
from encryption import generate_content_hash
from bloom_filter import BloomFilter
from reference_counter import ReferenceCounter

# Initialize components for testing
bloom = BloomFilter()
ref_counter = ReferenceCounter(Path("data/test_refcounts.json"))

def generate_test_file(size_kb, content_id):
    """Generate test file with specific content"""
    # Create deterministic content based on content_id
    random.seed(content_id)
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=size_kb * 1024))
    return content.encode()

def test_deduplication_efficiency():
    """Test storage efficiency with controlled duplicate rates"""
    
    print("=" * 60)
    print("TEST 1: DEDUPLICATION EFFICIENCY")
    print("=" * 60)
    
    results = []
    
    # Test scenarios with different duplicate rates
    scenarios = [
        {"name": "20% Duplicates", "total_files": 100, "unique_files": 80},
        {"name": "40% Duplicates", "total_files": 100, "unique_files": 60},
        {"name": "60% Duplicates", "total_files": 100, "unique_files": 40},
        {"name": "80% Duplicates", "total_files": 100, "unique_files": 20},
    ]
    
    for scenario in scenarios:
        # Reset state for each scenario
        global bloom, ref_counter
        bloom = BloomFilter()
        ref_counter = ReferenceCounter(None)  # Use in-memory only
        
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario['name']}")
        print(f"Total Files: {scenario['total_files']}")
        print(f"Unique Files: {scenario['unique_files']}")
        print(f"{'='*60}")
        
        # Reset system (in production, you'd clear the database)
        # For now, use unique tenant ID per scenario
        tenant_id = f"test_tenant_{scenario['name'].replace(' ', '_')}"
        
        total_uploaded = 0
        unique_stored = 0
        duplicate_detected = 0
        total_response_time = 0
        
        # Generate unique file contents
        unique_contents = []
        for i in range(scenario['unique_files']):
            content = generate_test_file(size_kb=10, content_id=i)
            unique_contents.append(content)
        
        # Upload files (with duplicates)
        upload_count = 0
        for i in range(scenario['total_files']):
            # Pick content (creates duplicates)
            content_idx = i % scenario['unique_files']
            file_content = unique_contents[content_idx]
            
            # Simulate upload with direct component testing
            start_time = time.time()
            try:
                # Generate content hash
                content_hash = generate_content_hash(file_content)
                
                # Check bloom filter
                maybe_duplicate = bloom.check(content_hash)
                
                # Check reference counter
                status = ref_counter.add_reference(
                    content_hash,
                    tenant_id,
                    f'test_file_{i}.txt'
                )
                
                elapsed = (time.time() - start_time) * 1000  # Convert to ms
                total_response_time += elapsed
                total_uploaded += 1
                
                if status == "NEW":
                    # First upload - add to bloom filter
                    bloom.add(content_hash)
                    unique_stored += 1
                    print(f"  File {i+1}: NEW (CID: {content_hash[:16]}...) - {elapsed:.1f}ms")
                else:
                    # Duplicate
                    duplicate_detected += 1
                    print(f"  File {i+1}: DUPLICATE (CID: {content_hash[:16]}...) - {elapsed:.1f}ms")
            
            except Exception as e:
                print(f"  File {i+1}: EXCEPTION - {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Calculate metrics
        expected_unique = scenario['unique_files']
        expected_duplicates = scenario['total_files'] - scenario['unique_files']
        duplicate_rate = scenario['total_files'] - scenario['unique_files']
        storage_reduction = (duplicate_detected / scenario['total_files']) * 100
        avg_response_time = total_response_time / total_uploaded if total_uploaded > 0 else 0
        
        # Verify results
        print(f"\n{'─'*60}")
        print("RESULTS:")
        print(f"{'─'*60}")
        print(f"Total Uploaded:        {total_uploaded}")
        print(f"Unique Stored:         {unique_stored} (Expected: {expected_unique})")
        print(f"Duplicates Detected:   {duplicate_detected} (Expected: {expected_duplicates})")
        print(f"Storage Reduction:     {storage_reduction:.1f}%")
        print(f"Avg Response Time:     {avg_response_time:.1f} ms")
        
        # Accuracy check
        accuracy = (unique_stored == expected_unique and duplicate_detected == expected_duplicates)
        print(f"Accuracy:              {' PASS' if accuracy else ' FAIL'}")
        
        results.append({
            "scenario": scenario['name'],
            "total_files": total_uploaded,
            "unique_files": unique_stored,
            "duplicates": duplicate_detected,
            "storage_reduction_pct": round(storage_reduction, 1),
            "avg_response_time_ms": round(avg_response_time, 1),
            "accuracy": "PASS" if accuracy else "FAIL"
        })
        
        time.sleep(1)  # Pause between scenarios
    
    # Summary table
    print(f"\n{'='*60}")
    print("SUMMARY TABLE (for paper)")
    print(f"{'='*60}")
    print(f"{'Scenario':<20} {'Total':<8} {'Unique':<8} {'Reduction':<12} {'Avg Time':<10}")
    print(f"{'-'*60}")
    for r in results:
        print(f"{r['scenario']:<20} {r['total_files']:<8} {r['unique_files']:<8} "
              f"{r['storage_reduction_pct']}%{'':<8} {r['avg_response_time_ms']} ms")
    
    # Save results to JSON
    output_file = Path("test_results_deduplication.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = test_deduplication_efficiency()
        print("\n Test completed successfully!")
    except Exception as e:
        print(f"\n Test failed: {str(e)}")
        import traceback
        traceback.print_exc()