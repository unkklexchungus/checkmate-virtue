from pydantic import BaseModel
from typing import List, Optional

class InspectionItem(BaseModel):
    step: str
    subcategory: str
    item: str
    status: str  # pass/recommended/required
    notes: Optional[str] = None
    photo_url: Optional[str] = None

class InspectionCreate(BaseModel):
    vin: Optional[str] = None
    vehicle_id: Optional[int] = None
    items: List[InspectionItem] 