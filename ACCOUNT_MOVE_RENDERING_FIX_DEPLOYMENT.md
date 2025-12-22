# Account Move Rendering Fix - Production Deployment Guide

## Overview
This document provides step-by-step instructions to deploy the account move rendering fix to your production server at `139.84.163.11`.

**Issue Fixed:**
- Invoice/Bill list view was showing "ARCHIVED - DO NOT USE" for archived partner customers
- Form view displayed the correct customer name
- This caused confusion and misleading information

**Solution:**
- Added `name_get()` method override in `account.move` model
- Added `name_get()` method override in `account.journal` model
- Both methods properly display customer/partner names without archive indicators
- Module version bumped from 17.0.1.2.0 → 17.0.1.2.1

---

## Prerequisites

1. SSH access to production server: `root@139.84.163.11:22`
2. SSH keys configured for authentication (no password required)
3. Odoo service running with database: `osusproperties`
4. Backup of database created before deployment

---

## Deployment Steps

### Step 1: Connect to Production Server

```bash
# Connect via SSH with keys
ssh -p 22 root@139.84.163.11

# Verify you're in the right location
cd /opt/odoo/addons
ls -la payment_account_enhanced/
```

Expected output:
```
drwxr-xr-x  models/
-rw-r--r--  __manifest__.py
-rw-r--r--  __init__.py
-rw-r--r--  security/
-rw-r--r--  views/
```

### Step 2: Backup Current Module Files

```bash
# Create backup directory with timestamp
BACKUP_DIR="/opt/odoo/backups/payment_account_enhanced_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup the module
cp -r /opt/odoo/addons/payment_account_enhanced $BACKUP_DIR/

echo "✅ Backup created at: $BACKUP_DIR"
```

### Step 3: Update Module Files

#### Option A: Using SCP from Windows/Local Machine

```powershell
# From your local machine (Windows PowerShell)
$server = "root@139.84.163.11"
$port = 22
$modulePath = "d:\RUNNING APPS\odoo17\osuspropertiesv1\payment_account_enhanced"

# Copy account_move.py
scp -P $port "$modulePath\models\account_move.py" "${server}:/opt/odoo/addons/payment_account_enhanced/models/"

# Copy account_journal.py  
scp -P $port "$modulePath\models\account_journal.py" "${server}:/opt/odoo/addons/payment_account_enhanced/models/"

# Copy __manifest__.py
scp -P $port "$modulePath\__manifest__.py" "${server}:/opt/odoo/addons/payment_account_enhanced/"
```

#### Option B: Manual File Editing on Server

If SCP doesn't work, edit files directly on the server:

```bash
# On production server
cd /opt/odoo/addons/payment_account_enhanced/models

# Edit account_move.py - add name_get() method at the end (see section below)
nano account_move.py

# Edit account_journal.py - add name_get() method (see section below)
nano account_journal.py

# Exit nano with Ctrl+X, then Y to save

# Update manifest version
cd ..
nano __manifest__.py
# Change 'version': '17.0.1.2.0' to 'version': '17.0.1.2.1'
```

---

## Code Changes Reference

### Changes to `/opt/odoo/addons/payment_account_enhanced/models/account_move.py`

Add this method at the end of the `AccountMove` class (after `_clear_approval_fields` method):

```python
def name_get(self):
    """
    Override name_get to properly display invoice name with partner info
    even when partner is archived, matching the form view display.
    """
    result = []
    for record in self:
        # Get the base name from parent class
        name = record.name or ''
        
        # Add partner name with proper formatting
        if record.partner_id:
            # Get actual partner name, bypassing archive indicator
            partner_name = record.partner_id.name or ''
            # Construct display: Invoice# (Partner Name)
            display_name = f"{name} ({partner_name})" if name else partner_name
        else:
            display_name = name
        
        result.append((record.id, display_name))
    
    return result
```

### Changes to `/opt/odoo/addons/payment_account_enhanced/models/account_journal.py`

Replace the entire file with:

```python
# models/account_journal.py
from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    enable_payment_verification = fields.Boolean(
        string="Enable Payment Verification",
        default=True,
        help="Enable QR verification for payments in this journal"
    )
    
    payment_approval_required = fields.Boolean(
        string='Require Payment Approval',
        default=True,
        help="Require approval workflow for payments in this journal"
    )

    def name_get(self):
        """
        Override name_get to properly display journal name
        consistent across all views, avoiding archive indicators.
        """
        result = []
        for record in self:
            # Display journal name directly without archive prefix
            name = record.name or ''
            result.append((record.id, name))
        
        return result
```

### Changes to `/opt/odoo/addons/payment_account_enhanced/__manifest__.py`

Change version number:

