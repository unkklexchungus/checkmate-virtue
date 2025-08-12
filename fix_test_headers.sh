#!/bin/bash

# Remove auth headers from test API calls
echo "Removing auth headers from test API calls..."

# Remove headers parameter from API calls
sed -i 's/, headers=headers//g' test_system.py
sed -i 's/headers=headers, //g' test_system.py

echo "Auth headers removed from test API calls!"
