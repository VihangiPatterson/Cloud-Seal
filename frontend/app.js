// Enhanced Cloud Seal Frontend JavaScript

const API = ""; // Empty string for relative paths (Hosting readiness)

// ===== System Status =====
async function loadSystemStatus(isManual = false) {
  const btn = document.querySelector('button[onclick="loadSystemStatus(true)"]');
  const originalText = "🔄 Refresh Dashboard";

  if (isManual && btn) btn.textContent = "⏳ Refreshing...";

  try {
    const res = await fetch(`${API}./system/status?t=${Date.now()}`, {
      cache: 'no-cache',
      headers: { 'Cache-Control': 'no-cache' }
    });
    const data = await res.json();

    // Update dashboard
    document.getElementById("blockCount").textContent = data.blockchain.chain_length;
    document.getElementById("totalFiles").textContent = data.storage.total_files;
    document.getElementById("uniqueFiles").textContent = data.storage.unique_files;
    document.getElementById("dedupRatio").textContent =
      (data.storage.deduplication_ratio * 100).toFixed(1) + "%";
    document.getElementById("aiStatus").textContent =
      data.ai.trained ? "✅ Trained" : "❌ Untrained";
    document.getElementById("pqcAlgo").textContent = data.pqc.algorithm;

  } catch (err) {
    console.error("Failed to load system status:", err);
  } finally {
    if (isManual && btn) btn.textContent = originalText;
  }
}

// ===== Upload with Advanced Options =====
async function upload() {
  const tenant = document.getElementById("tenantId").value;
  const file = document.getElementById("fileInput").files[0];
  const usePQC = document.getElementById("usePQC").checked;
  const useAI = document.getElementById("useAI").checked;

  if (!tenant || !file) {
    alert("❌ Tenant ID and file required");
    return;
  }

  const resultBox = document.getElementById("uploadResult");
  resultBox.textContent = "⏳ Uploading...";
  resultBox.className = "result-box loading";

  try {
    const form = new FormData();
    form.append("file", file);

    const queryParams = new URLSearchParams();
    if (usePQC) queryParams.append("use_pqc", "true");
    if (useAI) queryParams.append("use_ai", "true");

    const url = `${API}./upload?${queryParams.toString()}`;

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "X-Tenant-ID": tenant
      },
      body: form
    });

    const data = await res.json();

    // Format result with highlights
    let resultText = `📊 Upload Result:\n\n`;
    resultText += `Status: ${data.status === "stored" ? "✅ NEW FILE" : "🔗 DEDUPLICATED"}\n`;
    resultText += `CID: ${data.cid}\n`;

    if (data.encryption) {
      resultText += `Encryption: ${data.encryption}\n`;
    }

    if (data.ai_details) {
      resultText += `\n🤖 AI Detection Result:\n`;
      resultText += `  - Similar Content: ${data.ai_details.ai_detected ? "✅ YES" : "❌ NO"}\n`;
      if (data.ai_details.similarity_score) {
        resultText += `  - Confidence: ${(data.ai_details.similarity_score * 100).toFixed(2)}%\n`;
      }
    }

    if (data.storage_saved) {
      resultText += `\n💾 Storage Saved: ${(data.storage_saved / 1024).toFixed(2)} KB\n`;
    }

    resultBox.textContent = resultText;
    resultBox.className = data.deduplicated ? "result-box success" : "result-box";

    // Refresh file lists and status
    await loadFiles();
    await loadMyFiles();
    await loadSystemStatus(false);

  } catch (err) {
    const resultBox = document.getElementById("uploadResult");
    resultBox.textContent = `❌ Error: ${err.message}`;
    resultBox.className = "result-box error";
  }
}

// ===== Quantum-Safe File Sharing =====
async function shareFile() {
  const cid = document.getElementById("shareCID").value;
  const receiver = document.getElementById("receiverID").value;
  const sender = document.getElementById("tenantId").value;

  if (!cid || !receiver || !sender) {
    alert("❌ Please fill all fields (CID, Receiver ID, and your Tenant ID)");
    return;
  }

  const resultBox = document.getElementById("shareResult");
  resultBox.textContent = "⏳ Establishing quantum-safe connection...";
  resultBox.className = "result-box loading";

  try {
    const res = await fetch(`${API}./share?file_cid=${cid}`, {
      method: "POST",
      headers: {
        "X-Sender-ID": sender,
        "X-Receiver-ID": receiver
      }
    });

    const data = await res.json();

    let resultText = `🔐 Quantum-Safe Sharing Complete!\n\n`;
    resultText += `File CID: ${data.file_cid}\n`;
    resultText += `Shared with: ${data.receiver}\n`;
    resultText += `Quantum-Safe: ${data.quantum_safe ? "✅ YES" : "❌ NO"}\n`;
    resultText += `Encapsulated Key: ${data.encapsulated_key}\n`;

    resultBox.textContent = resultText;
    resultBox.className = "result-box success";

    await loadMyFiles();

  } catch (err) {
    const resultBox = document.getElementById("shareResult");
    resultBox.textContent = `❌ Error: ${err.message}`;
    resultBox.className = "result-box error";
  }
}

