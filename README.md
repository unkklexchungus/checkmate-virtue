# CheckMate Virtue - Professional Vehicle Inspection System

A modern web-based vehicle inspection application built with FastAPI and Python, designed to replace the original Android app with a comprehensive web interface.

## 🚗 Features

- **Comprehensive Vehicle Inspections** - Multi-point inspection system covering all major vehicle systems
- **Photo Documentation** - Upload and attach photos to inspection items
- **Professional Reporting** - Generate detailed inspection reports
- **Vehicle Information Tracking** - Store VIN, make, model, year, mileage, and license plate
- **Inspector Management** - Track inspector details and assignments
- **Real-time Updates** - Auto-save functionality and live updates
- **Responsive Design** - Works on desktop, tablet, and mobile devices

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Template Engine**: Jinja2
- **File Upload**: Python Multipart
- **Data Storage**: JSON-based file system
- **Server**: Uvicorn ASGI server

## 📋 Inspection Categories

The application includes comprehensive inspection points for:

- **Brake System** - Pads, rotors, lines, calipers, master cylinder
- **Tire Maintenance** - Tread depth, pressure, condition, alignment
- **Steering & Suspension** - Shocks, struts, ball joints, control arms
- **Exhaust System** - Muffler, pipes, O2 sensors, catalytic converter
- **Engine Performance** - Ignition, fuel system, compression
- **Electrical System** - Battery, alternator, starter, wiring
- **Fluid Leaks** - Oil, coolant, transmission, brake fluid
- **Safety Equipment** - Lights, signals, wipers, mirrors

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/checkmate-virtue-web.git
   cd checkmate-virtue-web
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**
   Open your browser and navigate to: http://localhost:8000

## 📱 Usage

### Creating a New Inspection

1. Navigate to the home page
2. Click "Start New Inspection"
3. Fill in inspector information
4. Enter vehicle details (year, make, model, VIN, etc.)
5. Click "Start Inspection"

### Performing an Inspection

1. Go through each category systematically
2. For each item:
   - Select appropriate grade (Pass/Fail/Rec/Req/N/A)
   - Add notes describing findings
   - Upload photos if needed
3. Save your progress regularly
4. Generate final report when complete

### Photo Upload

- Click the camera icon next to any inspection item
- Drag and drop images or use the file picker
- Photos are automatically associated with the specific item
- Multiple photos can be uploaded per item

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/inspections` | List all inspections |
| GET | `/inspections/new` | New inspection form |
| POST | `/api/inspections` | Create new inspection |
| GET | `/inspections/{id}` | View specific inspection |
| PUT | `/api/inspections/{id}` | Update inspection |
| POST | `/api/inspections/{id}/photos` | Upload photos |
| GET | `/api/inspections/{id}/report` | Generate report |
| GET | `/api/inspection-template` | Get inspection template |

## 📁 Project Structure

```
checkmate-virtue-web/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── templates/             # HTML templates
│   ├── index.html         # Home page
│   ├── new_inspection.html # New inspection form
│   ├── inspections.html   # Inspections list
│   └── view_inspection.html # Inspection details
├── static/                # Static files
│   └── uploads/           # Photo uploads
└── data/                  # Data storage
    └── inspections.json   # Inspection data
```

## 🔒 Data Storage

- **Inspection Data**: Stored in JSON format in `data/inspections.json`
- **Photos**: Uploaded to `static/uploads/` directory
- **Templates**: Original inspection template from decompiled APK

## 🎨 Customization

### Adding New Inspection Categories

1. Modify the inspection template in `CheckMateVirtue/assets/basic_inspection.json`
2. Add new categories with items and descriptions
3. Restart the application

### Styling

- Bootstrap 5 for responsive design
- Custom CSS in template files
- Font Awesome icons for UI elements

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original CheckMate Virtue Android app for the inspection template
- FastAPI community for the excellent web framework
- Bootstrap team for the responsive UI components

## 📞 Support

For support, email support@checkmatevirtue.com or create an issue in the GitHub repository.

---

**CheckMate Virtue Web** - Professional vehicle inspections made simple and efficient. 