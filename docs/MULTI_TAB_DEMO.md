# 🎭 Multi-Tab Simultaneous Upload Demo Script

## Purpose
Demonstrate Cloud Seal's multi-tenant isolation and concurrent deduplication capabilities by having 3 tenants upload the same file simultaneously in different browser tabs.

---

## Setup Instructions

### 1. Prepare Test File
Create a test file to upload (or use an existing one):
```bash
# Create a sample PDF-like file
echo "This is a confidential business report for multi-tenant testing." > test_document.txt
# Repeat content to make it larger
for i in {1..100}; do cat test_document.txt >> shared_file.pdf; done
```

### 2. Open 3 Browser Tabs
1. Open your Choreo URL in Chrome/Firefox
2. Press `Cmd+T` (Mac) or `Ctrl+T` (Windows) to open new tab
3. Paste the same URL
4. Repeat for a third tab

**Result:** You should have 3 tabs, all showing the Cloud Seal dashboard

---

## Demo Execution

### Phase 1: Setup Tenants (30 seconds)

**Tab 1:**
1. Select `Tenant A (Commercial)` from dropdown
2. Keep both checkboxes enabled (PQC + AI)
3. Click "Select File" and choose `shared_file.pdf`
4. **DO NOT CLICK UPLOAD YET**

**Tab 2:**
1. Select `Tenant B (Enterprise)` from dropdown
2. Keep both checkboxes enabled
3. Click "Select File" and choose the **SAME** `shared_file.pdf`
4. **DO NOT CLICK UPLOAD YET**

**Tab 3:**
1. Select `Tenant C (Public)` from dropdown
2. Keep both checkboxes enabled
3. Click "Select File" and choose the **SAME** `shared_file.pdf`
4. **DO NOT CLICK UPLOAD YET**

### Phase 2: Simultaneous Upload (5 seconds)

**IMPORTANT:** You need to click all 3 upload buttons as quickly as possible.

**Technique:**
1. Position your mouse over the "🚀 Start Secure Upload" button in Tab 1
2. Click it
3. Immediately switch to Tab 2 (Cmd+Tab or Ctrl+Tab)
4. Click upload
5. Immediately switch to Tab 3
6. Click upload

**Goal:** All 3 uploads should start within 1-2 seconds of each other

---

## Expected Results

### Tab 1 (Tenant A) - First to Complete
```
📊 Upload Result:

Status: ✅ NEW FILE
CID: QmXyZ123abc...
Encryption: AES-256 + Kyber-768
```

**Explanation:** Tenant A's upload completes first, so it's stored as a new file.

### Tab 2 (Tenant B) - Second to Complete
```
📊 Upload Result:

Status: 🔗 DEDUPLICATED
CID: QmXyZ123abc... (same as Tenant A!)
Encryption: AES-256 + Kyber-768

💾 Storage Saved: 512.00 KB
```

**Explanation:** Tenant B's file is detected as identical and linked to Tenant A's copy.

### Tab 3 (Tenant C) - Third to Complete
```
📊 Upload Result:

Status: 🔗 DEDUPLICATED
CID: QmXyZ123abc... (same as Tenant A!)
Encryption: AES-256 + Kyber-768

💾 Storage Saved: 512.00 KB
```

**Explanation:** Tenant C's file is also deduplicated.

---

## Verification Steps

### Check Dashboard Metrics

After all uploads complete, click "🔄 Refresh Dashboard" in any tab:

```
📊 Live System Status

📦 Blocks:        4 (or more)
📂 Total Files:   3
💎 Unique Files:  1
♻️ Dedup Ratio:   66.7%
```

**Key Metrics:**
- **Total Files: 3** → Three tenants uploaded files
- **Unique Files: 1** → Only one physical copy stored
- **Dedup Ratio: 66.7%** → Saved 2/3 of storage space

### Check Personal Vaults

**Tab 1 (Tenant A):**
Scroll to "📁 Personal Vault" section:
```
📄 File Name: shared_file.pdf
🔑 CID: QmXyZ123abc...
👥 Ref Count: 3
🏢 Owners: tenant_A, tenant_B, tenant_C
```

**Tab 2 (Tenant B):**
Same file appears in their vault with identical CID

**Tab 3 (Tenant C):**
Same file appears in their vault with identical CID

**Proof:** All three tenants "own" the file, but only one copy exists physically.

---

## Advanced Demo: Safe Deletion

### Demonstrate Tenant Isolation

**In Tab 1 (Tenant A):**
1. Scroll to "Personal Vault"
2. Click "🗑️ Delete" on the shared file
3. Confirm deletion

**Expected Result:**
```
✅ Reference removed. Remaining refs: 2
```

**In Tab 2 (Tenant B):**
1. Click "Refresh My Vault"
2. **File is still there!**

**Explanation:** Tenant A's deletion only removed their reference. The physical file remains because Tenant B and C still need it.

**In Tab 2 (Tenant B):**
1. Click "🗑️ Delete"
2. Confirm

**Expected Result:**
```
✅ Reference removed. Remaining refs: 1
```

**In Tab 3 (Tenant C):**
1. Click "🗑️ Delete" (last owner)
2. Confirm

**Expected Result:**
```
✅ File deleted permanently. Remaining refs: 0
```

**Final Verification:**
- Refresh Dashboard → **Total Files: 0**, **Unique Files: 0**
- All Personal Vaults are empty

---

## Key Points to Emphasize

### 1. **Concurrent Safety**
"Notice that even though all three tenants uploaded simultaneously, the system correctly identified the duplicates and only stored one copy."

### 2. **Cryptographic Isolation**
"Each tenant has their own encryption key. Even though they share the physical file, they cannot decrypt each other's data."

### 3. **Reference Counting**
"The system tracks ownership using a reference counter. The file is only deleted when the last owner removes it."

### 4. **Blockchain Audit**
Scroll to "🔍 Blockchain Ledger" and show:
```json
{
  "action": "UPLOAD",
  "tenant_id": "tenant_A",
  "file_cid": "QmXyZ123abc...",
  "timestamp": "2026-02-04T12:34:56"
}
```

"Every action is permanently recorded on the blockchain for compliance and forensics."

---

## Troubleshooting

### Issue: All 3 uploads show "NEW FILE"
**Cause:** Uploads were too far apart in time, or files are slightly different
**Solution:** 
- Ensure all 3 tabs are using the **exact same file**
- Try clicking upload buttons faster (within 1 second)

### Issue: Only 2 uploads deduplicated
**Cause:** Normal! The first upload to complete stores the file, the next two deduplicate
**Solution:** This is expected behavior

### Issue: Dashboard shows wrong numbers
**Cause:** Cache or timing issue
**Solution:** Click "🔄 Refresh Dashboard" button

---

## Summary

This demo proves:
✅ **Multi-tenant support** - 3 independent tenants  
✅ **Concurrent deduplication** - Simultaneous uploads handled correctly  
✅ **Storage efficiency** - 66.7% savings (1 file instead of 3)  
✅ **Safe deletion** - Reference counting prevents data loss  
✅ **Audit trail** - Blockchain records all actions  

**Impact:** In a real-world scenario with 1000 tenants uploading common files (contracts, reports, etc.), this system could save 80-90% of storage costs while maintaining perfect security isolation.
