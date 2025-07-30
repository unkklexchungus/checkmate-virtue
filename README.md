# CheckMate Virtue - Professional Vehicle Inspection System

A modern, Pythonic FastAPI-based web application for professional vehicle inspections.

## 🚀 Features

- **Professional Vehicle Inspections**: Complete inspection workflow with categories and items
- **Photo Upload**: Support for uploading inspection photos with validation
- **Report Generation**: Automatic report generation with statistics
- **Modern Web Interface**: Clean, responsive HTML templates
- **RESTful API**: Full API for programmatic access
- **Data Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Robust error handling with proper HTTP status codes

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
├── main.py              # Main FastAPI application
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── test_utils.py       # Utility function tests
├── data/               # Data storage
│   └── inspections.json
├── static/             # Static files
│   └── uploads/        # Uploaded photos
├── templates/          # HTML templates
│   ├── index.html
│   ├── inspections.html
│   ├── new_inspection.html
│   └── view_inspection.html
└── CheckMateVirtue/    # Original APK assets
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