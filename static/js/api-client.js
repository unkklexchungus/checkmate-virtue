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

    async uploadPhotoLegacy(inspectionId, file, category, item) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);
        formData.append('item', item);

        const response = await window.errorHandler.fetchWithErrorHandling(`${this.baseURL}/api/inspections/${inspectionId}/photos`, {
            method: 'POST',
            body: formData
        });
        
        if (!response) return null;
        return response.json();
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
