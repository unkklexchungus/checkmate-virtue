# Vehicle Data Module

The Vehicle Data Module provides VIN (Vehicle Identification Number) decoding functionality for the CheckMate Virtue automotive inspection system.

## Features

- **NHTSA VIN Decoder API Integration**: Real-time VIN decoding using the NHTSA API
- **Offline Fallback**: Static VIN data for offline operation
- **Auto-population**: Automatically fills vehicle information fields in inspection forms
- **Error Handling**: Comprehensive error handling for API failures and invalid VINs
- **Real-time Feedback**: User-friendly status messages and loading indicators

## API Endpoints

### GET `/vehicle/decode/{vin}`
Decodes a VIN and returns vehicle information.

**Parameters:**
- `vin` (string): Vehicle Identification Number (10-17 characters)

**Response:**
```json
{
  "vin": "1HGBH41JXMN109186",
  "year": "1991",
  "make": "HONDA",
  "model": "ACCORD",
  "trim": "DX",
  "engine_displacement": "2.2",
  "transmission_type": "Automatic",
  "body_style": "Sedan",
  "fuel_type": "Gasoline",
  "drivetrain": "FWD",
  "country_of_origin": "USA",
  "plant_code": "H",
  "serial_number": "ACCORD"
}
```

### GET `/vehicle/health`
Health check endpoint for the vehicle data service.

**Response:**
```json
{
  "status": "healthy",
  "service": "vehicle_data"
}
```

## Frontend Integration

The module integrates with the automotive inspection form to provide:

1. **VIN Input Field**: Enhanced with search button and status indicators
2. **Auto-population**: Vehicle fields automatically fill when VIN is decoded
3. **Real-time Feedback**: Loading states and success/error messages
4. **Debounced Input**: Auto-decode VIN after user stops typing (1-second delay)

## Static VIN Data

The module includes static VIN data for offline operation with sample vehicles:

- 1991 Honda Accord DX
- 2006 Chevrolet Corvette Z06
- 2015 BMW 3 Series 328i
- 2015 Hyundai Sonata Sport

## Dependencies

- `httpx==0.25.2`: For async HTTP requests to NHTSA API
- `pydantic`: For data validation and serialization

## Usage

### Backend Integration

```python
from modules.vehicle_data.service import decode_vin

# Decode a VIN
vehicle_info = await decode_vin("1HGBH41JXMN109186")
print(f"Vehicle: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
```

### Frontend Integration

```javascript
// Decode VIN and auto-populate fields
async function decodeVIN() {
    const response = await fetch(`/vehicle/decode/${vin}`);
    const vehicleData = await response.json();
    
    if (response.ok && vehicleData) {
        // Auto-populate fields
        document.getElementById('year').value = vehicleData.year;
        document.getElementById('make').value = vehicleData.make;
        document.getElementById('model').value = vehicleData.model;
        // ... etc
    }
}
```

## Error Handling

The module handles various error scenarios:

- **Invalid VIN**: Returns minimal vehicle info with just the VIN
- **API Failures**: Falls back to static data
- **Network Issues**: Graceful degradation to offline mode
- **Missing Fields**: Preserves existing data when fields are not found

## Testing

Test VINs included in static data:
- `1HGBH41JXMN109186` - 1991 Honda Accord DX
- `1G1ZT51806F123456` - 2006 Chevrolet Corvette Z06
- `WBA3B5C50FD123456` - 2015 BMW 3 Series 328i
- `5NPE34AF4FH123456` - 2015 Hyundai Sonata Sport 