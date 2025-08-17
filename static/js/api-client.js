/**
 * API Client for CheckMate Virtue
 * Standardized under /api/v1 endpoints with centralized error handling
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.apiV1Base = '/api/v1';
    }

    // Health check
    async healthCheck() {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/healthz`);
        if (!response) return null;
        return response.json();
    }

    // Inspection API v1 endpoints
    async getInspectionTemplate() {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/template`);
        if (!response) return null;
        return response.json();
    }

    async createInspection(inspectionData) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inspectionData)
        });
        
        if (!response) return null;
        return response.json();
    }

    async getInspection(inspectionId) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}`);
        if (!response) return null;
        return response.json();
    }

    async updateInspection(inspectionId, inspectionData) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inspectionData)
        });
        
        if (!response) return null;
        return response.json();
    }

    async saveDraft(inspectionId, draftData) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(draftData)
        });
        
        if (!response) return null;
        return response.json();
    }

    async uploadPhoto(inspectionId, file, step, subcategory, item) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('step', step);
        formData.append('subcategory', subcategory);
        formData.append('item', item);

        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}/photos`, {
            method: 'POST',
            body: formData
        });
        
        if (!response) return null;
        return response.json();
    }

    async finalizeInspection(inspectionId) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}/finalize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response) return null;
        return response.json();
    }

    async generateReport(inspectionId, format = 'html') {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${this.apiV1Base}/inspection/${inspectionId}/report?format=${format}`);
        if (!response) return null;
        
        if (format === 'pdf') {
            return response.blob();
        }
        
        return response.json();
    }

    // Legacy endpoints for backward compatibility
    async getInspectionTemplateLegacy() {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspection-template`);
        if (!response) return null;
        return response.json();
    }

    async createInspectionLegacy(inspectionData) {
        console.log('=== CREATE INSPECTION LEGACY ===');
        console.log('Request URL:', `${this.baseURL}/api/inspections`);
        console.log('Request data:', inspectionData);
        console.log('Request JSON:', JSON.stringify(inspectionData, null, 2));
        
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inspectionData)
        });
        
        if (!response) {
            console.error('No response from createInspectionLegacy');
            return null;
        }
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            console.error('Create inspection failed:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response body:', errorText);
            throw new Error(`Failed to create inspection: ${response.status} ${response.statusText} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Inspection created successfully:', result);
        return result;
    }

    async getInspectionLegacy(inspectionId) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}`);
        if (!response) return null;
        return response.json();
    }

    async updateInspectionLegacy(inspectionId, inspectionData) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inspectionData)
        });
        
        if (!response) return null;
        return response.json();
    }

    async saveDraftLegacy(inspectionId, draftData) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(draftData)
        });
        
        if (!response) return null;
        return response.json();
    }

    async uploadPhotoLegacy(inspectionId, file, step, item) {
        console.log('=== UPLOAD PHOTO LEGACY ===');
        console.log('Inspection ID:', inspectionId);
        console.log('Step:', step);
        console.log('Item:', item);
        
        // Map step names to category names
        const stepToCategoryMap = {
            'Under the Hood': 'Engine Bay',
            'Wheels Off': 'Wheels & Tire Maintenance',
            'Underbody': 'Underbody',
            'Interior': 'Interior',
            'Exterior': 'Exterior',
            'Test Drive': 'Test Drive',
            'Fluid Leaks': 'Fluid Leaks',
            'Exhaust': 'Exhaust'
        };
        
        const category = stepToCategoryMap[step] || step;
        console.log('Mapped category:', category);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);
        formData.append('item', item);

        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}/photos`, {
            method: 'POST',
            body: formData
        });
        
        if (!response) {
            console.error('No response from uploadPhotoLegacy');
            return null;
        }
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            console.error('Upload photo failed:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Error response body:', errorText);
            throw new Error(`Failed to upload photo: ${response.status} ${response.statusText} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('Photo uploaded successfully:', result);
        return result;
    }

    async generateReportLegacy(inspectionId, format = 'html') {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}/report?format=${format}`);
        if (!response) return null;
        
        if (format === 'pdf') {
            return response.blob();
        }
        
        return response.json();
    }

    // Vehicle data endpoints
    async decodeVIN(vin) {
        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/vehicle/decode/${vin}`);
        if (!response) return null;
        return response.json();
    }

    // Utility methods
    async testEndpoint(endpoint) {
        try {
            const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}${endpoint}`);
            return {
                status: response?.status || 0,
                ok: response?.ok || false,
                url: `${this.baseURL}${endpoint}`
            };
        } catch (error) {
            return {
                status: 0,
                ok: false,
                error: error.message,
                url: `${this.baseURL}${endpoint}`
            };
        }
    }
}

// Create a global instance
window.apiClient = new APIClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}