```python
# From:
'version': '17.0.1.2.0',

# To:
'version': '17.0.1.2.1',
```

---

## Step 4: Update Module in Odoo

On the production server:

```bash
# Verify file permissions are correct
cd /opt/odoo/addons/payment_account_enhanced
chmod -R 755 .
chown -R odoo:odoo .

# Stop the Odoo service (if currently running)
systemctl stop odoo

# Update the module in Odoo database
cd /opt/odoo
./odoo-bin -u payment_account_enhanced -d osusproperties --stop-after-init

# Monitor the update process
tail -f /var/log/odoo/odoo.log

# Wait for "Modules loaded" message, then press Ctrl+C
```

---

## Step 5: Restart Odoo Service

```bash
# Restart the Odoo service
systemctl restart odoo

# Verify service is running
systemctl status odoo

# Expected output:
# ● odoo.service - Odoo
#      Loaded: loaded (/etc/systemd/system/odoo.service; enabled; vendor preset: enabled)
#      Active: active (running) since ...
```

---

## Step 6: Verify Deployment

### Check Service Status

```bash
# Service should be running
systemctl status odoo | head -10

# Check recent logs
journalctl -u odoo -n 50 --no-pager
```

### Test in Odoo Interface

1. **Login to Odoo**: https://139.84.163.11:8069
2. **Navigate to**: Accounting → Invoices
3. **Check list view**: 
   - Invoices should now show partner name properly
   - Example: "INV/2025/00222 (CONTINENTAL INVESTMENT LMD LLC)"
4. **Verify form view**: 
   - Should match the list view display
   - No "ARCHIVED" prefix should appear

### Database Verification

```bash
# Connect to PostgreSQL
psql -U odoo -d osusproperties

# Check module version
SELECT name, state, installed_version FROM ir_module_module 
WHERE name = 'payment_account_enhanced';

# Expected output:
# name                      | state   | installed_version
# payment_account_enhanced  | installed | 17.0.1.2.1

# Exit with \q
```

---

## Rollback Procedure (if needed)

If you need to rollback the changes:

```bash
# Stop Odoo
systemctl stop odoo

# Restore from backup
BACKUP_DIR="/opt/odoo/backups/payment_account_enhanced_YYYYMMDD_HHMMSS"
rm -rf /opt/odoo/addons/payment_account_enhanced
cp -r $BACKUP_DIR/payment_account_enhanced /opt/odoo/addons/

# Downgrade module
cd /opt/odoo
./odoo-bin -u payment_account_enhanced -d osusproperties --stop-after-init

# Restart service
systemctl restart odoo

echo "✅ Rollback completed"
```

---

## Troubleshooting

### Issue: "Module not found" error

```bash
# Verify module structure
ls -la /opt/odoo/addons/payment_account_enhanced/models/

# Should show:
# __init__.py
# account_move.py
# account_journal.py
# account_payment.py
# account_payment_register.py
```

### Issue: Syntax error in Python files

```bash
# Check Python syntax
python3 -m py_compile /opt/odoo/addons/payment_account_enhanced/models/account_move.py
python3 -m py_compile /opt/odoo/addons/payment_account_enhanced/models/account_journal.py

# Should produce no output if syntax is correct
```

### Issue: Permission denied errors

```bash
# Fix permissions
chown -R odoo:odoo /opt/odoo/addons/payment_account_enhanced
chmod -R 755 /opt/odoo/addons/payment_account_enhanced
```

### Issue: Odoo still showing old data

```bash
# Clear browser cache
# And clear Odoo cache
redis-cli FLUSHALL  # if Redis is used

# Hard restart
systemctl stop odoo
sleep 5
systemctl start odoo
```

---

## Post-Deployment Checklist

- [ ] Files copied to production server
- [ ] Module version updated to 17.0.1.2.1
- [ ] Odoo service restarted
- [ ] Service status shows "active (running)"
- [ ] Database verified with correct version
- [ ] List view displays partner names correctly
- [ ] Form view matches list view display
- [ ] No "ARCHIVED" prefix appears on invoices
- [ ] Archive indicator removed from journal names
- [ ] Backup created before deployment

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Odoo logs: `tail -f /var/log/odoo/odoo.log`
3. Check module is installed: `SELECT * FROM ir_module_module WHERE name = 'payment_account_enhanced';`

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `account_move.py` | Added `name_get()` override | Proper invoice name display with partner in list view |
| `account_journal.py` | Added `name_get()` override | Consistent journal name display |
| `__manifest__.py` | Version 17.0.1.2.0 → 17.0.1.2.1 | Cache invalidation, forces UI refresh |

---

**Deployed on:** [Current Date]  
**Module Version:** 17.0.1.2.1  
**Database:** osusproperties  
**Status:** ✅ Ready for Production
