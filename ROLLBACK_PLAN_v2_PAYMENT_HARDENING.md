# 🔄 ROLLBACK PLAN: Payment Workflow Hardening (v17.0.1.0.9)
**Date**: December 22, 2025  
**Deployment Window**: Low-traffic period (evening/weekend)  
**Rollback Complexity**: MEDIUM  
**Estimated Rollback Time**: 15-20 minutes  

---

## 📋 EXECUTIVE SUMMARY

This document provides a complete rollback procedure for the payment workflow hardening deployment that:
- Locks posted payments from unauthorized edits
- Prevents resetting posted journal entries to draft
- Adds reconciliation integrity checks
- Renames "View Payment" button to "Print Voucher"

**Key Safety Feature**: All changes are **code-level only** (no database schema changes), making rollback straightforward.

---

## 🔍 CHANGES DEPLOYED

### File 1: `payment_account_enhanced/models/account_payment.py`
**Lines**: 593-654 (merged write methods with posted guard + QR generation)  
**Lines**: 1052-1062 (added action_draft guard)  
**Change Type**: Added 2 new enforcement blocks + consolidated write() method

**Guard 1** - Write Method (lines 593-654):
```python
# Hard guard: block edits on posted payments unless Payment Manager/System Admin
if any(rec.state == 'posted' for rec in self):
    allowed = self.env.user.has_group('payment_account_enhanced.group_payment_manager') or \
              self.env.user.has_group('account.group_system')
    if not allowed:
        raise ValidationError(...)
```

**Guard 2** - action_draft Method (lines 1052-1062):
```python
def action_draft(self):
    """Block resetting posted vouchers to draft unless Payment Manager/System Admin"""
    for payment in self:
        if payment.state == 'posted':
            allowed = self.env.user.has_group('payment_account_enhanced.group_payment_manager') or \
                      self.env.user.has_group('account.group_system')
            if not allowed:
                raise ValidationError(...)
    return super(AccountPayment, self).action_draft()
```

### File 2: `payment_account_enhanced/models/account_move.py`
**Lines**: 147-157 (added button_draft guard)  
**Change Type**: New method to prevent posting JE draft reset without manager

**Guard 3** - button_draft Method:
```python
def button_draft(self):
    """Disallow resetting posted entries unless Payment Manager/System Admin"""
    for move in self:
        if move.state == 'posted':
            allowed = self.env.user.has_group('payment_account_enhanced.group_payment_manager') or \
                      self.env.user.has_group('account.group_system')
            if not allowed:
                raise UserError(...)
    return super(AccountMove, self).button_draft()
```

### File 3: `payment_account_enhanced/views/account_payment_views.xml`
**Line**: 45 (changed button label + visibility)  
**From**: `<button name="action_print_payment_voucher" string="View Payment" ... invisible="approval_state not in ['approved', 'posted']"/>`  
**To**: `<button name="action_print_payment_voucher" string="Print Voucher" ... invisible="approval_state != 'posted'" groups="account.group_account_user"/>`

---

## 🛡️ DATA INTEGRITY SAFEGUARDS

### No Breaking Changes:
✅ **No schema modifications** - No database column/table changes  
✅ **No data deletion** - All payment/invoice records preserved  
✅ **Backward compatible** - Code validates but doesn't alter existing data  
✅ **Reconciliation-safe** - No touches to `account.bank.reconciliation` or matched records  

### Reconciliation Protection:
- Payments/invoices with matched bank reconciliations **remain intact**
- `account.bank.reconciliation_ids` relationships **untouched**
- `account.move` records linked to reconciliations **persist unchanged**
- No cascade deletes or orphan creation possible

---

## 🚨 ROLLBACK PROCEDURES

### **IMMEDIATE ROLLBACK (if errors occur within 1 hour)**

#### **Option A: Revert via Git (Recommended)**
```bash
# SSH into production server
ssh -p 22 root@139.84.163.11

# Stop Odoo service
systemctl stop odoo.service

# Navigate to addon directory
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844

# Revert all 3 files to previous version
git checkout HEAD~1 -- payment_account_enhanced/models/account_payment.py
git checkout HEAD~1 -- payment_account_enhanced/models/account_move.py
git checkout HEAD~1 -- payment_account_enhanced/views/account_payment_views.xml

# Verify rollback
git status
# Output should show: modified, deleted (if we added files)

# Start Odoo
systemctl start odoo.service

# Clear cache by accessing Odoo UI: Settings → Activate Developer Mode → Clear Cache
```

#### **Option B: Manual File Restore (if git unavailable)**
```bash
# Stop Odoo
systemctl stop odoo.service

# Restore from backup (create backup before deployment!)
cp /var/odoo/backups/payment_account_enhanced_BACKUP_20251222.tar.gz /tmp/
tar -xzf /tmp/payment_account_enhanced_BACKUP_20251222.tar.gz -C /var/odoo/osusproperties/extra-addons/

# Start Odoo
systemctl start odoo.service
```

