let currentTask = null;
let uploadedPapers = {}; // Store papers per session

const taskConfig = {
    'summarize': { name: 'Summarize', maxPapers: 1, type: 'single' },
    'qa': { name: 'Intelligent Q&A', maxPapers: 1, type: 'single' },
    'gaps': { name: 'Gap Detection', maxPapers: 1, type: 'single' },
    'trends': { name: 'Trend Mapping', maxPapers: 1, type: 'single' },
    'graph': { name: 'Knowledge Graph', maxPapers: 1, type: 'single' },
    'compare': { name: 'Compare Papers', maxPapers: 2, type: 'dual' }
};

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupAllUploads();
    setupActionButtons();
});

function setupActionButtons() {
    // 1. Summarize
    const btnSummarize = document.getElementById('btn-generate-summary');
    if (btnSummarize) {
        btnSummarize.addEventListener('click', async () => {
            if (!uploadedPapers.single) return alert("Please upload a paper first.");

            const summaryOutput = document.querySelector('.summary-output');
            if (summaryOutput) {
                summaryOutput.innerHTML = '<div class="skeleton-text">AI Agent is analyzing the paper... This might take a minute.</div>';
            }

            try {
                const result = await window.getPaperSummary(uploadedPapers.single);
                if (summaryOutput) {
                    // Using a simple marked-like approach or just setting content if we don't have a library
                    // For now, let's just set it. If marked is available, we'd use marked.parse(result.summary)
                    // Given the prompt, let's assume we might need a simple markdown renderer or just display it cleanly.
                    // The CSS already handles line breaks with line-height, but we should handle markdown.
                    // Let's check if marked is available in base.html
                    summaryOutput.innerHTML = formatMarkdown(result.summary);
                }
            } catch (error) {
                if (summaryOutput) {
                    summaryOutput.innerHTML = '<div class="error-message">Failed to generate summary. Please try again.</div>';
                }
            }
        });
    }

    // 2. Compare
    const btnCompare = document.getElementById('btn-compare-papers');
    if (btnCompare) {
        btnCompare.addEventListener('click', () => {
            if (!uploadedPapers.paperA || !uploadedPapers.paperB) return alert("Please upload both papers first.");
            console.log("Comparing:", uploadedPapers.paperA, "vs", uploadedPapers.paperB);
            alert("Comparing " + uploadedPapers.paperA + " vs " + uploadedPapers.paperB + "...");
        });
    }

    // 3. Gaps
    const btnGaps = document.getElementById('btn-detect-gaps');
    if (btnGaps) {
        btnGaps.addEventListener('click', () => {
            if (!uploadedPapers.single) return alert("Please upload a paper first.");
            alert("Detecting research gaps...");
        });
    }

    // 4. Trends
    const btnTrends = document.getElementById('btn-map-trends');
    if (btnTrends) {
        btnTrends.addEventListener('click', () => {
            if (!uploadedPapers.single) return alert("Please upload a paper first.");
            alert("Mapping literature trends...");
        });
    }

    // 5. QA
    const btnQA = document.getElementById('btn-start-qa');
    if (btnQA) {
        btnQA.addEventListener('click', () => {
            if (!uploadedPapers.single) return alert("Please upload a paper first.");
            alert("Starting Q&A session...");
        });
    }

    // 6. Graph
    const btnGraph = document.getElementById('btn-generate-graph');
    if (btnGraph) {
        btnGraph.addEventListener('click', () => {
            if (!uploadedPapers.single) return alert("Please upload a paper first.");
            alert("Generating knowledge graph...");
        });
    }
}

// Navigation: Dashboard cards -> Feature Views
function selectTask(task) {
    currentTask = task;
    uploadedPapers = {}; // Reset session state on task switch

    // Deactivate all sections
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    // Activate target section
    const targetSection = document.getElementById(task);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Activate sidebar nav if applicable
    const navItem = document.querySelector(`.nav-item[data-tab="${task}"]`);
    if (navItem) navItem.classList.add('active');

    if (task === 'trends') initTrendChart();
    if (task === 'graph') initNetworkGraph();

    // Clear global list (though we might not see it on feature pages)
    clearPaperList();
}

function resetTaskSelection() {
    // Go back to dashboard
    currentTask = null;
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.getElementById('dashboard').classList.add('active');

    // Reset sidebar
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelector('.nav-item[data-tab="dashboard"]').classList.add('active');
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');

            if (tabId === 'dashboard') {
                resetTaskSelection();
            } else {
                selectTask(tabId);
            }
        });
    });
}

