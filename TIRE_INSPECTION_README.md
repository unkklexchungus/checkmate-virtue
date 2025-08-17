# Tire Inspection System Implementation

This document describes the implementation of the "Tires & Tire Maintenance" section for the automotive inspection system.

## Overview

The tire inspection system provides a comprehensive interface for recording tire condition, pressure readings, tread depth, and maintenance recommendations. It follows the traffic-light workflow (Green = OK, Yellow = Attention, Red = Immediate) and is designed to be mobile-friendly and printable.

## Architecture

### Models (`modules/inspection/tire_models.py`)

#### Core Enums
- `TirePos`: Tire positions (LF, RF, LR, RR, SPARE)
- `Light`: Traffic light status (GREEN, YELLOW, RED, NA)

#### Data Models
- `TireReading`: Individual tire measurements and status
- `TireInspection`: Complete tire inspection data
- `TireInspectionCreate`: Input model for creating/updating inspections

#### Key Features
- **Validation**: PSI (0-80), tread depth (0-20 32nds)
- **Status Calculation**: Automatic section status based on tire conditions
- **Auto-suggestions**: Intelligent work item recommendations

### Service Layer (`modules/inspection/tire_service.py`)

#### Core Functions
- `get_tire_inspection(inspection_id)`: Retrieve tire data
- `create_or_update_tire_inspection(inspection_id, data)`: Save tire data
- `delete_tire_inspection(inspection_id)`: Remove tire data
- `get_tire_inspection_status(inspection_id)`: Get overall status
- `validate_tire_reading(data)`: Validate individual readings

#### Data Storage
- JSON-based storage in `data/tire_inspections.json`
- Automatic data serialization/deserialization
- Error handling and logging

### API Routes (`modules/inspection/tire_routes.py`)

#### Endpoints
- `POST /api/v1/inspections/{inspection_id}/tires`: Create/upsert
- `GET /api/v1/inspections/{inspection_id}/tires`: Fetch data
- `PUT /api/v1/inspections/{inspection_id}/tires`: Update data
- `DELETE /api/v1/inspections/{inspection_id}/tires`: Delete data
- `GET /api/v1/inspections/{inspection_id}/tires/status`: Get status
- `POST /api/v1/inspections/{inspection_id}/tires/validate`: Validate data

#### Features
- Comprehensive validation
- Auto-suggestion responses
- Performance timing
- Error handling

### UI Component (`templates/tire_inspection_section.html`)

#### Layout Structure
1. **Header Row**: Tire brand/pattern, size, speed/load (F/R)
2. **Main Table**: 5×5 grid for tire readings
3. **Work Checkboxes**: Rotation, balance, maintenance, wear concern
4. **Alignment Check**: Traffic light selector
5. **Condition Checklist**: Right-hand column with observations

#### Interactive Features
- **Auto-save**: Debounced saving on input changes
- **Traffic Light Controls**: Keyboard-navigable radio buttons
- **Status Indicators**: Real-time section status updates
- **Auto-suggestions**: Intelligent work item recommendations
- **Print Mode**: Optimized for printing

## Usage Examples

### Basic Integration

```html
<!-- Include the tire section in your inspection template -->
{% from 'tire_inspection_section.html' import tire_inspection_section %}
{{ tire_inspection_section('your_inspection_id') }}
```

### API Usage

```javascript
// Create tire inspection
const tireData = {
    tire_front: "Michelin Primacy",
    tire_rear: "Michelin Primacy",
    size_front: "225/45R17",
    size_rear: "225/45R17",
    speed_load_front: "94V",
    speed_load_rear: "94V",
    readings: {
        "LF": {
            "psi_in": 32.0,
            "psi_out": 35.0,
            "tread_32nds": 7.0,
            "status": "GREEN"
        },
        "RF": {
            "psi_in": 30.0,
            "psi_out": 35.0,
            "tread_32nds": 6.0,
            "status": "YELLOW"
        }
    },
    rotation: true,
    balance: false,
    maintenance: false,
    tire_wear_concern: true,
    alignment_check: "YELLOW",
    cond_inner_wear: true,
    cond_cupping_feather: true
};

const response = await fetch(`/api/v1/inspections/${inspectionId}/tires`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tireData)
});

const result = await response.json();
console.log('Section status:', result.section_status);
console.log('Suggestions:', result.suggestions);
```

### Python Service Usage

