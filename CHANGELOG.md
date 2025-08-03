# Changelog

## [1.0.2] - 2024-12-19

### 🚀 New Features
- **Vehicle Data Module**: Complete VIN decoding system for automotive inspections
  - New `/modules/vehicle_data/` module with comprehensive vehicle information handling
  - NHTSA VIN decoder API integration with offline fallback
  - Auto-population of vehicle fields (year, make, model, trim, engine, transmission, etc.)
  - Real-time VIN decoding with user feedback and error handling
  - Static VIN data for offline operation with sample vehicles

### 📁 New Files Added
- `modules/vehicle_data/__init__.py` - Module initialization
- `modules/vehicle_data/models.py` - VehicleInfo Pydantic model
- `modules/vehicle_data/vin_decoder.py` - VIN parsing and field mapping
- `modules/vehicle_data/service.py` - Async VIN decoding service
- `modules/vehicle_data/routes.py` - Vehicle data API endpoints
- `modules/vehicle_data/static_vin_data.json` - Static VIN data for offline use

### 🔧 Technical Improvements
- **Enhanced Vehicle Information**: Extended VehicleInfo model with comprehensive fields
  - Added trim, body_style, engine_displacement, transmission_type, drivetrain, fuel_type
  - Added country_of_origin, plant_code, serial_number for complete vehicle data
- **API Integration**: New `/vehicle/decode/{vin}` endpoint for VIN decoding
- **Frontend Integration**: Auto-population of vehicle fields in inspection forms
- **Offline Support**: Static VIN data with sample vehicles for testing
- **Error Handling**: Comprehensive error handling for API failures and invalid VINs

### 🎨 UI/UX Enhancements
- **VIN Decoder Interface**: Added search button and status indicators
- **Auto-fill Functionality**: Vehicle fields automatically populate when VIN is decoded
- **Real-time Feedback**: Loading states and success/error messages
- **Debounced Input**: Auto-decode VIN after user stops typing (1-second delay)

### 📦 Dependencies
- Added `httpx==0.25.2` for async HTTP requests to NHTSA API

### 🔄 Integration
- **Inspection Creation**: Enhanced inspection creation to use decoded vehicle data
- **Automotive Industry**: Special handling for automotive inspections with VIN decoding
- **Backward Compatibility**: All existing functionality preserved

## [1.0.1] - 2024-12-19

### Removed
- **Complete VIN Decoder Integration**: Removed all VIN decoding functionality including:
  - `vin_decoder.py` - Core VIN decoder service
  - `vin_routes.py` - VIN API routes
  - `vehicle_data.py` - Vehicle data management module
  - `vehicle_routes.py` - Vehicle API routes
  - `static/js/vin_decoder.js` - Frontend VIN decoder functionality
  - `static/css/vin_decoder.css` - VIN decoder styling
  - `test_vin_decoder.py` - VIN decoder unit tests
  - `test_vin_simple.py` - Simple VIN validation script
  - `VIN_DECODER_README.md` - VIN decoder documentation
  - `VIN_INTEGRATION_SUMMARY.md` - VIN integration summary
  - `VEHICLE_DATA_MODULE_README.md` - Vehicle data module documentation
  - `data/vin_cache.json` - VIN cache storage
  - `data/vehicles.json` - Vehicle data storage
  - `templates/test_vin_frontend.html` - VIN test frontend

### Changed
- **Simplified Vehicle Information**: Vehicle info is now manually entered without auto-fill
- **Removed VIN Auto-fill**: Removed VIN decoder integration from forms
- **Updated Templates**: Removed VIN confidence, source, and error displays
- **Updated App Description**: Changed from "Vehicle Inspection System" to "Multi-Industry Inspection System"

### Technical Changes
- Removed VIN router imports and inclusions from `main.py`
- Simplified vehicle info processing in inspection creation
- Removed VIN decoder metadata fields from VehicleInfo model
- Removed VIN auto-fill buttons and functionality from templates
- Removed VIN decoder CSS and JS includes from templates

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
  - **Removed all OAuth functionality** to eliminate jose dependency issues
  - Deleted OAuth-related files and documentation
  - Simplified authentication to basic session management only

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