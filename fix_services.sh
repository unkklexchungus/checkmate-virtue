#!/bin/bash

# Fix service configurations
services=(
    "appointment-service:appointment_db"
    "inventory-service:inventory_db"
    "notification-service:notification_db"
    "vehicle-service:vehicle_db"
    "api-gateway:api_gateway_db"
)

for service_config in "${services[@]}"; do
    service_name=$(echo $service_config | cut -d: -f1)
    db_name=$(echo $service_config | cut -d: -f2)
    
    echo "Fixing $service_name..."
    
    # Update main.py
    sed -i "s/workshop-service/$service_name/g" services/$service_name/app/main.py
    sed -i "s/workshop_db/$db_name/g" services/$service_name/app/main.py
    sed -i "s/Workshop Service/$service_name/g" services/$service_name/app/main.py
    
    # Update pyproject.toml
    sed -i "s/workshop-service/$service_name/g" services/$service_name/pyproject.toml
    sed -i "s/Workshop management service/$service_name service/g" services/$service_name/pyproject.toml
    
    echo "✅ Fixed $service_name"
done

echo "All services fixed!"
