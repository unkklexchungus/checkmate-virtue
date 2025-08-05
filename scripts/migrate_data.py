#!/usr/bin/env python3
"""
Data migration script for CheckMate Virtue refactoring.
Moves existing data from old structure to new modular structure.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

def migrate_inspections() -> None:
    """Migrate inspection data from old structure to new."""
    print("Migrating inspection data...")
    
    # Source files
    old_inspections_file = Path("data/inspections.json")
    old_templates_dir = Path("templates/industries")
    
    # Destination files
    new_inspections_file = Path("data/inspections.json")
    new_templates_dir = Path("app/templates/industries")
    
    # Ensure destination directories exist
    new_inspections_file.parent.mkdir(parents=True, exist_ok=True)
    new_templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate inspections data
    if old_inspections_file.exists():
        with open(old_inspections_file, 'r', encoding='utf-8') as f:
            inspections = json.load(f)
        
        # Save to new location
        with open(new_inspections_file, 'w', encoding='utf-8') as f:
            json.dump(inspections, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Migrated {len(inspections)} inspections")
    else:
        print("⚠ No inspections data found to migrate")
    
    # Migrate industry templates
    if old_templates_dir.exists():
        for template_file in old_templates_dir.glob("*.json"):
            dest_file = new_templates_dir / template_file.name
            shutil.copy2(template_file, dest_file)
            print(f"✓ Migrated template: {template_file.name}")
    else:
        print("⚠ No industry templates found to migrate")


def migrate_invoices() -> None:
    """Migrate invoice data from old structure to new."""
    print("Migrating invoice data...")
    
    # Source files
    old_invoices_file = Path("data/invoices.json")
    old_clients_file = Path("data/clients.json")
    
    # Destination files
    new_invoices_file = Path("data/invoices.json")
    new_clients_file = Path("data/clients.json")
    
    # Ensure destination directories exist
    new_invoices_file.parent.mkdir(parents=True, exist_ok=True)
    new_clients_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Migrate invoices data
    if old_invoices_file.exists():
        with open(old_invoices_file, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
        
        # Save to new location
        with open(new_invoices_file, 'w', encoding='utf-8') as f:
            json.dump(invoices, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Migrated {len(invoices)} invoices")
    else:
        print("⚠ No invoices data found to migrate")
    
    # Migrate clients data
    if old_clients_file.exists():
        with open(old_clients_file, 'r', encoding='utf-8') as f:
            clients = json.load(f)
        
        # Save to new location
        with open(new_clients_file, 'w', encoding='utf-8') as f:
            json.dump(clients, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Migrated {len(clients)} clients")
    else:
        print("⚠ No clients data found to migrate")


def migrate_static_files() -> None:
    """Migrate static files from old structure to new."""
    print("Migrating static files...")
    
    # Source directories
    old_static_dir = Path("static")
    old_uploads_dir = Path("static/uploads")
    
    # Destination directories
    new_static_dir = Path("app/static")
    new_uploads_dir = Path("app/static/uploads")
    
    # Ensure destination directories exist
    new_static_dir.mkdir(parents=True, exist_ok=True)
    new_uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate static files
    if old_static_dir.exists():
        for item in old_static_dir.iterdir():
            if item.is_file():
                dest_file = new_static_dir / item.name
                shutil.copy2(item, dest_file)
                print(f"✓ Migrated static file: {item.name}")
            elif item.is_dir() and item.name != "uploads":
                dest_dir = new_static_dir / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(item, dest_dir)
                print(f"✓ Migrated static directory: {item.name}")
    
    # Migrate uploads
    if old_uploads_dir.exists():
        for item in old_uploads_dir.iterdir():
            if item.is_dir():
                dest_dir = new_uploads_dir / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(item, dest_dir)
                print(f"✓ Migrated uploads directory: {item.name}")
    
    print("✓ Static files migration completed")


def migrate_templates() -> None:
    """Migrate HTML templates from old structure to new."""
    print("Migrating HTML templates...")
    
    # Source directory
    old_templates_dir = Path("templates")
    
    # Destination directory
    new_templates_dir = Path("app/templates")
    
    # Ensure destination directory exists
    new_templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate HTML templates
    if old_templates_dir.exists():
        for item in old_templates_dir.iterdir():
            if item.is_file() and item.suffix == '.html':
                dest_file = new_templates_dir / item.name
                shutil.copy2(item, dest_file)
                print(f"✓ Migrated template: {item.name}")
            elif item.is_dir():
                dest_dir = new_templates_dir / item.name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(item, dest_dir)
                print(f"✓ Migrated template directory: {item.name}")
    
    print("✓ Templates migration completed")


def migrate_vehicle_data() -> None:
    """Migrate vehicle data from old structure to new."""
    print("Migrating vehicle data...")
    
    # Source files
    old_vehicle_data_file = Path("modules/vehicle_data/static_vin_data.json")
    
    # Destination directory
    new_vehicle_data_dir = Path("app/data/vehicle")
    new_vehicle_data_file = new_vehicle_data_dir / "static_vin_data.json"
    
    # Ensure destination directory exists
    new_vehicle_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate vehicle data
    if old_vehicle_data_file.exists():
        shutil.copy2(old_vehicle_data_file, new_vehicle_data_file)
        print("✓ Migrated vehicle data")
    else:
        print("⚠ No vehicle data found to migrate")


def create_backup() -> None:
    """Create backup of original data."""
    print("Creating backup...")
    
    backup_dir = Path("backup_old_structure")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    # Backup key directories
    directories_to_backup = [
        "data",
        "static", 
        "templates",
        "modules"
    ]
    
    for dir_name in directories_to_backup:
        dir_path = Path(dir_name)
        if dir_path.exists():
            backup_path = backup_dir / dir_name
            shutil.copytree(dir_path, backup_path)
            print(f"✓ Backed up: {dir_name}")
    
    print(f"✓ Backup created at: {backup_dir}")


def main() -> None:
    """Main migration function."""
    print("🚀 Starting CheckMate Virtue Data Migration")
    print("=" * 50)
    
    try:
        # Create backup first
        create_backup()
        print()
        
        # Migrate data
        migrate_inspections()
        print()
        
        migrate_invoices()
        print()
        
        migrate_static_files()
        print()
        
        migrate_templates()
        print()
        
        migrate_vehicle_data()
        print()
        
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the new application structure")
        print("2. Update any hardcoded paths in your code")
        print("3. Remove old files after confirming everything works")
        print("4. Update your deployment configuration")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check the error and try again.")


if __name__ == "__main__":
    main() 