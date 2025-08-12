#!/bin/bash

# Update all services to remove auth dependencies
services=("workshop-service" "appointment-service" "inventory-service" "notification-service" "vehicle-service" "api-gateway")

for service in "${services[@]}"; do
    echo "Updating $service..."
    
    # Update main.py to remove auth_db references
    if [ -f "services/$service/app/main.py" ]; then
        # Replace auth_db with the appropriate db for each service
        case $service in
            "workshop-service")
                sed -i 's/auth_db/workshop_db/g' services/$service/app/main.py
                ;;
            "appointment-service")
                sed -i 's/auth_db/appointment_db/g' services/$service/app/main.py
                ;;
            "inventory-service")
                sed -i 's/auth_db/inventory_db/g' services/$service/app/main.py
                ;;
            "notification-service")
                sed -i 's/auth_db/notification_db/g' services/$service/app/main.py
                ;;
            "vehicle-service")
                sed -i 's/auth_db/vehicle_db/g' services/$service/app/main.py
                ;;
            "api-gateway")
                sed -i 's/auth_db/api_gateway_db/g' services/$service/app/main.py
                ;;
        esac
        
        # Remove any auth-related imports
        sed -i '/from _shared.utils.security import/d' services/$service/app/main.py
        sed -i '/from _shared.utils.security import/d' services/$service/app/api/*.py 2>/dev/null || true
    fi
    
    # Update any API files to remove auth dependencies
    if [ -d "services/$service/app/api" ]; then
        for api_file in services/$service/app/api/*.py; do
            if [ -f "$api_file" ]; then
                # Remove auth-related imports
                sed -i '/from _shared.utils.security import/d' "$api_file"
                # Remove current_user parameters from function definitions
                sed -i 's/, current_user: dict = Depends(get_current_user)//g' "$api_file"
                sed -i 's/current_user: dict = Depends(get_current_user), //g' "$api_file"
            fi
        done
    fi
done

echo "All services updated!"