// ===== My Files =====
async function loadMyFiles() {
  const tenant = document.getElementById("tenantId").value;
  if (!tenant) {
    document.getElementById("myFiles").innerHTML =
      '<p style="color: #94a3b8;">Enter Tenant ID to view your files</p>';
    return;
  }

  try {
    const res = await fetch(`${API}./files/${tenant}`);
    const data = await res.json();

    const container = document.getElementById("myFiles");
    container.innerHTML = "";

    if (data.length === 0) {
      container.innerHTML = '<p style="color: #94a3b8;">No files owned by this tenant.</p>';
      return;
    }

    data.forEach(f => {
      const div = document.createElement("div");
      div.className = "file-item";

      const fileName = f.filenames && f.filenames[tenant]
        ? f.filenames[tenant]
        : "Unknown";

      div.innerHTML = `
        <p><strong>📄 File Name:</strong> ${fileName}</p>
        <p><strong>🔑 CID:</strong> <code>${f.cid.substring(0, 16)}...</code></p>
        <p><strong>👥 Ref Count:</strong> ${f.ref_count}</p>
        <p><strong>🏢 Owners:</strong> ${f.owners.join(", ")}</p>
        <button onclick="deleteFile('${f.cid}')">🗑️ Delete</button>
      `;

      container.appendChild(div);
    });

  } catch (err) {
    document.getElementById("myFiles").innerHTML =
      `<p class="error">❌ Error loading files: ${err.message}</p>`;
  }
}

// ===== Delete File =====
async function deleteFile(cid) {
  const tenant = document.getElementById("tenantId").value;

  if (!confirm(`Delete file ${cid.substring(0, 16)}...?`)) {
    return;
  }

  try {
    const res = await fetch(`${API}./delete/${cid}`, {
      method: "POST",
      headers: {
        "X-Tenant-ID": tenant
      }
    });

    const data = await res.json();

    const msg = data.deleted_from_storage
      ? `✅ File deleted permanently. Remaining refs: ${data.remaining_refs}`
      : `✅ Reference removed. Remaining refs: ${data.remaining_refs}`;

    alert(msg);

    await loadFiles();
    await loadMyFiles();
    await loadSystemStatus(false);

  } catch (err) {
    alert(`❌ Error: ${err.message}`);
  }
}

// ===== All Files =====
async function loadFiles() {
  try {
    const res = await fetch(`${API}./files`);
    const data = await res.json();
    document.getElementById("files").textContent =
      JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("files").textContent = `Error: ${err.message}`;
  }
}

// ===== Audit Log =====
async function loadAudit() {
  const filterMy = document.getElementById("filterMyAudit")?.checked;
  const tenant = document.getElementById("tenantId").value;

  try {
    let url = `${API}./audit`;
    if (filterMy && tenant) {
      url += `?tenant_id=${tenant}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    document.getElementById("audit").textContent =
      JSON.stringify(data, null, 2);

  } catch (err) {
    document.getElementById("audit").textContent = `Error: ${err.message}`;
  }
}

// ===== Blockchain Stats =====
async function loadBlockchainStats() {
  try {
    const res = await fetch(`${API}./blockchain/stats`);
    const data = await res.json();

    document.getElementById("blockchainStats").textContent =
      JSON.stringify(data, null, 2);

  } catch (err) {
    document.getElementById("blockchainStats").textContent = `Error: ${err.message}`;
  }
}

// ===== AI Training =====
async function trainAI() {
  const epochs = parseInt(document.getElementById("trainEpochs").value) || 20;

  const resultBox = document.getElementById("trainResult");
  resultBox.textContent = `⏳ Training AI model for ${epochs} epochs...\nThis may take a few minutes.`;
  resultBox.className = "result-box loading";

  try {
    const res = await fetch(`${API}./ai/train?epochs=${epochs}`, {
      method: "POST"
    });

    const data = await res.json();

    let resultText = `🧠 AI Training Complete!\n\n`;
    resultText += `Status: ${data.status}\n`;
    resultText += `Training Pairs: ${data.training_pairs}\n`;
    resultText += `Epochs: ${data.epochs}\n`;

    resultBox.textContent = resultText;
    resultBox.className = "result-box success";

    await loadSystemStatus(false);

  } catch (err) {
    const resultBox = document.getElementById("trainResult");
    resultBox.textContent = `❌ Error: ${err.message}`;
    resultBox.className = "result-box error";
  }
}

// ===== PQC Info =====
async function loadPQCInfo() {
  try {
    const res = await fetch(`${API}./pqc/info`);
    const data = await res.json();

    document.getElementById("pqcInfo").textContent =
      JSON.stringify(data, null, 2);

  } catch (err) {
    document.getElementById("pqcInfo").textContent = `Error: ${err.message}`;
  }
}

// ===== Tenant Change Handler =====
function onTenantChange() {
  loadMyFiles();
  loadAudit();
  loadSystemStatus(false);
  loadFiles();
  // Refresh advanced details if they were open/visible
  if (document.getElementById("blockchainStats").textContent !== "") loadBlockchainStats();
  if (document.getElementById("pqcInfo").textContent !== "") loadPQCInfo();
}

// ===== Auto-load on page load =====
window.addEventListener("DOMContentLoaded", () => {
  loadSystemStatus(false);
  loadFiles();
});

// ===== Auto-refresh status every 10 seconds =====
setInterval(() => {
  loadSystemStatus(false);
}, 10000);