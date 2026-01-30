"""
Master Test Runner - Runs all tests and generates final report
"""
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

def run_test_script(script_name):
    """Run a test script and return success status"""
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Test {script_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Test {script_name} failed with error: {str(e)}")
        return False

def generate_final_report():
    """Generate comprehensive test report"""
    
    print(f"\n{'#'*70}")
    print("PMCD PoC - COMPREHENSIVE TEST REPORT")
    print(f"{'#'*70}\n")
    
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: PMCD (Privacy-Preserving Multi-Tenant Cloud Deduplication)")
    
    # Check if result files exist
    result_files = [
        "test_results_deduplication.json",
        "test_results_bloom_filter.json",
        "test_results_multitenant.json",
        "test_results_blockchain.json"
    ]
    
    all_results = {}
    
    for result_file in result_files:
        path = Path(result_file)
        if path.exists():
            with open(path, 'r') as f:
                test_name = result_file.replace("test_results_", "").replace(".json", "")
                all_results[test_name] = json.load(f)
    
    # Print summary
    print(f"\n{'='*70}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*70}\n")
    
    if "deduplication" in all_results:
        print("✅ Deduplication Efficiency Test - COMPLETED")
        dedup_results = all_results["deduplication"]
        if isinstance(dedup_results, list) and len(dedup_results) > 0:
            avg_reduction = sum(r['storage_reduction_pct'] for r in dedup_results) / len(dedup_results)
            print(f"   Average storage reduction: {avg_reduction:.1f}%")
    
    if "bloom_filter" in all_results:
        print("✅ Bloom Filter Accuracy Test - COMPLETED")
        bloom_results = all_results["bloom_filter"]
        if "performance" in bloom_results:
            fp_rate = bloom_results["performance"]["false_positive_rate_pct"]
            print(f"   False positive rate: {fp_rate}%")
    
    if "multitenant" in all_results:
        print("✅ Multi-Tenant Safety Test - COMPLETED")
        mt_results = all_results["multitenant"]
        if "overall_verdict" in mt_results:
            verdict = mt_results["overall_verdict"]["test_result"]
            print(f"   Test result: {verdict}")
    
    if "blockchain" in all_results:
        print("✅ Blockchain Integrity Test - COMPLETED")
        bc_results = all_results["blockchain"]
        if "overall_verdict" in bc_results:
            verdict = bc_results["overall_verdict"]
            print(f"   Test result: {verdict}")
    
    # Generate paper-ready tables
    print(f"\n{'='*70}")
    print("PAPER-READY RESULTS")
    print(f"{'='*70}\n")
    
    # Table I: Deduplication Efficiency
    if "deduplication" in all_results:
        print("TABLE I: DEDUPLICATION EFFICIENCY ACROSS DATASETS\n")
        print(f"{'Dataset':<25} | {'Total Files':<12} | {'Unique Files':<12} | {'Storage Reduction':<18} | {'Avg Response':<12}")
        print(f"{'-'*100}")
        
        for result in all_results["deduplication"]:
            print(f"{result['scenario']:<25} | {result['total_files']:<12} | {result['unique_files']:<12} | "
                  f"{result['storage_reduction_pct']}%{'':<15} | {result['avg_response_time_ms']} ms")
    
    # Table II: Bloom Filter
    if "bloom_filter" in all_results:
        print(f"\n\nTABLE II: BLOOM FILTER ACCURACY\n")
        bloom = all_results["bloom_filter"]
        print(f"{'Metric':<40} | {'Value':<20}")
        print(f"{'-'*65}")
        
        config = bloom.get("configuration", {})
        perf = bloom.get("performance", {})
        
        print(f"{'Bit array size':<40} | {config.get('bit_array_size_bits', 'N/A')} bits ({config.get('bit_array_size_kb', 'N/A')} KB)")
        print(f"{'Hash functions':<40} | {config.get('hash_functions', 'N/A')} (MurmurHash3)")
        print(f"{'Files tested':<40} | {perf.get('items_tested', 'N/A')}")
        print(f"{'True positives':<40} | {perf.get('true_positives', 'N/A')} / {perf.get('items_tested', 'N/A')} ({perf.get('true_positive_rate_pct', 'N/A')}%)")
        print(f"{'False positives':<40} | {perf.get('false_positives', 'N/A')} / {perf.get('items_tested', 'N/A')} ({perf.get('false_positive_rate_pct', 'N/A')}%)")
        print(f"{'Query time (avg)':<40} | {perf.get('avg_query_time_ms', 'N/A')} ms")
        print(f"{'Memory efficiency':<40} | {perf.get('bytes_per_item', 'N/A')} bytes per file")
    
    # Save comprehensive report
    comprehensive_report = {
        "generated_at": datetime.now().isoformat(),
        "test_results": all_results,
        "summary": {
            "total_tests_run": len(all_results),
            "all_tests_passed": all(
                result.get("overall_verdict", {}).get("test_result", "UNKNOWN") == "PASS" 
                if isinstance(result, dict) else True
                for result in all_results.values()
            )
        }
    }
    
    output_file = Path("comprehensive_test_report.json")
    with open(output_file, 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    print(f"\n\n✅ Comprehensive report saved to: {output_file}")

def main():
    """Main test execution"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         PMCD PoC - COMPREHENSIVE TEST SUITE                      ║
║   Privacy-Preserving Multi-Tenant Cloud Deduplication            ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    print("Starting comprehensive test suite...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # List of test scripts to run
    test_scripts = [
        "test_deduplication_efficiency.py",
        "test_bloom_filter_accuracy.py",
        "test_multitenant_safety.py",
        "test_blockchain_integrity.py"
    ]
    
    results = {}
    
    # Run each test
    for script in test_scripts:
        script_path = Path(script)
        if not script_path.exists():
            print(f"⚠️  Test script not found: {script}")
            results[script] = False
            continue
        
        success = run_test_script(script)
        results[script] = success
        
        if success:
            print(f"\n✅ {script} completed successfully")
        else:
            print(f"\n❌ {script} failed")
        
        time.sleep(2)  # Pause between tests
    
    # Generate final report
    time.sleep(1)
    generate_final_report()
    
    # Print final summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}\n")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"Total tests run:     {total_tests}")
    print(f"Tests passed:        {passed_tests}")
    print(f"Tests failed:        {total_tests - passed_tests}")
    print(f"Success rate:        {(passed_tests / total_tests * 100):.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Your PoC is validated!")
    else:
        print(f"\n⚠️  Some tests failed. Review the logs above.")
    
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()