"""
VIN decoder utilities for CheckMate Virtue.
"""

from .models import VehicleInfo

# Mapping from NHTSA API field names to our model fields
KEY_MAP = {
    "Model Year": "year",
    "Make": "make", 
    "Model": "model",
    "Trim": "trim",
    "Displacement (L)": "engine_displacement",
    "Transmission Style": "transmission_type",
    "Body Style": "body_style",
    "Fuel Type - Primary": "fuel_type",
    "Drive Type": "drivetrain",
    "Plant Country": "country_of_origin",
    "Plant Code": "plant_code",
    "Series": "serial_number"
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
        "serial_number": None
    }

    # Parse the Results array from NHTSA API
    for item in vin_data.get("Results", []):
        var_name = item.get("Variable")
        value = item.get("Value")
        
        if var_name in KEY_MAP and value and value != "0":
            mapped_data[KEY_MAP[var_name]] = value

    # Normalize transmission type
    if mapped_data["transmission_type"]:
        transmission = mapped_data["transmission_type"].lower()
        if "auto" in transmission:
            mapped_data["transmission_type"] = "Automatic"
        elif "man" in transmission:
            mapped_data["transmission_type"] = "Manual"
        # Keep original value if not clearly auto/manual

    return VehicleInfo(**mapped_data) 