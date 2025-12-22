# ROLLBACK PLAN - Partner Name Fix (2025-12-22)

## Emergency Rollback Procedure

If the partner name fix causes issues, follow these steps:

### Step 1: Stop Odoo Service
```bash
systemctl stop odoo-osusproperties.service
```

### Step 2: Restore Module Files
```bash
BACKUP_DIR=/var/odoo/backups/pre-partner-fix-20251222
cd /var/odoo/osusproperties/extra-addons
rm -rf payment_account_enhanced
tar -xzf $BACKUP_DIR/payment_account_enhanced.tar.gz
chown -R odoo:odoo payment_account_enhanced
```

### Step 3: Restore Database (If Critical Data Issue)
```bash
BACKUP_DIR=/var/odoo/backups/pre-partner-fix-20251222

# Stop Odoo and PostgreSQL
systemctl stop odoo-osusproperties.service
systemctl stop postgresql.service

# Restore database
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS osusproperties;
CREATE DATABASE osusproperties OWNER odoo;
EOF

# Restore from backup
cat $BACKUP_DIR/osusproperties_db.sql | sudo -u postgres psql -d osusproperties

# Restart services
systemctl start postgresql.service
systemctl start odoo-osusproperties.service
```

### Step 4: Verify Rollback
```bash
# Check service status
systemctl status odoo-osusproperties.service

# Check module version
ssh -p 22 root@139.84.163.11 "grep version /var/odoo/osusproperties/extra-addons/payment_account_enhanced/__manifest__.py"

# Verify database is accessible
ssh -p 22 root@139.84.163.11 "sudo -u odoo psql -d osusproperties -c 'SELECT id, name FROM ir_module_module WHERE name=\'payment_account_enhanced\';'"
```

## What Was Changed

### Files Modified
1. **payment_account_enhanced/models/res_partner.py**
   - Added `name_get()` override to remove "[Archived]" prefix
   - Returns clean partner names consistently

2. **payment_account_enhanced/views/account_move_views.xml**
   - Added/modified tree view inheritance records for clean display
   - Added clean name context for partner_id fields

3. **payment_account_enhanced/__manifest__.py**
   - Version bumped from 17.0.1.2.2 → 17.0.1.2.7
   - Added 'views/account_move_tree_overrides.xml' to data

### Database Records Created
- View record: `view_invoice_tree_enhanced` (inherits account.view_move_tree)
- View record: `view_out_invoice_tree_enhanced` (inherits account.view_out_invoice_tree)
- View record: `view_in_invoice_tree_enhanced` (inherits account.view_in_invoice_tree)

### NO Data Deletion or Modification
- No partner records deleted
- No invoice records modified
- No GL entries changed
- Only display logic and view architecture modified

## Backup Files Location

Server: `139.84.163.11` 
Path: `/var/odoo/backups/pre-partner-fix-20251222/`

- `osusproperties_db.sql` (245 MB) - Full database backup
- `payment_account_enhanced.tar.gz` (383 KB) - Module backup

## Testing Checklist Before Committing

- [ ] Refresh browser (Ctrl+F5)
- [ ] Open invoice list - check customer names display correctly
- [ ] Open a single invoice in form view
- [ ] Verify list and form show SAME customer name
- [ ] Check archived partners don't show "[Archived]" prefix
- [ ] Test filter by customer - still works
- [ ] Check PDF invoice generation - customer name correct
- [ ] Check accounting reports - partner names display correctly

## Contact Information

If rollback needed and system unresponsive:
1. Server: 139.84.163.11 (Port 22)
2. Database: osusproperties
3. Backup location: `/var/odoo/backups/pre-partner-fix-20251222/`
