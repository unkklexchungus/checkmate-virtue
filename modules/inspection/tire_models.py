from typing import Optional, Dict, List
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime, timezone
from uuid import uuid4

class TirePos(str, Enum):
    LF = "LF"
    RF = "RF"
    LR = "LR"
    RR = "RR"
    SPARE = "SPARE"

class Light(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    NA = "NA"

class TireReading(BaseModel):
    psi_in: Optional[float] = None
    psi_out: Optional[float] = None
    tread_32nds: Optional[float] = None       # optional if you log tread here
    status: Light = Light.GREEN               # traffic-light for that tire

    @validator('psi_in', 'psi_out')
    def validate_psi(cls, v):
        if v is not None and (v < 0 or v > 80):
            raise ValueError('PSI must be between 0 and 80')
        return v

    @validator('tread_32nds')
    def validate_tread(cls, v):
        if v is not None and (v < 0 or v > 20):
            raise ValueError('Tread must be between 0 and 20 32nds')
        return v

class TireInspection(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique tire inspection ID")
    inspection_id: str = Field(..., description="Associated inspection ID")

    # Header rows on the card
    tire_front: Optional[str] = None          # e.g., "Michelin Primacy"
    tire_rear: Optional[str] = None
    size_front: Optional[str] = None          # if you separate size vs brand
    size_rear: Optional[str] = None
    speed_load_front: Optional[str] = None    # e.g., "94V"
    speed_load_rear: Optional[str] = None

    # Per-position readings
    readings: Dict[TirePos, TireReading] = Field(default_factory=dict)

    # Work checkboxes
    rotation: bool = False
    balance: bool = False
    maintenance: bool = False
    tire_wear_concern: bool = False

    # Alignment row has its own light
    alignment_check: Light = Light.GREEN

    # Right-hand checklist (boolean flags)
    # (Use common items from tire sheets)
    cond_even_wear: bool = False
    cond_inner_wear: bool = False
    cond_outer_wear: bool = False
    cond_center_wear: bool = False
    cond_cupping_feather: bool = False
    cond_sidewall_damage: bool = False
    cond_cracking_dryrot: bool = False
    cond_puncture_object: bool = False
    cond_bead_damage: bool = False
    cond_cords_visible: bool = False
    cond_noise_vibration: bool = False
    cond_age_over_6y: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_section_status(self) -> Light:
        """Calculate overall section status based on tire readings and alignment."""
        # Check for any RED tires first
        for reading in self.readings.values():
            if reading.status == Light.RED:
                return Light.RED
        
        # Check alignment RED
        if self.alignment_check == Light.RED:
            return Light.RED
        
        # Check for any YELLOW tires or alignment YELLOW
        has_yellow = any(reading.status == Light.YELLOW for reading in self.readings.values())
        if has_yellow or self.alignment_check == Light.YELLOW:
            return Light.YELLOW
        
        return Light.GREEN

    def auto_suggest_work_items(self):
        """Auto-suggest work items based on conditions."""
        suggestions = []
        
        # Check for uneven wear patterns
        if (self.cond_inner_wear or self.cond_outer_wear or 
            self.cond_center_wear or self.cond_cupping_feather):
            suggestions.append("rotation")
            suggestions.append("tire_wear_concern")
        
        # Check for alignment issues
        if self.alignment_check in [Light.YELLOW, Light.RED]:
            suggestions.append("balance")
        
        # Check for low tread
        for pos, reading in self.readings.items():
            if reading.tread_32nds is not None and reading.tread_32nds < 3:
                suggestions.append("maintenance")
                break
        
        return suggestions

class TireInspectionCreate(BaseModel):
    """Model for creating/updating tire inspections."""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    tire_front: Optional[str] = None
    tire_rear: Optional[str] = None
    size_front: Optional[str] = None
    size_rear: Optional[str] = None
    speed_load_front: Optional[str] = None
    speed_load_rear: Optional[str] = None
    readings: Dict[TirePos, TireReading] = Field(default_factory=dict)
    rotation: bool = False
    balance: bool = False
    maintenance: bool = False
    tire_wear_concern: bool = False
    alignment_check: Light = Light.GREEN
    cond_even_wear: bool = False
    cond_inner_wear: bool = False
    cond_outer_wear: bool = False
    cond_center_wear: bool = False
    cond_cupping_feather: bool = False
    cond_sidewall_damage: bool = False
    cond_cracking_dryrot: bool = False
    cond_puncture_object: bool = False
    cond_bead_damage: bool = False
    cond_cords_visible: bool = False
    cond_noise_vibration: bool = False
    cond_age_over_6y: bool = False