// Upload Initialization
function setupAllUploads() {
    // 1. Setup Single Uploads
    const singleTasks = ['summarize', 'qa', 'gaps', 'trends', 'graph'];
    singleTasks.forEach(task => {
        const dropZone = document.getElementById(`drop-zone-${task}`);
        const fileInput = document.getElementById(`file-input-${task}`);
        if (dropZone && fileInput) {
            setupDragDrop(dropZone, fileInput, (files) => handleFiles(files, task, 'single'));
        }
    });

    // 2. Setup Compare Uploads
    const dropZoneA = document.getElementById('drop-zone-a');
    const fileInputA = document.getElementById('file-input-a');
    if (dropZoneA && fileInputA) {
        setupDragDrop(dropZoneA, fileInputA, (files) => handleFiles(files, 'compare', 'paperA'));
    }

    const dropZoneB = document.getElementById('drop-zone-b');
    const fileInputB = document.getElementById('file-input-b');
    if (dropZoneB && fileInputB) {
        setupDragDrop(dropZoneB, fileInputB, (files) => handleFiles(files, 'compare', 'paperB'));
    }
}

function setupDragDrop(area, input, callback) {
    if (!area) return;

    area.onclick = () => input.click();
    input.onchange = (e) => callback(e.target.files);

    area.ondragover = (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--primary)';
        area.style.background = 'rgba(14, 165, 233, 0.1)';
    };

    area.ondragleave = (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--border)';
        area.style.background = 'transparent';
    };

    area.ondrop = (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--border)';
        area.style.background = 'transparent';
        callback(e.dataTransfer.files);
    };
}

function handleFiles(files, taskContext, source) {
    const validFiles = [];

    // Validate
    for (const file of files) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError("This summarizer accepts only valid pdf");
            return;
        }
        validFiles.push(file);
    }
    if (validFiles.length === 0) return;

    // Strict Checks
    if (source === 'single' && validFiles.length > 1) {
        showError("Please upload only 1 paper.");
        return;
    }

    hideError();

    // Update UI (Dropzone text) to show success
    if (source === 'single') {
        const dropZone = document.getElementById(`drop-zone-${taskContext}`);
        if (dropZone) {
            dropZone.querySelector('p').innerHTML = `<i class="fa-solid fa-file-circle-check" style="color: var(--secondary); font-size: 1.5rem;"></i><br><span style="color: white; font-weight: 600;">${validFiles[0].name}</span><br><span style="font-size: 0.8rem; color: var(--text-muted);">Ready to analyze</span>`;
            dropZone.style.borderColor = 'var(--secondary)';
            dropZone.style.background = 'rgba(139, 92, 246, 0.1)';
        }

        // Also update the status bar if it exists (e.g. in Summarize view)
        const statusEl = document.getElementById(`file-status-${taskContext}`);
        if (statusEl) {
            statusEl.innerHTML = `
                <div class="glass-panel" style="padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.8rem; border: 1px solid var(--secondary);">
                    <i class="fa-solid fa-file-pdf" style="color: var(--primary);"></i>
                    <span>${validFiles[0].name}</span>
                </div>
            `;
        }

    } else if (source === 'paperA') {
        document.getElementById('label-a').innerHTML = `<i class="fa-solid fa-check" style="color: var(--secondary);"></i> ${validFiles[0].name}`;
        document.getElementById('drop-zone-a').style.borderColor = 'var(--secondary)';
    } else if (source === 'paperB') {
        document.getElementById('label-b').innerHTML = `<i class="fa-solid fa-check" style="color: var(--secondary);"></i> ${validFiles[0].name}`;
        document.getElementById('drop-zone-b').style.borderColor = 'var(--secondary)';
    }

    // Call API (auto-clears list for single, appends for dual maybe? - strictly 1 for single)
    // Actually for 'single' page uploads, we always strictly replace.
    const shouldClear = (source === 'single');

    if (source === 'single') {
        uploadedPapers.single = validFiles[0].name;
    } else if (source === 'paperA') {
        uploadedPapers.paperA = validFiles[0].name;
    } else if (source === 'paperB') {
        uploadedPapers.paperB = validFiles[0].name;
    }

    // If compare, we don't clear unless we want to reset A/B state, but user might upload A then B.
    // So for compare, we append.
    uploadPapers(validFiles, shouldClear);
}

// Simple Markdown Formatter
function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function showError(msg) {
    const el = document.getElementById('upload-error');
    if (el) {
        el.querySelector('span').innerText = msg;
        el.classList.remove('hidden');
        el.style.display = 'flex';
        setTimeout(() => hideError(), 3000); // Auto-hide after 3s
    }
}

function hideError() {
    const el = document.getElementById('upload-error');
    if (el) {
        el.classList.add('hidden');
        el.style.display = 'none';
    }
}

function clearPaperList() {
    const grid = document.querySelector('.papers-grid');
    if (grid) {
        grid.innerHTML = `
            <div class="paper-card empty-state">
                <p>No papers uploaded yet.</p>
            </div>
        `;
    }
}

window.selectTask = selectTask;
window.resetTaskSelection = resetTaskSelection;
window.initTrendChart = window.initTrendChart || function () { };
window.initNetworkGraph = window.initNetworkGraph || function () { };
