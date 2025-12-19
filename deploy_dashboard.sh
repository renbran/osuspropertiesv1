#!/bin/bash

# Deployment script for osus_sales_invoicing_dashboard module
# Uploads modified files to the server and triggers module upgrade

SERVER_USER="odoo"
SERVER_HOST="139.84.163.11"
SERVER_PATH="/mnt/odoo17/addons/osus_sales_invoicing_dashboard"
LOCAL_PATH="/mnt/d/RUNNING APPS/odoo17/osuspropertiesv1/osus_sales_invoicing_dashboard"

echo "[*] Deploying osus_sales_invoicing_dashboard (v17.0.1.0.4)"
echo "[*] Server: $SERVER_HOST"
echo "[*] Target: $SERVER_PATH"

# Upload manifest
echo "[*] Uploading __manifest__.py..."
scp -P 22 "$LOCAL_PATH/__manifest__.py" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"

# Upload Python models
echo "[*] Uploading models/sales_invoicing_dashboard.py..."
scp -P 22 "$LOCAL_PATH/models/sales_invoicing_dashboard.py" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/models/"

# Upload JavaScript files
echo "[*] Uploading dashboard_filters.js..."
scp -P 22 "$LOCAL_PATH/static/src/js/dashboard_filters.js" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/static/src/js/"

# Upload form view
echo "[*] Uploading dashboard_views.xml..."
scp -P 22 "$LOCAL_PATH/views/dashboard_views.xml" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/views/"

echo "[*] Files uploaded successfully"
echo "[*] Next steps:"
echo "    1. Log in to Odoo at http://139.84.163.11:8069"
echo "    2. Go to Apps > Update Apps List"
echo "    3. Search for 'OSUS Sales & Invoicing Dashboard'"
echo "    4. Click the module and select 'Upgrade'"
echo "    5. Test the dashboard filters"
