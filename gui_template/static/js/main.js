// Main JavaScript - GUI Template System

// Global Variables
let currentFile = null;
let currentCategory = '';
let currentItem = '';

// Utility Functions
function showLoading(element) {
    element.classList.add('loading');
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
}

function hideLoading(element, originalText) {
    element.classList.remove('loading');
    element.innerHTML = originalText;
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// File Upload Functions
function openCamera() {
    const cameraInput = document.getElementById('cameraInput');
    if (cameraInput) {
        cameraInput.click();
    }
}

function clearPreview() {
    const previewArea = document.getElementById('previewArea');
    const fileInput = document.getElementById('fileInput');
    const cameraInput = document.getElementById('cameraInput');
    
    if (previewArea) previewArea.style.display = 'none';
    if (fileInput) fileInput.value = '';
    if (cameraInput) cameraInput.value = '';
    currentFile = null;
}

async function uploadFile(file, endpoint, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data
    Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key]);
    });
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('Upload failed: ' + error.message, 'danger');
        throw error;
    }
}

// Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Search and Filter Functions
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput ? searchInput.value.trim() : '';
    
    if (query) {
        // Implement search functionality
        console.log('Searching for:', query);
        // You can customize this based on your needs
    }
}

function applyFilters() {
    const filter1 = document.getElementById('filter1');
    const filter2 = document.getElementById('filter2');
    const dateFilter = document.getElementById('dateFilter');
    
    const filters = {
        category: filter1 ? filter1.value : '',
        status: filter2 ? filter2.value : '',
        date: dateFilter ? dateFilter.value : ''
    };
    
    console.log('Applying filters:', filters);
    // Implement filter functionality
}

// Modal Functions
function openModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function closeModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

function submitModalForm() {
    const form = document.getElementById('modalForm');
    if (form && validateForm(form)) {
        // Implement form submission
        console.log('Submitting modal form');
        closeModal('formModal');
    }
}

// Card Interaction Functions
function toggleCard(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.classList.toggle('expanded');
    }
}

function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Photo Gallery Functions
function openPhotoModal(photoUrl, photoTitle = 'Photo') {
    const modal = `
        <div class="modal fade" id="photoModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${photoTitle}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${photoUrl}" class="img-fluid" alt="${photoTitle}">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="downloadFile('${photoUrl}', '${photoTitle}')">
                            <i class="fas fa-download me-2"></i>Download
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('photoModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modal);
    
    // Show modal
    const photoModal = new bootstrap.Modal(document.getElementById('photoModal'));
    photoModal.show();
}

// Drag and Drop Functions
function initializeDragAndDrop() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
    });
}

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        showAlert('Please select an image file.', 'warning');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewImage = document.getElementById('previewImage');
        const previewArea = document.getElementById('previewArea');
        
        if (previewImage) {
            previewImage.src = e.target.result;
        }
        if (previewArea) {
            previewArea.style.display = 'block';
        }
        
        currentFile = file;
    };
    
    reader.readAsDataURL(file);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop
    initializeDragAndDrop();
    
    // File input change handlers
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Search input handler
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
});

// Export functions for use in other scripts
window.GUITemplate = {
    showAlert,
    showLoading,
    hideLoading,
    uploadFile,
    validateForm,
    openModal,
    closeModal,
    openPhotoModal,
    downloadFile,
    toggleCard
}; 