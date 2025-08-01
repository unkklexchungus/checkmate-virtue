# Changelog

## [Unreleased] - Invoice View Fixes and Improvements

### 🐛 Fixed
- **Invoice View Template Errors**: Fixed TypeError when comparing string values to integers in template comparisons
  - Fixed `tax_rate > 0` comparisons by converting to float: `(item['tax_rate']|float) > 0`
  - Fixed `discount_percent > 0` comparisons by converting to float: `(item['discount_percent']|float) > 0`
  - Fixed all invoice total comparisons for shipping, handling, other_charges
  - Fixed all breakdown total comparisons for labor_total, parts_total, materials_total, service_total
- **Deployment Crashes**: Fixed missing template files and dependency issues that were causing deployment failures
  - Added missing `templates/invoices/edit.html` template
  - Cleared Python cache to ensure template changes are applied
  - Improved error handling for missing template files
  - Fixed ModuleNotFoundError for reportlab by resolving dependency conflicts
  - Removed problematic Pillow version constraint that was causing build failures

### 📊 Data Structure Improvements
- **Invoice Data Consistency**: Fixed missing fields and data structure issues
  - Added missing `item_type` fields to all invoice items
  - Added calculated totals (`subtotal`, `discount_amount`, `taxable_amount`, `tax_amount`, `total`) to all invoice items
  - Fixed duplicate job IDs by giving each job a unique identifier
  - Updated job references in items to match new job IDs
  - Added missing `jobs` array to invoices that were missing it
  - Added job-based totals (`labor_total`, `parts_total`, `materials_total`, `service_total`)

### 🎨 UI/UX Enhancements
- **Job-Based Organization**: Enhanced invoice view to group items by their associated jobs
  - Items are now organized under their respective job sections
  - Added "General Services" section for items not associated with specific jobs
  - Improved visual hierarchy with proper indentation and styling
  - Job names are displayed instead of job IDs for better readability

- **Payment Tracking**: Added comprehensive payment tracking and balance calculations
  - Shows payment history with amounts, methods, and dates
  - Displays total paid and remaining balance
  - Payment information is clearly organized and easy to read

- **Enhanced Visual Design**: Improved styling and layout throughout the invoice view
  - Better color coding for different item types (labor, parts, materials, services)
  - Improved spacing and typography
  - Added badges for tax rates, discounts, and item types
  - Enhanced responsive design for mobile devices

### 🔧 Technical Improvements
- **Template Error Handling**: Added robust error handling for missing or malformed data
- **Type Safety**: Ensured all numeric comparisons use proper type conversion
- **Code Organization**: Improved template structure with better separation of concerns
- **Performance**: Optimized template rendering with efficient data processing

### 📁 Files Modified
- `data/invoices.json` - Fixed data structure and added missing fields
- `templates/invoices/view.html` - Enhanced template with job-based organization and type-safe comparisons
- `invoice_routes.py` - Added invoice routing functionality
- `models.py` - Added comprehensive invoice and payment models

### 🚀 New Features
- **Invoice Management System**: Complete invoicing system with job-based organization
- **Payment Tracking**: Full payment history and balance calculation
- **Multi-Industry Support**: Invoice templates for different industries
- **Client Management**: Integrated client information display
- **PDF Generation**: Support for invoice PDF generation (framework ready)

### 🔄 Backward Compatibility
- All existing invoice data has been preserved and enhanced
- Template changes are backward compatible with existing data structures
- Graceful handling of missing or malformed data

---

## Previous Releases

### [v1.0.0] - Railway deployment configuration
- Added Railway deployment configuration
- Configured production environment settings

### [v0.9.0] - OAuth Authentication
- Added OAuth authentication with Google and GitHub support
- Implemented secure session management
- Added user authentication middleware

### [v0.8.0] - GUI Template System
- Added comprehensive GUI template system extracted from CheckMate Virtue
- Implemented responsive design patterns
- Added industry-specific inspection templates

### [v0.7.0] - Camera and Upload Features
- Added camera functionality for photo capture
- Fixed upload button issues
- Improved file handling and storage

### [v0.6.0] - Railway Deployment Fixes
- Fixed template file location for Railway deployment
- Optimized file paths for production environment 