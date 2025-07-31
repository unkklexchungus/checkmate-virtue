# CheckMate Virtue - GUI Template Example

This example shows how CheckMate Virtue uses the GUI template system.

## 🎯 Template Usage

### Base Template Extension
```html
<!-- templates/index.html -->
{% extends "base.html" %}

{% block title %}CheckMate Virtue - Professional Inspection System{% endblock %}

{% block content %}
<section class="hero-section">
    <div class="container text-center">
        <h1 class="display-4 mb-4">Professional Vehicle Inspection System</h1>
        <p class="lead mb-4">Comprehensive multi-point vehicle inspection with detailed reporting and photo documentation.</p>
        <a href="/inspections/new" class="btn btn-light btn-lg">
            <i class="fas fa-plus me-2"></i>
            Start New Inspection
        </a>
    </div>
</section>
{% endblock %}
```

### Custom Navigation
```html
<!-- Custom navbar for CheckMate Virtue -->
{% block nav_items %}
<li class="nav-item">
    <a class="nav-link" href="/inspections">Inspections</a>
</li>
<li class="nav-item">
    <a class="nav-link" href="/inspections/new">New Inspection</a>
</li>
{% endblock %}
```

### Card Components
```html
<!-- Using interactive cards for inspections -->
<div class="card interactive-card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">{{ inspection.title }}</h6>
        <span class="badge bg-{{ 'success' if inspection.status == 'completed' else 'warning' }} status-badge">
            {{ inspection.status.title() }}
        </span>
    </div>
    <div class="card-body">
        <div class="mb-2">
            <small class="text-muted">
                <i class="fas fa-calendar me-1"></i>
                {{ inspection.date.split('T')[0] if inspection.date else 'N/A' }}
            </small>
        </div>
        <div class="mb-3">
            <small class="text-muted">
                <i class="fas fa-user me-1"></i>
                {{ inspection.inspector_name }}
            </small>
        </div>
    </div>
    <div class="card-footer">
        <div class="d-flex justify-content-between">
            <a href="/inspections/{{ inspection.id }}" class="btn btn-outline-primary btn-sm">
                <i class="fas fa-eye me-1"></i>
                View
            </a>
            <button class="btn btn-outline-success btn-sm" onclick="generateReport('{{ inspection.id }}')">
                <i class="fas fa-file-pdf me-1"></i>
                Report
            </button>
        </div>
    </div>
</div>
```

### Form Components
```html
<!-- Using upload form with camera functionality -->
<div class="upload-form">
    <div class="upload-area" id="uploadArea">
        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
        <p>Drag and drop photos here or click to select</p>
        <input type="file" id="fileInput" accept="image/*" style="display: none;">
        <div class="upload-buttons">
            <button type="button" class="btn btn-primary me-2" onclick="document.getElementById('fileInput').click()">
                <i class="fas fa-folder-open me-2"></i>
                Choose File
            </button>
            <button type="button" class="btn btn-success" onclick="openCamera()">
                <i class="fas fa-camera me-2"></i>
                Take Photo
            </button>
        </div>
    </div>
    
    <!-- Camera Input (Hidden) -->
    <input type="file" id="cameraInput" accept="image/*" capture="environment" style="display: none;">
    
    <!-- Preview Area -->
    <div id="previewArea" class="mt-3" style="display: none;">
        <div class="preview-container">
            <img id="previewImage" class="img-fluid rounded" alt="Preview">
            <button type="button" class="btn btn-danger btn-sm mt-2" onclick="clearPreview()">
                <i class="fas fa-times me-1"></i>
                Remove
            </button>
        </div>
    </div>
</div>
```

## 🎨 Custom Styling

### Brand Colors
```css
/* Custom colors for CheckMate Virtue */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --primary-color: #667eea;
    --secondary-color: #764ba2;
}
```

### Custom Components
```css
/* Inspection-specific styles */
.inspection-card {
    transition: transform 0.2s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.inspection-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
```

## 📱 Mobile Features

### Camera Integration
```javascript
// Camera functionality for mobile devices
function openCamera() {
    const cameraInput = document.getElementById('cameraInput');
    if (cameraInput) {
        cameraInput.click();
    }
}
```

### Touch-Friendly Interface
```html
<!-- Large touch targets for mobile -->
<button class="btn btn-primary btn-lg">
    <i class="fas fa-camera me-2"></i>
    Take Photo
</button>
```

## 🔧 Custom JavaScript

### File Upload Handling
```javascript
// Custom upload function for inspections
async function uploadPhoto() {
    const fileInput = document.getElementById('photoInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file first', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', currentCategory.toLowerCase().replace(/ /g, '_'));
    formData.append('item', currentItem.toLowerCase().replace(/ /g, '_'));

    try {
        const response = await fetch(`/api/inspections/${inspectionId}/photos`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            showAlert('Photo uploaded successfully!', 'success');
            location.reload();
        } else {
            showAlert('Upload failed: ' + result.error, 'danger');
        }
    } catch (error) {
        showAlert('Upload failed: ' + error.message, 'danger');
    }
}
```

## 📊 Data Display

### Status Badges
```html
<!-- Dynamic status badges -->
<span class="badge bg-{{ 'success' if item.grade == 'PASS' else 'warning' if item.grade == 'REC' else 'danger' if item.grade == 'REQ' else 'secondary' }}">
    {{ item.grade if item.grade else 'N/A' }}
</span>
```

### Photo Galleries
```html
<!-- Photo gallery with modal support -->
<div class="photo-gallery">
    {% for photo in photos %}
    <div class="col-md-4 mb-3">
        <div class="photo-item">
            <img src="{{ photo.url }}" class="img-fluid rounded" alt="Photo" 
                 onclick="openPhotoModal('{{ photo.url }}', '{{ photo.title }}')">
        </div>
    </div>
    {% endfor %}
</div>
```

## 🚀 Deployment Ready

The template system includes:
- ✅ Responsive design
- ✅ Mobile camera support
- ✅ File upload handling
- ✅ Form validation
- ✅ Modal dialogs
- ✅ Photo galleries
- ✅ Status indicators
- ✅ Loading states
- ✅ Error handling

This example demonstrates how to build a professional web application using the GUI template system while maintaining consistency and reusability. 