#### **Option C: Database Module Reset (if UI accessible)**
```sql
-- SSH and connect to PostgreSQL
ssh -p 22 root@139.84.163.11
psql -U odoo -d osusproperties

-- Uninstall and reinstall the module
UPDATE ir_module_module SET state = 'uninstalled' 
WHERE name = 'payment_account_enhanced';

-- Exit and restart Odoo
-- Then reinstall via UI: Apps → Payment Account Enhanced → Install
```

---

### **DEFERRED ROLLBACK (if issues appear after 1+ hour)**

#### **Step 1: Identify Issue**
```sql
-- Check for failed payments/invoices
SELECT id, name, state, approval_state, created_at 
FROM account_payment 
WHERE created_at > NOW() - INTERVAL '1 hour'
  AND state = 'posted'
LIMIT 20;

-- Check for unreconciled movements (should be empty)
SELECT COUNT(*) as orphan_count FROM account_move 
WHERE id NOT IN (SELECT move_id FROM account_bank_reconciliation_line 
                 WHERE move_id IS NOT NULL)
  AND state = 'posted'
  AND name LIKE 'BNK%';  -- Bank statement lines
```

#### **Step 2: Backup Current Database**
```bash
# Full database backup before rollback
pg_dump -U odoo -d osusproperties > /var/odoo/backups/osusproperties_PRE_ROLLBACK_$(date +%s).sql

# Compress if needed
gzip /var/odoo/backups/osusproperties_PRE_ROLLBACK_*.sql
```

#### **Step 3: Revert Code**
```bash
# Use Option A (Git revert) from above
git checkout HEAD~1 -- payment_account_enhanced/models/account_payment.py
git checkout HEAD~1 -- payment_account_enhanced/models/account_move.py
git checkout HEAD~1 -- payment_account_enhanced/views/account_payment_views.xml
```

#### **Step 4: Module Reinstall**
```bash
# From SSH
systemctl restart odoo.service

# Wait for service startup (60 seconds)
sleep 60

# Force module update (this will re-load old code)
# Via psql:
psql -U odoo -d osusproperties
UPDATE ir_module_module 
SET state = 'to_upgrade' 
WHERE name = 'payment_account_enhanced';
```

#### **Step 5: Verify Recovery**
```sql
-- Check that payments can be edited again
SELECT id, name, state FROM account_payment 
WHERE state = 'posted' LIMIT 5;

-- Try reset to draft (should work for managers)
-- Via UI: Open posted payment → Button "Reset to Draft" should appear again

-- Verify no data loss
SELECT COUNT(*) as total_payments FROM account_payment;
SELECT COUNT(*) as reconciled FROM account_move 
WHERE id IN (SELECT move_id FROM account_bank_reconciliation_line 
             WHERE move_id IS NOT NULL);
```

---

## 📊 PRE-DEPLOYMENT VALIDATION

### Database Health Check
```sql
-- Run before deployment to establish baseline
psql -U odoo -d osusproperties

-- Check reconciliation integrity
SELECT 
  COUNT(DISTINCT am.id) as total_posted_moves,
  COUNT(DISTINCT CASE WHEN br.id IS NOT NULL THEN am.id END) as reconciled_moves,
  COUNT(DISTINCT CASE WHEN br.id IS NULL THEN am.id END) as unreconciled_moves
FROM account_move am
LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
LEFT JOIN account_bank_reconciliation br ON abrl.reconciliation_id = br.id
WHERE am.state = 'posted';

-- Result should show all reconciled items linked properly
```

### Payment State Consistency
```sql
-- Verify no orphaned payment records
SELECT 
  COUNT(*) as total_payments,
  COUNT(CASE WHEN state = 'posted' THEN 1 END) as posted_count,
  COUNT(CASE WHEN state = 'draft' THEN 1 END) as draft_count,
  COUNT(CASE WHEN state = 'cancelled' THEN 1 END) as cancelled_count
FROM account_payment
WHERE date >= NOW() - INTERVAL '30 days';

-- Expected: All counts > 0, no orphaned records
```

---

## ✅ BACKUP STRATEGY

### Pre-Deployment Backup
```bash
# 1. Database backup
pg_dump -U odoo -d osusproperties -Fc -f /var/odoo/backups/osusproperties_$(date +%Y%m%d_%H%M%S).dump

# 2. Code backup (entire addon directory)
tar -czf /var/odoo/backups/payment_account_enhanced_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/odoo/osusproperties/extra-addons/payment_account_enhanced/

# 3. Create snapshot label
echo "Backup created before payment hardening deployment v17.0.1.0.9 on $(date)" \
  > /var/odoo/backups/DEPLOYMENT_SNAPSHOT_20251222.txt

# 4. Verify backup
pg_dump -U odoo -d osusproperties --schema-only | wc -l  # Should show schema count
ls -lh /var/odoo/backups/osusproperties_*.dump  # Verify file exists and has size > 1MB
```

### Backup Storage
- **Primary**: `/var/odoo/backups/` on production server
- **Secondary**: Weekly sync to `/mnt/backup/odoo/` (if external mounted)
- **Archive**: Keep last 5 backups, delete older ones

