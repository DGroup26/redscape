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
    // Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    // Load cases if switching to cases tab
    if (tabName === 'cases') {
        loadCases();
    }
}

// Identity generation
let currentIdentity = null;

async function generateIdentity() {
    const btn = document.getElementById('generate-btn');
    const loading = document.getElementById('identity-loading');
    const result = document.getElementById('identity-result');
    
    btn.disabled = true;
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    
    try {
        const response = await fetch('/api/identity/generate');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        currentIdentity = data;
        
        // Populate the card
        document.getElementById('id-name').textContent = data.full_name;
        document.getElementById('id-occupation').textContent = data.occupation;
        document.getElementById('id-contact').textContent = `✉ ${data.email} | ☎ ${data.phone}`;
        document.getElementById('id-location').textContent = `⚲ ${data.city} | DOB: ${data.dob}`;
        
        document.getElementById('id-photo').src = `data:image/jpeg;base64,${data.image_b64}`;
        
        const edu = data.education;
        document.getElementById('id-education').textContent = `${edu.level} — ${edu.university} (${edu.grad_year})`;
        
        const skillsList = document.getElementById('id-skills');
        skillsList.innerHTML = data.skills.map(s => `<li>${s}</li>`).join('');
        
        const workDiv = document.getElementById('id-work');
        workDiv.innerHTML = data.work_history.map(job => `
            <div class="work-item">
                <div class="work-header">
                    <span class="work-title">${job.title}</span>
                    <span class="work-period">${job.period}</span>
                </div>
                <div class="work-company">${job.company}</div>
            </div>
        `).join('');
        
        loading.classList.add('hidden');
        result.classList.remove('hidden');
        
    } catch (error) {
        console.error('Failed to generate identity:', error);
        alert('Failed to generate identity: ' + error.message);
        loading.classList.add('hidden');
    } finally {
        btn.disabled = false;
    }
}

async function downloadPDF() {
    if (!currentIdentity) {
        alert('Generate an identity first');
        return;
    }
    
    try {
        const response = await fetch('/api/identity/pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(currentIdentity)
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `CV_${currentIdentity.full_name.replace(' ', '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('Failed to download PDF:', error);
        alert('Failed to download PDF: ' + error.message);
    }
}
});