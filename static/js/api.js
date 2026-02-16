async function uploadPapers(files, shouldClear = false) {
    const formData = new FormData();
    // No grid to update anymore

    // 1. Client-side Validation (Redundant checks but safe to keep)
    let validFilesCount = 0;
    for (const file of files) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            continue;
        }
        formData.append('files', file);
        validFilesCount++;
    }

    if (validFilesCount === 0) return;

    try {
        // Send to backend
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const result = await response.json();

        if (result.status === 'success') {
            console.log('Upload success:', result.files);
            // Optional: You could trigger a toast here if wanted
        } else {
            alert('Upload failed: ' + result.message);
        }
    } catch (error) {
        console.error('Error uploading:', error);
        alert('An error occurred during upload.');
    }
}

function clearPaperList() {
    // No-op since list is removed
}

async function getPaperSummary(paperId) {
    try {
        const response = await fetch(`/api/summary/${encodeURIComponent(paperId)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching summary:', error);
        throw error;
    }
}

window.uploadPapers = uploadPapers;
window.clearPaperList = clearPaperList;
window.getPaperSummary = getPaperSummary;