### Recovery Time Objective (RTO)
- **Database restore**: 5-10 minutes
- **Code revert**: 2-3 minutes
- **Service restart**: 2 minutes
- **Total RTO**: ~15 minutes

---

## 🚀 DEPLOYMENT CHECKLIST

### Before Deployment
- [ ] Schedule during low-traffic window (evening 6PM - 8PM AED / Sunday)
- [ ] Notify users: "System maintenance 6PM-7PM, brief unavailability expected"
- [ ] Create full database backup
- [ ] Create addon code backup
- [ ] Document current version numbers from `__manifest__.py`
- [ ] Test changes locally in Docker environment first
- [ ] Get approval from Finance/CFO for payment workflow changes

### During Deployment
- [ ] Stop Odoo service: `systemctl stop odoo.service`
- [ ] Pull latest code: `git pull origin main`
- [ ] Verify 3 files changed: `git status`
- [ ] Start Odoo: `systemctl start odoo.service`
- [ ] Wait 60 seconds for full startup
- [ ] Clear Odoo cache via UI (Settings → Developer Mode → Clear Cache)
- [ ] Verify module: Apps → search "Payment Account Enhanced" → should show v17.0.1.0.9

### After Deployment (1st hour)
- [ ] Test as Payment Manager: Create payment → Post → Try to edit (should be blocked)
- [ ] Test as regular user: Try to edit posted payment (should fail with message)
- [ ] Test payment reset to draft (should fail for non-managers)
- [ ] Test invoice posting workflow (should work normally)
- [ ] Check logs: `tail -100 /var/odoo/osusproperties/logs/odoo-server.log`
- [ ] Monitor for errors (no ValidationError spam)

### After Deployment (24 hours)
- [ ] Verify no failed payments in queue
- [ ] Check reconciliation count unchanged: `SELECT COUNT(*) FROM account_bank_reconciliation`
- [ ] Review approval workflow emails sent successfully
- [ ] Confirm no "Posted payment locked" complaints from users
- [ ] Archive pre-deployment backups to offline storage

---

## 🔐 ROLLBACK DECISION CRITERIA

**Roll back immediately if:**
1. ❌ Users cannot create new payments (critical)
2. ❌ Posted payments show orphaned reconciliations (data integrity)
3. ❌ Accounting users locked out from legitimate payment edits
4. ❌ Manager approval workflow broken (cannot approve payments)
5. ❌ Invoice posting failing due to new guards
6. ❌ Service crashing with "ImportError" or "SyntaxError" from modified files
7. ❌ > 5% of users unable to perform normal operations

**Can tolerate / fix in place:**
- ✅ Button label display issue ("Print Voucher" appears incorrectly) → Quick XML fix
- ✅ User doesn't see "Print Voucher" button → Adjust group permissions
- ✅ Minor log warnings about workflow validation → Not blocking
- ✅ Manager requests to edit posted payment → Already allowed per design

---

## 📞 CONTACT & ESCALATION

**Deployment Manager**: [CFO/System Admin Name]  
**Backup Contact**: [Secondary Admin Name]  
**Expected Issue Resolution Time**: 15-30 minutes (via rollback)

**In case of critical failure:**
1. ✅ Execute rollback procedure (Option A recommended)
2. ✅ Notify Finance team of revert
3. ✅ Investigate root cause in development environment
4. ✅ Schedule 2nd deployment attempt after fixes (48-72 hours later)

---

## 📝 ROLLBACK EXECUTION LOG

Use this table to document actual rollback (if needed):

| Timestamp | Action | Status | Notes |
|-----------|--------|--------|-------|
| 2025-12-22 18:00 | Database backup created | ✅ | Size: XXX MB |
| 2025-12-22 18:05 | Code pulled from git | ✅ | 3 files changed |
| 2025-12-22 18:10 | Odoo service restarted | ✅ | Startup successful |
| 2025-12-22 18:15 | Module cache cleared | ✅ | Via UI |
| 2025-12-22 18:30 | Testing passed | ✅ | All workflow checks OK |
| 2025-12-22 19:00 | Issue detected | ❌ | Describe issue here... |
| 2025-12-22 19:05 | Rollback initiated | 🔄 | Using Git revert |
| 2025-12-22 19:20 | Service restarted | ✅ | Recovery complete |
| 2025-12-22 19:25 | Verification passed | ✅ | Data integrity confirmed |

---

## 🎯 SUCCESS CRITERIA (Post-Deployment)

✅ **Payment workflow hardening deployed successfully when:**
1. Posted payments cannot be edited by regular users (error displayed)
2. Payment Managers CAN edit posted payments without error
3. Posted journal entries cannot be reset to draft (except for managers)
4. "Print Voucher" button shows only for posted payments
5. All reconciled payments remain intact (count unchanged)
6. No data loss in any tables
7. Approval workflow functions normally
8. No orphaned reconciliation records created
9. Users can still create and approve payments normally
10. System logs show no critical errors related to payment module

---

**Document Version**: 2.0  
**Last Updated**: 2025-12-22  
**Next Review**: After first successful deployment  
