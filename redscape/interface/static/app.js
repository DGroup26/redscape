/* Redscape Archive - Logic */

document.addEventListener('DOMContentLoaded', () => {
    loadCases();
    
    document.getElementById('back-btn').addEventListener('click', showCasesList);
});

async function loadCases() {
    try {
        const response = await fetch('/api/cases');
        const cases = await response.json();
        renderCases(cases);
    } catch (error) {
        console.error('Failed to load cases:', error);
        document.getElementById('cases-container').innerHTML = 
            '<p class="error">Failed to load archive.</p>';
    }
}

function renderCases(cases) {
    const container = document.getElementById('cases-container');
    
    if (cases.length === 0) {
        container.innerHTML = '<p class="loading">No cases in archive.</p>';
        return;
    }
    
    container.innerHTML = cases.map(c => `
        <div class="case-card" onclick="viewCase('${c.case_id}')">
            <h3>${c.case_id}</h3>
            <div class="target">${c.target}</div>
            <div class="timestamp">${c.timestamp}</div>
            <div class="pages">${c.pages} pages scraped</div>
        </div>
    `).join('');
}

async function viewCase(caseId) {
    try {
        const response = await fetch(`/api/case/${caseId}`);
        const data = await response.json();
        
        if (data.error) {
            alert('Case not found');
            return;
        }
        
        document.getElementById('cases-list').classList.add('hidden');
        document.getElementById('case-detail').classList.remove('hidden');
        
        document.getElementById('case-title').textContent = `Case: ${caseId}`;
        
        document.getElementById('case-info').innerHTML = `
            <p><strong>Target:</strong> ${data.target}</p>
            <p><strong>Timestamp:</strong> ${data.timestamp}</p>
            <p><strong>Pages:</strong> ${data.pages.length || data.pages}</p>
        `;
        
        const screenshotsDiv = document.getElementById('screenshots');
        if (data.screenshots && data.screenshots.length > 0) {
            screenshotsDiv.innerHTML = data.screenshots.map(s => `
                <div class="screenshot-item" onclick="openModal('/api/screenshot/${caseId}/${s}')">
                    <img src="/api/screenshot/${caseId}/${s}" alt="Screenshot">
                </div>
            `).join('');
        } else {
            screenshotsDiv.innerHTML = '<p>No screenshots available.</p>';
        }
        
    } catch (error) {
        console.error('Failed to load case:', error);
        alert('Failed to load case details');
    }
}

function showCasesList() {
    document.getElementById('case-detail').classList.add('hidden');
    document.getElementById('cases-list').classList.remove('hidden');
    loadCases();
}

function openModal(imageSrc) {
    const modal = document.getElementById('screenshot-modal');
    const img = document.getElementById('modal-image');
    img.src = imageSrc;
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('screenshot-modal');
    modal.classList.remove('active');
    document.getElementById('modal-image').src = '';
}

// Close modal on background click or Escape key
document.getElementById('screenshot-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});