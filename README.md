# CheckMate Virtue - Multi-Industry Professional Inspection System

A modern, Pythonic FastAPI-based web application for professional inspections across multiple industries, featuring a guided inspection flow with comprehensive vehicle data integration.

## 🚀 Features

### Guided Inspection System
- **Three-Step Guided Flow**: Under the Hood → Wheels Off → Underbody
- **Dynamic Template System**: JSON-based configuration for inspection items
- **Three-Color Status System**: Pass (✅), Recommended (⚠️), Required (❌)
- **Real-time Progress Tracking**: Visual progress bar with completion statistics
- **Photo Documentation**: Upload photos for each inspection item
- **Comprehensive Notes**: Detailed notes field for each item
- **VIN Auto-fill**: Automatic vehicle data population from VIN input

### Multi-Industry Support
- **Automotive**: Vehicle inspections with VIN decoding
- **Construction**: Site safety and structural integrity
- **Healthcare**: Medical equipment and facility safety
- **Manufacturing**: Equipment and quality control
- **Food Safety**: Restaurant and kitchen hygiene
- **Real Estate**: Property condition and maintenance
- **IT & Data Centers**: Infrastructure and security
- **Environmental**: Compliance and waste management

### Technical Features
- **Modular Architecture**: Clean separation with dedicated modules
- **API-First Design**: RESTful endpoints for all operations
- **Modern Web Interface**: Bootstrap 5 with responsive design
- **Data Persistence**: JSON-based storage with backup
- **PDF Report Generation**: Professional documentation export
- **Photo Management**: Secure file upload with validation
- **Vehicle Data Integration**: Comprehensive VIN decoding system

## 🏗️ Architecture

The application follows modern Python best practices:

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Pydantic**: Data validation and serialization
- **Jinja2**: Template engine for HTML rendering
- **Pathlib**: Modern path handling
- **Type Hints**: Comprehensive type annotations for better code quality

## 📁 Project Structure

```
Lexicon-Re/
├── main.py                    # Main FastAPI application
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── CHANGELOG.md              # Version history and changes
├── data/                     # Data storage
│   ├── inspections.json      # Legacy inspections
│   ├── invoices.json         # Invoice data
│   └── clients.json          # Client information
├── static/                   # Static files
│   ├── uploads/              # Uploaded photos
│   ├── invoices/             # Invoice files
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript files
├── templates/                # HTML templates
│   ├── index.html            # Home page
│   ├── inspection_form.html  # Guided inspection form
│   ├── inspection_list.html  # Inspection list view
│   ├── industries.html       # Industry selection
│   └── invoices/             # Invoice templates
├── modules/                  # Modular components
│   ├── inspection/           # Guided inspection module
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic models
│   │   ├── service.py        # Business logic
│   │   ├── routes.py         # API endpoints
│   │   └── templates.json    # Dynamic configuration
│   └── vehicle_data/         # Vehicle data module
│       ├── __init__.py
│       ├── models.py         # Vehicle models
│       ├── service.py        # VIN decoding service
│       ├── routes.py         # Vehicle API endpoints
│       └── vin_decoder.py    # VIN parsing logic
└── CheckMateVirtue/          # Original APK assets
    └── assets/
        └── basic_inspection.json
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Lexicon-Re
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the application**:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔧 Configuration

All configuration settings are centralized in `config.py`:

- **Application Settings**: Name, version, description
- **Server Settings**: Host, port
- **File Paths**: All file and directory paths
- **CORS Settings**: Cross-origin resource sharing
- **Upload Settings**: File size limits, allowed extensions
- **Validation Settings**: Input validation rules

## 🔍 Guided Inspection System

The new guided inspection system provides a structured, step-by-step approach to vehicle inspections:

### Three-Step Process
1. **Under the Hood**: Engine fluids, filters, belts, and electrical systems
2. **Wheels Off**: Brake systems, suspension components, and wheel assemblies  
3. **Underbody**: Leaks, exhaust systems, and structural integrity

### Key Features
- **Dynamic Templates**: Inspection items are loaded from JSON configuration
- **Status Tracking**: Three-color system (Pass/Recommended/Required)
- **Photo Documentation**: Upload photos for each inspection item
- **Progress Tracking**: Real-time completion statistics
- **VIN Integration**: Automatic vehicle data population
- **Comprehensive Reporting**: Detailed inspection reports with statistics

### Usage
1. Navigate to `/inspection/form` to start a new guided inspection
2. Enter VIN for automatic vehicle data population
3. Complete each step with checkboxes and status selections
4. Add photos and notes as needed
5. Save inspection and view results at `/inspection/list`

### API Endpoints
- `GET /inspection/template` - Get inspection template
- `GET /inspection/form` - Render inspection form
- `GET /inspection/list` - View inspection list
- `POST /inspection/` - Create new inspection
- `GET /inspection/{id}` - Get specific inspection
- `PUT /inspection/{id}` - Update inspection
- `POST /inspection/{id}/photos` - Upload photos

## 🔐 OAuth Authentication

The application supports OAuth authentication with Google and GitHub. To enable OAuth:

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set authorized redirect URI: `http://localhost:8000/auth/callback/google`
6. Copy Client ID and Client Secret to your `.env` file

### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set Homepage URL: `http://localhost:8000`
4. Set Authorization callback URL: `http://localhost:8000/auth/callback/github`
5. Copy Client ID and Client Secret to your `.env` file

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 📋 API Endpoints

### Web Interface
- `GET /` - Home page
- `GET /inspections` - List all inspections
- `GET /inspections/new` - New inspection form
- `GET /inspections/{id}` - View specific inspection

### API Endpoints
- `GET /api/inspection-template` - Get inspection template
- `POST /api/inspections` - Create new inspection
- `PUT /api/inspections/{id}` - Update inspection
- `POST /api/inspections/{id}/photos` - Upload inspection photos
- `GET /api/inspections/{id}/report` - Generate inspection report

### OAuth Endpoints
- `GET /login` - Login page
- `GET /auth/google` - Google OAuth login
- `GET /auth/github` - GitHub OAuth login
- `GET /auth/callback/{provider}` - OAuth callback handler
- `GET /auth/logout` - Logout user
- `GET /auth/user` - Get current user info

## 🧪 Testing

Run the utility function tests:

```bash
python3 test_utils.py
```

## 🔍 Code Quality Improvements

The codebase has been significantly improved with:

### 1. **Better Organization**
- Separated configuration into `config.py`
- Centralized constants and settings
- Clear separation of concerns

### 2. **Enhanced Error Handling**
- Proper HTTP status codes
- Comprehensive exception handling
- User-friendly error messages

### 3. **Improved Type Safety**
- Comprehensive type hints
- Pydantic models for data validation
- Better IDE support and code completion

### 4. **File Operations**
- Centralized file handling utilities
- Proper encoding handling
- Error recovery mechanisms

### 5. **Data Validation**
- Input validation with Pydantic
- File type validation for uploads
- Data structure validation

### 6. **Pythonic Practices**
- Pathlib for path handling
- Context managers for file operations
- List comprehensions and generator expressions
- Modern Python syntax

## 🚀 Running the Application

1. **Start the server**:
   ```bash
   python main.py
   ```

2. **Access the web interface**:
   - Open http://localhost:8000 in your browser

3. **API Documentation**:
   - Visit http://localhost:8000/docs for interactive API documentation

## 📊 Data Models

### VehicleInfo
- `year`: Vehicle year
- `make`: Vehicle make
- `model`: Vehicle model
- `vin`: Vehicle identification number
- `license_plate`: License plate number
- `mileage`: Vehicle mileage

### InspectionRequest
- `title`: Inspection title (1-200 characters)
- `vehicle_info`: Vehicle information
- `inspector_name`: Inspector name (1-100 characters)
- `inspector_id`: Inspector ID

### InspectionData
- `id`: Unique inspection ID
- `title`: Inspection title
- `vehicle_info`: Vehicle information
- `inspector_name`: Inspector name
- `inspector_id`: Inspector ID
- `date`: Inspection date
- `categories`: List of inspection categories
- `status`: Inspection status (default: "draft")

## 🔒 Security Features

- **File Upload Validation**: Only allowed image types
- **Input Validation**: Comprehensive validation with Pydantic
- **Error Handling**: Secure error messages without information leakage
- **CORS Configuration**: Configurable cross-origin settings

## 🛠️ Development

### Adding New Features

1. **Update models** in `main.py` if needed
2. **Add configuration** in `config.py` for new settings
3. **Create templates** in `templates/` for new pages
4. **Add routes** in `main.py` for new endpoints
5. **Update tests** in `test_utils.py` for new functionality

### Code Style

The code follows PEP 8 guidelines and modern Python practices:
- Type hints for all functions
- Docstrings for all classes and functions
- Consistent naming conventions
- Proper error handling
- Clean, readable code structure

## 📝 License

This project is part of the CheckMate Virtue vehicle inspection system.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**CheckMate Virtue** - Professional Vehicle Inspection System 