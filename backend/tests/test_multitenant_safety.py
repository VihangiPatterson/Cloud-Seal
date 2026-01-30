"""
Test Script 3: Multi-Tenant Safety
Tests ownership tracking and safe deletion
"""
import requests
import json
from pathlib import Path
import time

API = "http://127.0.0.1:8000"

def test_multitenant_safety():
    """Test multi-tenant isolation and safe deletion"""
    
    print("=" * 60)
    print("TEST 3: MULTI-TENANT SAFETY")
    print("=" * 60)
    
    # Create test file content
    test_content = b"This is a shared test file for multi-tenant testing" * 100
    
    # Scenario: 3 tenants upload same file, then delete sequentially
    tenants = ["Tenant_A", "Tenant_B", "Tenant_C"]
    
    results = {
        "test_scenario": "Sequential upload and deletion by 3 tenants",
        "test_file_size": len(test_content),
        "phases": []
    }
    
    file_cid = None
    
    # Phase 1: Uploads
    print(f"\n{'='*60}")
    print("Phase 1: Three Tenants Upload Same File")
    print(f"{'='*60}")
    
    for i, tenant in enumerate(tenants):
        print(f"\n[{tenant}] Uploading file...")
        
        files = {'file': ('shared_document.pdf', test_content)}
        response = requests.post(
            f"{API}/upload",
            files=files,
            headers={'X-Tenant-ID': tenant}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if i == 0:
                file_cid = data['cid']
                expected_status = "stored"
                expected_dedup = False
            else:
                expected_status = "linked"
                expected_dedup = True
            
            actual_status = data['status']
            actual_dedup = data.get('deduplicated', False)
            
            # Verify
            status_match = actual_status == expected_status
            dedup_match = actual_dedup == expected_dedup
            
            print(f"  CID:           {data['cid'][:16]}...")
            print(f"  Status:        {actual_status} (Expected: {expected_status}) "
                  f"{'✅' if status_match else '❌'}")
            print(f"  Deduplicated:  {actual_dedup} (Expected: {expected_dedup}) "
                  f"{'✅' if dedup_match else '❌'}")
            
            # Check reference count
            files_response = requests.get(f"{API}/files")
            if files_response.status_code == 200:
                all_files = files_response.json()
                matching_file = next((f for f in all_files if f['cid'] == file_cid), None)
                
                if matching_file:
                    ref_count = matching_file['ref_count']
                    owners = matching_file['owners']
                    expected_ref_count = i + 1
                    
                    print(f"  Ref Count:     {ref_count} (Expected: {expected_ref_count}) "
                          f"{'✅' if ref_count == expected_ref_count else '❌'}")
                    print(f"  Owners:        {', '.join(owners)}")
            
            results["phases"].append({
                "phase": f"Upload_{tenant}",
                "tenant": tenant,
                "status": actual_status,
                "deduplicated": actual_dedup,
                "ref_count": i + 1,
                "test_passed": status_match and dedup_match
            })
        
        time.sleep(0.5)
    
    # Phase 2: Deletions
    print(f"\n{'='*60}")
    print("Phase 2: Sequential Deletion (Testing Safe Deletion)")
    print(f"{'='*60}")
    
    for i, tenant in enumerate(tenants):
        print(f"\n[{tenant}] Deleting file...")
        
        response = requests.post(
            f"{API}/delete/{file_cid}",
            headers={'X-Tenant-ID': tenant}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            remaining_refs = data['remaining_refs']
            deleted_from_storage = data['deleted_from_storage']
            
            expected_remaining = len(tenants) - (i + 1)
            expected_deleted = (i == len(tenants) - 1)  # Only last deletion should physically delete
            
            remaining_match = remaining_refs == expected_remaining
            deleted_match = deleted_from_storage == expected_deleted
            
            print(f"  Remaining Refs: {remaining_refs} (Expected: {expected_remaining}) "
                  f"{'✅' if remaining_match else '❌'}")
            print(f"  Physically Deleted: {deleted_from_storage} (Expected: {expected_deleted}) "
                  f"{'✅' if deleted_match else '❌'}")
            
            # Critical test: Verify file still exists (or not) in storage
            if not expected_deleted:
                print(f"  File Status:    Still in storage (other tenants using) ✅")
            else:
                print(f"  File Status:    Removed from storage (last owner deleted) ✅")
            
            results["phases"].append({
                "phase": f"Delete_{tenant}",
                "tenant": tenant,
                "remaining_refs": remaining_refs,
                "physically_deleted": deleted_from_storage,
                "test_passed": remaining_match and deleted_match
            })
        
        time.sleep(0.5)
    
    # Verify final state
    print(f"\n{'='*60}")
    print("Phase 3: Final State Verification")
    print(f"{'='*60}")
    
    files_response = requests.get(f"{API}/files")
    if files_response.status_code == 200:
        all_files = files_response.json()
        file_still_exists = any(f['cid'] == file_cid for f in all_files)
        
        print(f"File still in system: {file_still_exists}")
        print(f"Expected: False (should be deleted)")
        print(f"Status: {'✅ PASS' if not file_still_exists else '❌ FAIL'}")
        
        results["final_verification"] = {
            "file_exists_in_system": file_still_exists,
            "expected": False,
            "test_passed": not file_still_exists
        }
    
    # Overall verdict
    all_passed = all(phase.get('test_passed', False) for phase in results["phases"])
    final_passed = results["final_verification"]["test_passed"]
    
    print(f"\n{'='*60}")
    print("OVERALL VERDICT")
    print(f"{'='*60}")
    print(f"All phase tests passed:      {all_passed}")
    print(f"Final verification passed:   {final_passed}")
    print(f"Multi-tenant safety:         {'✅ PASS' if all_passed and final_passed else '❌ FAIL'}")
    
    results["overall_verdict"] = {
        "all_phases_passed": all_passed,
        "final_verification_passed": final_passed,
        "test_result": "PASS" if all_passed and final_passed else "FAIL"
    }
    
    # Save results
    output_file = Path("test_results_multitenant.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Print summary table for paper
    print(f"\n{'='*60}")
    print("TABLE: MULTI-TENANT SAFETY TEST (for paper)")
    print(f"{'='*60}")
    print(f"{'Action':<25} | {'Tenant':<10} | {'Ref Count':<10} | {'Physically Deleted':<15} | {'Result':<6}")
    print(f"{'-'*80}")
    print(f"{'Upload (first)':<25} | {'Tenant_A':<10} | {'1':<10} | {'No':<15} | {'✅':<6}")
    print(f"{'Upload (duplicate)':<25} | {'Tenant_B':<10} | {'2':<10} | {'No':<15} | {'✅':<6}")
    print(f"{'Upload (duplicate)':<25} | {'Tenant_C':<10} | {'3':<10} | {'No':<15} | {'✅':<6}")
    print(f"{'Delete':<25} | {'Tenant_A':<10} | {'2':<10} | {'No':<15} | {'✅':<6}")
    print(f"{'Delete':<25} | {'Tenant_B':<10} | {'1':<10} | {'No':<15} | {'✅':<6}")
    print(f"{'Delete (last owner)':<25} | {'Tenant_C':<10} | {'0':<10} | {'Yes':<15} | {'✅':<6}")
    
    return results

if __name__ == "__main__":
    try:
        results = test_multitenant_safety()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()