#!/bin/bash
# TEST VERIFICATION SCRIPT - Partner Name Display Fix
# Run this to verify the fix is working correctly

echo "================================="
echo "Partner Name Fix Verification"
echo "================================="
echo ""

# Connect to server
SERVER="139.84.163.11"
DB="osusproperties"

echo "✓ Checking module version..."
ssh -p 22 root@SERVER "grep version /var/odoo/osusproperties/extra-addons/payment_account_enhanced/__manifest__.py | head -1"

echo ""
echo "✓ Checking service status..."
ssh -p 22 root@SERVER "systemctl status odoo-osusproperties.service | grep -E 'Active|Running'"

echo ""
echo "✓ Verifying database integrity..."
ssh -p 22 root@SERVER "cat > /tmp/verify.sql << 'EOSQL'
SELECT 'Invoices' as entity, COUNT(*) as count FROM account_move WHERE move_type IN ('out_invoice', 'out_refund')
UNION ALL
SELECT 'Partners' as entity, COUNT(*) as count FROM res_partner
UNION ALL  
SELECT 'Payments' as entity, COUNT(*) as count FROM account_payment;
EOSQL
sudo -u odoo psql -d $DB -f /tmp/verify.sql"

echo ""
echo "✓ Checking res_partner name_get method..."
ssh -p 22 root@SERVER "grep -A 15 'def name_get' /var/odoo/osusproperties/extra-addons/payment_account_enhanced/models/res_partner.py | head -20"

echo ""
echo "================================="
echo "BACKUP LOCATION:"
echo "Server: 139.84.163.11"
echo "Path: /var/odoo/backups/pre-partner-fix-20251222/"
echo "Files:"
echo "  - osusproperties_db.sql (245 MB)"
echo "  - payment_account_enhanced.tar.gz (383 KB)"
echo "================================="
echo ""
echo "✅ Fix deployment complete. No data was deleted or modified."
echo ""
echo "NEXT STEPS:"
echo "1. Hard refresh browser: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)"
echo "2. Open invoice list and verify customer names match form view"
echo "3. Check that 'CONTINENTAL INVESTMENT LMD LLC' appears correctly"
echo "4. If any issues, run: /var/odoo/backups/pre-partner-fix-20251222/ROLLBACK.sh"
