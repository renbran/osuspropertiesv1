#!/bin/bash
# Emergency deployment script for clear_cache fix
# Run this on the production server

set -e  # Exit on error

echo "==========================================="
echo "Deploying clear_cache AttributeError Fix"
echo "==========================================="

# Navigate to repository
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844

echo "[1/7] Checking current git status..."
git status

echo "[2/7] Fetching latest changes from GitHub..."
git fetch origin

echo "[3/7] Pulling latest changes..."
git pull origin main

echo "[4/7] Verifying fix is applied..."
if grep -q "clear_cache" osus_sales_invoicing_dashboard/models/sales_invoicing_dashboard.py; then
    echo "WARNING: clear_cache still found in file!"
    grep -n "clear_cache" osus_sales_invoicing_dashboard/models/sales_invoicing_dashboard.py
else
    echo "✓ Fix verified - no clear_cache calls found"
fi

echo "[5/7] Clearing Python cache..."
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "[6/7] Restarting Odoo service..."
sudo systemctl restart odona-osusproperties.service

echo "[7/7] Checking service status..."
sudo systemctl status odona-osusproperties.service --no-pager

echo ""
echo "==========================================="
echo "✓ Deployment Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Clear browser cache (Ctrl+Shift+R)"
echo "2. Test at https://erp.erposus.com"
echo "3. Verify no AttributeError appears"
echo ""
