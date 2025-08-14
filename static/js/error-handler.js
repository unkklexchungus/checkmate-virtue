/**
 * Centralized Error Handler for CheckMate Virtue
 * Provides consistent error handling across all fetch requests
 */

class ErrorHandler {
    constructor() {
        this.errorCount = new Map(); // Track error frequency to avoid spam
        this.toastContainer = null;
        this.init();
    }

    init() {
        this.createToastContainer();
        this.setupGlobalErrorHandlers();
    }

    createToastContainer() {
        // Create a dedicated container for error toasts
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'error-toast-container';
        this.toastContainer.className = 'position-fixed';
        this.toastContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        document.body.appendChild(this.toastContainer);
    }

    setupGlobalErrorHandlers() {
        // Global unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled Promise Rejection', event.reason, 'error');
            event.preventDefault();
        });

        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleError('JavaScript Error', event.error || event.message, 'error');
        });
    }

    /**
     * Centralized fetch wrapper with error handling
     */
    async fetchWithErrorHandling(url, options = {}) {
        const requestId = this.generateRequestId();
        
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                await this.handleHttpError(response, requestId);
                return null;
            }
            
            return response;
        } catch (error) {
            this.handleNetworkError(error, requestId);
            return null;
        }
    }

    /**
     * Handle HTTP error responses (4xx, 5xx)
     */
    async handleHttpError(response, requestId) {
        let errorData;
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
            errorData = await response.json();
        } catch {
            // If response is not JSON, use status text
            errorData = { detail: response.statusText };
        }

        // Extract user-friendly error message
        const userMessage = this.extractUserMessage(errorData, response.status);
        
        // Log error once per request
        this.logErrorOnce(`HTTP ${response.status}`, {
            url: response.url,
            status: response.status,
            statusText: response.statusText,
            detail: errorData.detail,
            requestId
        });

        // Show user-friendly toast
        this.showToast(userMessage, this.getErrorType(response.status));
        
        throw new Error(userMessage);
    }

    /**
     * Handle network errors (connection issues, timeouts, etc.)
     */
    handleNetworkError(error, requestId) {
        const errorMessage = this.getNetworkErrorMessage(error);
        
        // Log error once per request
        this.logErrorOnce('Network Error', {
            message: error.message,
            type: error.name,
            requestId
        });

        // Show user-friendly toast
        this.showToast(errorMessage, 'error');
        
        throw new Error(errorMessage);
    }

    /**
     * Extract user-friendly error message from server response
     */
    extractUserMessage(errorData, statusCode) {
        // Handle validation errors (422)
        if (statusCode === 422 && errorData.detail) {
            if (Array.isArray(errorData.detail)) {
                return errorData.detail.map(err => 
                    `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg}`
                ).join('; ');
            }
            return errorData.detail;
        }

        // Handle other structured errors
        if (errorData.detail) {
            return errorData.detail;
        }

        // Handle problem+json format
        if (errorData.title) {
            return errorData.title;
        }

        // Fallback to status-based messages
        return this.getStatusBasedMessage(statusCode);
    }

    /**
     * Get user-friendly message based on HTTP status
     */
    getStatusBasedMessage(statusCode) {
        const messages = {
            400: 'Invalid request. Please check your input and try again.',
            401: 'Authentication required. Please log in and try again.',
            403: 'Access denied. You don\'t have permission to perform this action.',
            404: 'Resource not found. The requested item may have been moved or deleted.',
            409: 'Conflict. The resource already exists or has been modified.',
            422: 'Validation error. Please check your input and try again.',
            429: 'Too many requests. Please wait a moment and try again.',
            500: 'Server error. Please try again later or contact support.',
            502: 'Service temporarily unavailable. Please try again later.',
            503: 'Service temporarily unavailable. Please try again later.',
            504: 'Request timeout. Please try again later.'
        };
        
        return messages[statusCode] || `Unexpected error (${statusCode}). Please try again.`;
    }

    /**
     * Get network error message
     */
    getNetworkErrorMessage(error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return 'Network connection error. Please check your internet connection and try again.';
        }
        
        if (error.name === 'AbortError') {
            return 'Request was cancelled. Please try again.';
        }
        
        return 'Network error. Please check your connection and try again.';
    }

    /**
     * Get error type for toast styling
     */
    getErrorType(statusCode) {
        if (statusCode >= 500) return 'error';
        if (statusCode >= 400) return 'warning';
        return 'info';
    }

    /**
     * Log error once to avoid console spam
     */
    logErrorOnce(errorType, details) {
        const key = `${errorType}:${details.url || details.message}`;
        const count = this.errorCount.get(key) || 0;
        
        if (count === 0) {
            console.error(`[${errorType}]`, details);
            this.errorCount.set(key, 1);
            
            // Reset count after 5 minutes
            setTimeout(() => {
                this.errorCount.delete(key);
            }, 5 * 60 * 1000);
        } else {
            console.warn(`[${errorType}] (repeated ${count + 1} times)`, details);
            this.errorCount.set(key, count + 1);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'error', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${this.getBootstrapAlertType(type)} alert-dismissible fade show`;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.toastContainer.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);

        return toast;
    }

    /**
     * Convert error type to Bootstrap alert type
     */
    getBootstrapAlertType(type) {
        const types = {
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        };
        return types[type] || 'danger';
    }

    /**
     * Generate unique request ID for tracking
     */
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Handle general errors
     */
    handleError(title, error, type = 'error') {
        const message = error?.message || error?.toString() || 'An unexpected error occurred';
        
        this.logErrorOnce(title, { message, error });
        this.showToast(message, type);
    }

    /**
     * Clear all error toasts
     */
    clearToasts() {
        if (this.toastContainer) {
            this.toastContainer.innerHTML = '';
        }
    }

    /**
     * Reset error counters
     */
    resetErrorCounters() {
        this.errorCount.clear();
    }
}

// Create global error handler instance
window.errorHandler = new ErrorHandler();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorHandler;
}
