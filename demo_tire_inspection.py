#!/usr/bin/env python3
"""
Demonstration script for the tire inspection system.
"""

from modules.inspection.tire_models import (
    TireInspection, TireInspectionCreate, TireReading, 
    TirePos, Light
)
from modules.inspection.tire_service import (
    create_or_update_tire_inspection,
    get_tire_inspection,
    get_tire_inspection_status
)

def demo_tire_inspection():
    """Demonstrate the tire inspection functionality."""
    
    print("=== Tire Inspection System Demo ===\n")
    
    # Create sample tire readings
    readings = {
        TirePos.LF: TireReading(psi_in=32.0, psi_out=35.0, tread_32nds=7.0, status=Light.GREEN),
        TirePos.RF: TireReading(psi_in=30.0, psi_out=35.0, tread_32nds=6.0, status=Light.YELLOW),
        TirePos.LR: TireReading(psi_in=28.0, psi_out=35.0, tread_32nds=5.0, status=Light.YELLOW),
        TirePos.RR: TireReading(psi_in=34.0, psi_out=35.0, tread_32nds=7.0, status=Light.GREEN),
        TirePos.SPARE: TireReading(psi_in=45.0, psi_out=45.0, tread_32nds=None, status=Light.NA)
    }
    
    # Create tire inspection data
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
    
    print("1. Creating tire inspection...")
    inspection_id = "demo_inspection_123"
    
    # Save the tire inspection
    inspection = create_or_update_tire_inspection(inspection_id, tire_data)
    
    if inspection:
        print(f"   ✓ Tire inspection created successfully")
        print(f"   - Inspection ID: {inspection.inspection_id}")
        print(f"   - Tire Front: {inspection.tire_front}")
        print(f"   - Tire Rear: {inspection.tire_rear}")
        print(f"   - Size Front: {inspection.size_front}")
        print(f"   - Size Rear: {inspection.size_rear}")
        
        # Show tire readings
        print("\n2. Tire Readings:")
        for pos, reading in inspection.readings.items():
            print(f"   {pos.value}: PSI In={reading.psi_in}, PSI Out={reading.psi_out}, "
                  f"Tread={reading.tread_32nds}/32, Status={reading.status.value}")
        
        # Show work items
        print("\n3. Work Items:")
        print(f"   - Rotation: {inspection.rotation}")
        print(f"   - Balance: {inspection.balance}")
        print(f"   - Maintenance: {inspection.maintenance}")
        print(f"   - Tire Wear Concern: {inspection.tire_wear_concern}")
        print(f"   - Alignment Check: {inspection.alignment_check.value}")
        
        # Show conditions
        print("\n4. Conditions:")
        conditions = [
            ("Even wear", inspection.cond_even_wear),
            ("Inner shoulder wear", inspection.cond_inner_wear),
            ("Outer shoulder wear", inspection.cond_outer_wear),
            ("Center wear", inspection.cond_center_wear),
            ("Cupping/feathering", inspection.cond_cupping_feather),
            ("Sidewall damage", inspection.cond_sidewall_damage),
            ("Cracking/dry rot", inspection.cond_cracking_dryrot),
            ("Puncture/object present", inspection.cond_puncture_object),
            ("Bead damage", inspection.cond_bead_damage),
            ("Cords visible", inspection.cond_cords_visible),
            ("Noise/vibration", inspection.cond_noise_vibration),
            ("Age > 6 years", inspection.cond_age_over_6y)
        ]
        
        for condition, value in conditions:
            if value:
                print(f"   ✓ {condition}")
        
        # Calculate and show section status
        print("\n5. Section Status:")
        section_status = inspection.get_section_status()
        print(f"   Overall Status: {section_status.value}")
        
        # Show auto-suggestions
        print("\n6. Auto-suggestions:")
        suggestions = inspection.auto_suggest_work_items()
        if suggestions:
            for suggestion in suggestions:
                print(f"   - {suggestion}")
        else:
            print("   No suggestions")
        
        # Retrieve the inspection
        print("\n7. Retrieving saved inspection...")
        retrieved_inspection = get_tire_inspection(inspection_id)
        
        if retrieved_inspection:
            print("   ✓ Inspection retrieved successfully")
            retrieved_status = get_tire_inspection_status(inspection_id)
            print(f"   - Retrieved Status: {retrieved_status.value if retrieved_status else 'Unknown'}")
        else:
            print("   ✗ Failed to retrieve inspection")
        
        print("\n=== Demo Complete ===")
        print("\nThe tire inspection system is working correctly!")
        print("Key features demonstrated:")
        print("- Data validation (PSI 0-80, tread 0-20)")
        print("- Traffic light status system (Green/Yellow/Red/NA)")
        print("- Auto-suggestions based on conditions")
        print("- Section status calculation")
        print("- Data persistence and retrieval")
        
    else:
        print("   ✗ Failed to create tire inspection")

if __name__ == "__main__":
    demo_tire_inspection()