```python
from modules.inspection.tire_models import TireInspectionCreate, TireReading, TirePos, Light
from modules.inspection.tire_service import create_or_update_tire_inspection

# Create tire inspection data
readings = {
    TirePos.LF: TireReading(psi_in=32, psi_out=35, tread_32nds=7, status=Light.GREEN),
    TirePos.RF: TireReading(psi_in=30, psi_out=35, tread_32nds=6, status=Light.YELLOW),
    TirePos.LR: TireReading(psi_in=28, psi_out=35, tread_32nds=5, status=Light.YELLOW),
    TirePos.RR: TireReading(psi_in=34, psi_out=35, tread_32nds=7, status=Light.GREEN),
    TirePos.SPARE: TireReading(psi_in=45, psi_out=45, tread_32nds=None, status=Light.NA)
}

tire_data = TireInspectionCreate(
    tire_front="Michelin Primacy",
    tire_rear="Michelin Primacy",
    size_front="225/45R17",
    size_rear="225/45R17",
    speed_load_front="94V",
    speed_load_rear="94V",
    readings=readings,
    rotation=True,
    balance=False,
    maintenance=False,
    tire_wear_concern=True,
    alignment_check=Light.YELLOW,
    cond_inner_wear=True,
    cond_cupping_feather=True
)

# Save tire inspection
inspection = create_or_update_tire_inspection("inspection_123", tire_data)
print(f"Section status: {inspection.get_section_status()}")
print(f"Auto-suggestions: {inspection.auto_suggest_work_items()}")
```

## Business Logic

### Status Calculation
1. **RED**: Any tire with RED status or alignment RED
2. **YELLOW**: Any tire with YELLOW status or alignment YELLOW (if no RED)
3. **GREEN**: All tires and alignment GREEN

### Auto-suggestions
- **Uneven wear patterns**: Suggests rotation and tire wear concern
- **Alignment issues**: Suggests balance
- **Low tread (< 3/32)**: Suggests maintenance
- **Alignment RED**: Auto-checks balance

### Validation Rules
- PSI: 0-80 range
- Tread: 0-20 32nds
- PSI Out should not be less than PSI In
- Status must be valid enum value

## Testing

Run the test suite:

```bash
python test_tire_inspection.py
```

### Test Coverage
- Model validation
- Service layer functions
- API endpoints
- Business logic
- Error handling

## Integration Points

### Main Application
The tire router is integrated into the main FastAPI application:

```python
# In main.py
from modules.inspection.tire_routes import tire_router
app.include_router(tire_router)
```

### Existing Inspection System
The tire section can be integrated into existing inspection workflows by:
1. Including the template macro
2. Handling status events
3. Integrating with overall inspection status

## Mobile & Print Support

### Mobile Responsiveness
- Responsive grid layout
- Touch-friendly controls
- Optimized for small screens

### Print Optimization
- Clean borders and spacing
- High contrast for readability
- Compact layout for single-page printing
- Hidden UI elements in print mode

## Accessibility Features

- Keyboard navigation for all controls
- ARIA labels for screen readers
- High contrast color scheme
- Focus indicators
- Semantic HTML structure

## Data Flow

1. **User Input**: Form interactions trigger JavaScript events
2. **Data Validation**: Client-side validation with server-side verification
3. **Auto-save**: Debounced saving to prevent excessive API calls
4. **Status Updates**: Real-time status calculation and display
5. **Suggestions**: Intelligent recommendations based on conditions
6. **Persistence**: JSON storage with error handling

## Future Enhancements

- Database integration (PostgreSQL/MySQL)
- Photo upload for tire damage
- Historical data tracking
- Advanced analytics and reporting
- Integration with tire manufacturer APIs
- Barcode scanning for tire identification

## Troubleshooting

### Common Issues

1. **Validation Errors**: Check PSI and tread ranges
2. **Save Failures**: Verify data directory permissions
3. **Status Not Updating**: Check JavaScript console for errors
4. **Print Issues**: Ensure print CSS is loaded

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=true
```

## API Reference

### Request/Response Format
All API endpoints return consistent JSON responses:

```json
{
    "success": true,
    "data": { /* tire inspection data */ },
    "section_status": "GREEN|YELLOW|RED",
    "suggestions": ["rotation", "balance"]
}
```

### Error Responses
```json
{
    "error": "Validation failed",
    "details": { /* validation errors */ },
    "path": "/api/v1/inspections/123/tires"
}
```

## Performance Considerations

- Debounced auto-save (500ms delay)
- Efficient JSON serialization
- Minimal DOM updates
- Optimized API responses
- Caching for frequently accessed data

## Security

- Input validation and sanitization
- CSRF protection (if enabled)
- Rate limiting (recommended)
- Data encryption for sensitive information
