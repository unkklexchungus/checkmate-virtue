/**
 * Main JavaScript functionality for CheckMate Virtue
 * Includes VIN decoder and general application functionality
 */

// Import error handler first
import './error-handler.js';

// Import VIN decoder functionality
import './vin_decoder.js';

// Main application class
class CheckMateVirtue {
    constructor() {
        this.vinDecoder = null;
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.initializeVINDecoder();
        this.setupEventListeners();
        this.setupFormValidation();
        this.setupNotifications();
    }

    /**
     * Initialize VIN decoder functionality
     */
    initializeVINDecoder() {
        if (typeof VINDecoder !== 'undefined') {
            this.vinDecoder = new VINDecoder();
            this.vinDecoder.init();
        }
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Form submission handling
        document.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Navigation highlighting
        this.setupNavigationHighlighting();
        
        // Modal handling
        this.setupModalHandling();
    }

    /**
     * Handle form submissions
     */
    handleFormSubmit(event) {
        const form = event.target;
        
        // Add loading state to submit buttons
        const submitButtons = form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            // Restore button after form submission
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalText;
            }, 5000);
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        // Real-time validation for required fields
        const requiredFields = document.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', this.validateField.bind(this));
            field.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    /**
     * Validate a form field
     */
    validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'This field is required');
        } else if (field.type === 'email' && value && !this.isValidEmail(value)) {
            this.showFieldError(field, 'Please enter a valid email address');
        } else {
            this.clearFieldError(event);
        }
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        // Remove existing error
        this.clearFieldError({ target: field });
        
        // Add error styling
        field.classList.add('is-invalid');
        
        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    /**
     * Clear field error
     */
    clearFieldError(event) {
        const field = event.target;
        field.classList.remove('is-invalid');
        
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Validate email format
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Setup navigation highlighting
     */
    setupNavigationHighlighting() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Setup modal handling
     */
    setupModalHandling() {
        // Auto-hide modals after form submission
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('hidden.bs.modal', () => {
                const forms = modal.querySelectorAll('form');
                forms.forEach(form => form.reset());
            });
        });
    }

    /**
     * Setup notification system
     */
    setupNotifications() {
        // Global notification function
        window.showNotification = this.showNotification.bind(this);
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);

        return notification;
    }

    /**
     * Utility function to format currency
     */
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    /**
     * Utility function to format dates
     */
    formatDate(date, format = 'short') {
        const dateObj = new Date(date);
        return dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: format === 'short' ? 'short' : 'long',
            day: 'numeric'
        });
    }

    /**
     * Utility function to debounce function calls
     */
    debounce(func, delay = 300) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Utility function to throttle function calls
     */
    throttle(func, limit = 300) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Get URL parameters
     */
    getUrlParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    /**
     * Set URL parameter
     */
    setUrlParameter(name, value) {
        const url = new URL(window.location);
        url.searchParams.set(name, value);
        window.history.pushState({}, '', url);
    }

    /**
     * Remove URL parameter
     */
    removeUrlParameter(name) {
        const url = new URL(window.location);
        url.searchParams.delete(name);
        window.history.pushState({}, '', url);
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            this.showNotification('Failed to copy to clipboard', 'error');
        }
    }

    /**
     * Download file
     */
    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Generate random ID
     */
    generateId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    /**
     * Sanitize HTML
     */
    sanitizeHtml(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    /**
     * Validate file upload
     */
    validateFileUpload(file, allowedTypes = [], maxSize = 10 * 1024 * 1024) {
        const errors = [];
        
        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            errors.push(`File type ${file.type} is not allowed`);
        }
        
        if (file.size > maxSize) {
            errors.push(`File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds maximum ${(maxSize / 1024 / 1024).toFixed(2)}MB`);
        }
        
        return errors;
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new CheckMateVirtue();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CheckMateVirtue;
} 