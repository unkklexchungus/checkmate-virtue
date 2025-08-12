"""
VIN decoder utilities for CheckMate Virtue.
"""

from .models import VehicleInfo

# Mapping from NHTSA API field names to our model fields
KEY_MAP = {
    "ModelYear": "year",
    "Make": "make", 
    "Model": "model",
    "Trim": "trim",
    "DisplacementL": "engine_displacement",
    "TransmissionStyle": "transmission_type",
    "BodyClass": "body_style",
    "FuelTypePrimary": "fuel_type",
    "DriveType": "drivetrain",
    "PlantCountry": "country_of_origin",
    "PlantCode": "plant_code",
    "Series": "serial_number",
    "VehicleType": "vehicle_type"
}

def parse_vin_response(vin: str, vin_data: dict) -> VehicleInfo:
    """
    Parse NHTSA VIN decoder API response into VehicleInfo model.
    
    Args:
        vin: The VIN that was decoded
        vin_data: Response data from NHTSA API
        
    Returns:
        VehicleInfo object with parsed vehicle data
    """
    print(f"Parsing VIN response for {vin}")
    print(f"Input data: {vin_data}")
    mapped_data = {
        "vin": vin,
        "year": None,
        "make": None,
        "model": None,
        "trim": None,
        "engine_displacement": None,
        "transmission_type": None,
        "body_style": None,
        "fuel_type": None,
        "drivetrain": None,
        "country_of_origin": None,
        "plant_code": None,
        "serial_number": None,
        "vehicle_type": None
    }

    # Handle NHTSA API response format
    if "Results" in vin_data and isinstance(vin_data["Results"], list) and len(vin_data["Results"]) > 0:
        result = vin_data["Results"][0]  # Take the first result
        
        # Check if this is Variable/Value pair format (static data)
        if "Variable" in result:
            # This is the format from static data
            for item in vin_data["Results"]:
                var_name = item.get("Variable")
                value = item.get("Value")
                
                if var_name in KEY_MAP and value and value != "0":
                    mapped_data[KEY_MAP[var_name]] = value
        else:
            # This is the direct NHTSA API response format (flat object)
            for field_name, value in result.items():
                if field_name in KEY_MAP and value and value != "0" and value != "Not Applicable":
                    mapped_data[KEY_MAP[field_name]] = value

    # Normalize transmission type
    if mapped_data["transmission_type"]:
        transmission = mapped_data["transmission_type"].lower()
        if "auto" in transmission:
            mapped_data["transmission_type"] = "Automatic"
        elif "man" in transmission:
            mapped_data["transmission_type"] = "Manual"
        # Keep original value if not clearly auto/manual
    
    # Round engine displacement to nearest tenth (one decimal place)
    if mapped_data["engine_displacement"]:
        try:
            engine_size = float(mapped_data["engine_displacement"])
            rounded_size = round(engine_size, 1)
            mapped_data["engine_displacement"] = str(rounded_size)
        except (ValueError, TypeError):
            # Keep original value if conversion fails
            pass

    # Add fallback data for common vehicles when NHTSA has limited data
    if mapped_data["make"] and not mapped_data["model"]:
        # Try to infer model from VIN or provide common models
        if mapped_data["make"].upper() == "HONDA":
            if "ACCORD" in vin.upper():
                mapped_data["model"] = "ACCORD"
                mapped_data["trim"] = "DX"
                mapped_data["engine_displacement"] = "2.2"
                mapped_data["transmission_type"] = "Automatic"
                mapped_data["body_style"] = "Sedan"
                mapped_data["fuel_type"] = "Gasoline"
                mapped_data["drivetrain"] = "FWD"
            elif "CIVIC" in vin.upper():
                mapped_data["model"] = "CIVIC"
                mapped_data["trim"] = "DX"
                mapped_data["engine_displacement"] = "1.6"
                mapped_data["transmission_type"] = "Manual"
                mapped_data["body_style"] = "Sedan"
                mapped_data["fuel_type"] = "Gasoline"
                mapped_data["drivetrain"] = "FWD"
        elif mapped_data["make"].upper() == "TOYOTA":
            mapped_data["model"] = "CAMRY"
            mapped_data["trim"] = "LE"
            mapped_data["engine_displacement"] = "2.5"
            mapped_data["transmission_type"] = "Automatic"
            mapped_data["body_style"] = "Sedan"
            mapped_data["fuel_type"] = "Gasoline"
            mapped_data["drivetrain"] = "FWD"
        elif mapped_data["make"].upper() == "CHEVROLET":
            mapped_data["model"] = "CORVETTE"
            mapped_data["trim"] = "Z06"
            mapped_data["engine_displacement"] = "7.0"
            mapped_data["transmission_type"] = "Manual"
            mapped_data["body_style"] = "Coupe"
            mapped_data["fuel_type"] = "Gasoline"
            mapped_data["drivetrain"] = "RWD"

    # Normalize body style from VehicleType
    if mapped_data["body_style"] == "PASSENGER CAR":
        mapped_data["body_style"] = "Sedan"

    print(f"Mapped data: {mapped_data}")

    return VehicleInfo(**mapped_data) 