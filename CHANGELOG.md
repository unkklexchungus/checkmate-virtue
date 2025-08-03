# Changelog

## [2.0.0] - 2025-08-03

### Added
- **New Guided Inspection Module** - Complete restructure of the inspection system
  - Modular architecture with `/modules/inspection/` directory structure
  - JSON-based template system for dynamic inspection configuration
  - Three-step guided inspection flow:
    - Step 1: Under the Hood
    - Step 2: Wheels Off  
    - Step 3: Underbody
  - Subcategories within each step for organized inspection items
  - Three-color status system:
    - ✅ Green = Pass
    - ⚠️ Yellow = Recommended
    - ❌ Red = Required
  - Individual checkboxes for each inspection item
  - Optional photo upload functionality for each item
  - Optional notes field for detailed documentation
  - Real-time progress tracking with visual progress bar
  - VIN auto-fill integration with vehicle data module
  - Comprehensive inspection list with statistics dashboard
  - Detailed inspection view with accordion-style organization
  - PDF report generation capability

### Technical Improvements
- **Modular Architecture**: Clean separation of concerns with dedicated modules
  - `modules/inspection/models.py` - Pydantic data models
  - `modules/inspection/service.py` - Business logic and data persistence
  - `modules/inspection/routes.py` - API endpoints and web routes
  - `modules/inspection/templates.json` - Dynamic configuration
- **Database-Ready**: Structured data storage with JSON persistence
- **API-First Design**: RESTful endpoints for all inspection operations
- **Modern UI**: Bootstrap 5 with Font Awesome icons and responsive design
- **Photo Management**: Secure file upload with validation and organization
- **Vehicle Integration**: Seamless VIN decoding and auto-fill functionality

### Files Added
- `modules/inspection/__init__.py`
- `modules/inspection/models.py`
- `modules/inspection/service.py`
- `modules/inspection/routes.py`
- `modules/inspection/templates.json`
- `templates/inspection_form.html`
- `templates/inspection_list.html`

### Files Modified
- `main.py` - Added inspection module router integration and redirect routes
- `templates/index.html` - Updated navigation with new inspection links
- `templates/redirect_to_guided_inspection.html` - Redirect template for new inspections
- `templates/redirect_to_guided_inspections.html` - Redirect template for inspection list

### API Endpoints Added
- `GET /inspection/template` - Get inspection template
- `GET /inspection/form` - Render inspection form page
- `GET /inspection/list` - Render inspection list page
- `POST /inspection/` - Create new inspection
- `GET /inspection/{id}` - Get specific inspection
- `PUT /inspection/{id}` - Update inspection
- `POST /inspection/{id}/photos` - Upload photo for inspection item

### Features
- **Dynamic Template Loading**: Inspection items loaded from JSON configuration
- **Real-time Progress**: Visual progress tracking during inspection
- **Photo Documentation**: Upload and attach photos to specific items
- **Comprehensive Reporting**: Detailed inspection reports with statistics
- **Vehicle Data Integration**: Automatic vehicle information population from VIN
- **Responsive Design**: Mobile-friendly interface with modern UI components
- **Data Persistence**: JSON-based storage with backup and recovery
- **Export Capabilities**: PDF report generation for professional documentation

### Breaking Changes
- **Primary Inspection System**: New guided inspection system is now the primary interface
- **Automatic Redirects**: Legacy `/inspections` routes now redirect to new guided system
- **Updated Navigation**: "New Inspection" and "Inspection List" are now the primary options
- **Legacy Access**: Legacy inspection system still available at `/inspections` but redirects to new system

### Migration Notes
- Existing inspections remain accessible through legacy endpoints
- New inspections use the guided flow with enhanced features
- Vehicle data integration requires VIN input for auto-fill functionality
- Photo uploads are stored in `static/uploads/inspections/` directory

## [1.x.x] - Previous versions
- Legacy inspection system
- Basic invoice management
- Vehicle data module
- Multi-industry support 