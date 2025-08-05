"""
VIN decoder utilities for CheckMate Virtue.
"""

from app.models import VehicleInfo

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
        "serial_number": None,
    }

    # Handle both old static data format and new NHTSA API format
    if "Results" in vin_data and isinstance(vin_data["Results"], list):
        if len(vin_data["Results"]) > 0:
            # Check if this is the old static data format (with Variable/Value pairs)
            first_result = vin_data["Results"][0]
            if "Variable" in first_result and "Value" in first_result:
                # Old static data format with Results array
                for item in vin_data.get("Results", []):
                    var_name = item.get("Variable")
                    value = item.get("Value")

                    if var_name in KEY_MAP and value and value != "0":
                        mapped_data[KEY_MAP[var_name]] = value
            else:
                # New NHTSA API format - flat object with field names as keys
                result = vin_data["Results"][0]

                for api_field, model_field in KEY_MAP.items():
                    value = result.get(api_field)
                    if value and value != "" and value != "0":
                        mapped_data[model_field] = value

    # Normalize transmission type
    if mapped_data["transmission_type"]:
        transmission = mapped_data["transmission_type"].lower()
        if "auto" in transmission:
            mapped_data["transmission_type"] = "Automatic"
        elif "man" in transmission:
            mapped_data["transmission_type"] = "Manual"
        # Keep original value if not clearly auto/manual

    return VehicleInfo(**mapped_data)
