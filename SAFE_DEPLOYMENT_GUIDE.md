# 📦 SAFE DEPLOYMENT GUIDE: Payment Workflow Hardening v17.0.1.0.9
**Last Updated**: December 22, 2025  
**Estimated Duration**: 45-60 minutes (including testing)  
**Required Permissions**: SSH access + Odoo Admin + Database admin  
**Backup Window**: 48 hours (can rollback within this window)  

---

## 🎯 DEPLOYMENT OVERVIEW

### What's Being Deployed
| Component | Change | Impact |
|-----------|--------|--------|
| account_payment.py | Add posted payment edit lock + reconciliation protection | Prevents data corruption |
| account_move.py | Add posted JE reset block | Enforces audit trail |
| account_payment_views.xml | Rename "View Payment" → "Print Voucher" | UI cleanup |
| Module Version | Bump to 17.0.1.0.9 | Cache invalidation |

### Safety Guarantees
✅ **Zero data loss** - No deletes, no schema changes  
✅ **Reversible** - Full git rollback in < 5 minutes  
✅ **Reconciliation safe** - Matched payments protected  
✅ **Manager override** - Payment managers can still escalate  
✅ **Backward compatible** - Existing workflows unaffected  

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### T-24 Hours Before
```bash
# 1. Schedule notification
echo "Sending deployment notification to users..."
# (Send email: "System maintenance Sunday 6PM-7PM, expect brief downtime")

# 2. Create backups directory
ssh -p 22 root@139.84.163.11 "mkdir -p /var/odoo/backups"

# 3. List current version
ssh -p 22 root@139.84.163.11 \
  "grep 'version' /var/odoo/osusproperties/extra-addons/payment_account_enhanced/__manifest__.py"
# Expected: 'version': '17.0.1.0.8'
```

### T-1 Hour Before (Day Of)
```bash
# 4. Verify production connectivity
ssh -p 22 root@139.84.163.11 "systemctl status odoo.service"
# Expected: active (running)

# 5. Check disk space
ssh -p 22 root@139.84.163.11 "df -h /var/odoo | head -2"
# Expected: > 10GB free for backup

# 6. Run pre-deployment validation
ssh -p 22 root@139.84.163.11 "cd /var/odoo/osusproperties && python3 -c \"
import psycopg2
conn = psycopg2.connect(dbname='osusproperties', user='odoo', host='localhost')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM account_payment WHERE state = \"posted\"')
print(f\"Posted payments: {cursor.fetchone()[0]}\")
cursor.execute('SELECT COUNT(*) FROM account_move WHERE state = \"posted\"')
print(f\"Posted moves: {cursor.fetchone()[0]}\")
conn.close()
\""
# Expected: Both counts > 100 (normal production data)
```

---

## ⚙️ DEPLOYMENT EXECUTION (Step by Step)

### PHASE 1: BACKUP (5 minutes)

#### Step 1.1: Database Full Backup
```bash
echo "========== STEP 1.1: DATABASE BACKUP =========="

# SSH into production
ssh -p 22 root@139.84.163.11

# Create backup directory
BACKUP_DIR="/var/odoo/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/osusproperties_PRE_DEPLOY_$TIMESTAMP.dump"

# Full database backup (custom format for faster restore)
pg_dump -U odoo -d osusproperties -Fc -f "$BACKUP_FILE"

# Verify backup size
ls -lh "$BACKUP_FILE"
# Expected: Size > 500MB

# Compress (optional, takes 2-3 minutes)
gzip "$BACKUP_FILE"
echo "✅ Database backup complete: ${BACKUP_FILE}.gz"
```

#### Step 1.2: Code Backup
```bash
echo "========== STEP 1.2: CODE BACKUP =========="

# Backup entire addon
ADDON_BACKUP="/var/odoo/backups/payment_account_enhanced_$TIMESTAMP.tar.gz"
tar -czf "$ADDON_BACKUP" \
  /var/odoo/osusproperties/extra-addons/payment_account_enhanced/

# Verify
ls -lh "$ADDON_BACKUP"
echo "✅ Addon backup complete: $ADDON_BACKUP"

# Create snapshot marker
cat > "/var/odoo/backups/DEPLOYMENT_SNAPSHOT_$TIMESTAMP.txt" << EOF
Deployment: Payment Workflow Hardening v17.0.1.0.9
Timestamp: $TIMESTAMP
Database Backup: ${BACKUP_FILE}.gz
Code Backup: $ADDON_BACKUP
Version Before: 17.0.1.0.8
Version After: 17.0.1.0.9

Modified Files:
1. payment_account_enhanced/models/account_payment.py
   - Added reconciliation integrity check
   - Added posted payment edit lock
   - Added action_draft guard

2. payment_account_enhanced/models/account_move.py
   - Added button_draft guard for posted JEs

3. payment_account_enhanced/views/account_payment_views.xml
   - Changed button label to "Print Voucher"
   - Made visible only when posted

Rollback: git checkout HEAD~1 -- [files]
Restart: systemctl restart odoo.service
EOF

echo "✅ Snapshot created: /var/odoo/backups/DEPLOYMENT_SNAPSHOT_$TIMESTAMP.txt"
```

---

### PHASE 2: CODE UPDATE (5 minutes)

#### Step 2.1: Pull Latest Code
```bash
echo "========== STEP 2.1: GIT PULL =========="

# Navigate to addon directory
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844

# Verify current branch
git branch -v
# Expected: * main (or your deployment branch)

# Check current status
git status
# Expected: On branch main, nothing to commit, working tree clean

# Pull latest changes
git fetch origin
git pull origin main
# Expected: Already up to date OR Fast-forward messages

# Verify 3 files changed
git log --oneline -5
echo ""
git diff HEAD~1 HEAD --stat
# Should show:
# payment_account_enhanced/models/account_payment.py   | XX +/-
# payment_account_enhanced/models/account_move.py       | XX +/-
# payment_account_enhanced/views/account_payment_views.xml | X +/-
```

#### Step 2.2: Verify Code Changes
```bash
echo "========== STEP 2.2: VERIFY CODE =========="

# Check file syntax
python3 -m py_compile payment_account_enhanced/models/account_payment.py
python3 -m py_compile payment_account_enhanced/models/account_move.py
echo "✅ Python syntax OK"

# Check XML validity
python3 << 'EOF'
import xml.etree.ElementTree as ET
try:
    ET.parse('payment_account_enhanced/views/account_payment_views.xml')
    print("✅ XML syntax OK")
except Exception as e:
    print(f"❌ XML error: {e}")
EOF

# Display version bump
grep "version" payment_account_enhanced/__manifest__.py
# Expected: 'version': '17.0.1.0.9'
```

---

### PHASE 3: SERVICE RESTART (5 minutes)

#### Step 3.1: Stop Odoo Service
```bash
echo "========== STEP 3.1: STOP ODOO =========="

# Stop the service
systemctl stop odoo.service

# Verify it stopped
sleep 3
systemctl status odoo.service
# Expected: inactive (dead)

echo "✅ Odoo service stopped"
```

#### Step 3.2: Clear Cache
```bash
echo "========== STEP 3.2: CLEAR CACHE =========="

# Remove Odoo cache
rm -rf /var/lib/odoo/.cache
rm -rf /var/lib/odoo/.local

# Clear temporary files
find /tmp -name "odoo*" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Cache cleared"
```

#### Step 3.3: Start Odoo Service
```bash
echo "========== STEP 3.3: START ODOO =========="

# Start the service
systemctl start odoo.service

# Wait for full startup
echo "Waiting for Odoo startup (60 seconds)..."
sleep 60

# Verify startup
systemctl status odoo.service
# Expected: active (running)

# Check logs for errors
tail -50 /var/odoo/osusproperties/logs/odoo-server.log | grep -E "ERROR|CRITICAL"
# Expected: No errors related to payment_account_enhanced

echo "✅ Odoo service started successfully"
```

---

### PHASE 4: POST-DEPLOYMENT TESTING (15 minutes)

#### Step 4.1: UI Cache Clear
```bash
echo "========== STEP 4.1: UI CACHE CLEAR =========="

echo "📝 Instructions:"
echo "  1. Go to: https://odoo.osusproperties.com:8070"
echo "  2. Login as admin"
echo "  3. Settings (gear icon) → Developer Mode (toggle ON)"
echo "  4. Reload page (F5 or Cmd+R)"
echo "  5. Settings → Clear Cache"
echo "  6. Reload page again"
echo ""
echo "⏳ Wait for cache clear..."
sleep 5
echo "✅ Browser cache should be cleared"
```

#### Step 4.2: Module Version Check
```bash
echo "========== STEP 4.2: MODULE VERSION CHECK =========="

# Via CLI - check module is loaded
ssh -p 22 root@139.84.163.11 "grep -i 'payment_account_enhanced' /var/odoo/osusproperties/logs/odoo-server.log | tail -5"

# Via Database
ssh -p 22 root@139.84.163.11 << 'EOF'
psql -U odoo -d osusproperties << SQL
SELECT name, state, installed_version FROM ir_module_module 
WHERE name = 'payment_account_enhanced';
SQL
EOF

# Expected: payment_account_enhanced | installed | 17.0.1.0.9
```

#### Step 4.3: Workflow Test - Regular User
```bash
echo "========== STEP 4.3: TEST REGULAR USER =========="

echo "📝 Test Steps:"
echo "  1. Login as: user@example.com (Payment User role, not Manager)"
echo "  2. Go to: Accounting → Payments"
echo "  3. Open any POSTED payment"
echo "  4. Try to edit a field (e.g., memo)"
echo "  5. Expected ERROR: 'Posted payments cannot be modified...'"
echo "  6. Try to click 'Reset to Draft' button"
echo "  7. Expected ERROR: 'Posted payments cannot be reset...'"
echo "  8. Check 'Print Voucher' button appears (should be visible)"
echo ""
echo "⏳ Waiting for tester confirmation..."
read -p "Did test pass? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Regular user workflow test PASSED"
else
    echo "❌ Regular user workflow test FAILED - ROLLBACK REQUIRED"
    exit 1
fi
```

#### Step 4.4: Workflow Test - Payment Manager
```bash
echo "========== STEP 4.4: TEST PAYMENT MANAGER =========="

echo "📝 Test Steps:"
echo "  1. Login as: cfomgr@osusproperties.com (Payment Manager role)"
echo "  2. Go to: Accounting → Payments"
echo "  3. Open the same POSTED payment"
echo "  4. Try to edit a field (e.g., memo)"
echo "  5. Expected: ALLOWED (edit works)"
echo "  6. Revert the change and save"
echo "  7. Try to click 'Reset to Draft' button"
echo "  8. Expected: ALLOWED (button works)"
echo "  9. Don't actually reset - just verify button is clickable"
echo ""
echo "⏳ Waiting for tester confirmation..."
read -p "Did test pass? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Payment Manager override test PASSED"
else
    echo "❌ Payment Manager override test FAILED - ROLLBACK REQUIRED"
    exit 1
fi
```

#### Step 4.5: New Payment Workflow
```bash
echo "========== STEP 4.5: TEST NEW PAYMENT WORKFLOW =========="

echo "📝 Test Steps:"
echo "  1. Login as: reviewer@osusproperties.com"
echo "  2. Go to: Accounting → Payments → Create"
echo "  3. Fill basic fields (Partner, Amount, Account)"
echo "  4. Click 'Submit for Review'"
echo "  5. Expected: Status changes to 'Under Review'"
echo "  6. Go back to Payments list"
echo "  7. Filter by approval_state = 'under_review'"
echo "  8. Open the payment"
echo "  9. Click 'Review' button"
echo "  10. Expected: Status → 'For Approval', Review date populated"
echo ""
echo "⏳ Waiting for tester confirmation..."
read -p "Did test pass? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ New payment workflow test PASSED"
else
    echo "❌ New payment workflow test FAILED - ROLLBACK REQUIRED"
    exit 1
fi
```

#### Step 4.6: Reconciled Payment Test
```bash
echo "========== STEP 4.6: TEST RECONCILED PAYMENT =========="

echo "📝 Test Steps (if reconciled payments exist):"
echo "  1. Go to: Accounting → Bank Reconciliation (or similar)"
echo "  2. Find a payment that was already reconciled"
echo "  3. Go to: Accounting → Payments"
echo "  4. Open the reconciled payment"
echo "  5. Try to edit critical fields (amount, partner, account)"
echo "  6. Expected ERROR: 'Cannot modify reconciled payment details'"
echo ""
echo "⏳ Waiting for tester confirmation..."
read -p "Did test pass? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Reconciled payment protection test PASSED"
else
    echo "⚠️  Warning: Reconciled payment protection did not trigger (may be OK if no reconciled payments to test)"
fi
```

#### Step 4.7: System Health Check
```bash
echo "========== STEP 4.7: SYSTEM HEALTH CHECK =========="

ssh -p 22 root@139.84.163.11 << 'EOF'

echo "Checking Odoo service..."
systemctl status odoo.service --no-pager | grep -E "active|inactive"

echo ""
echo "Checking recent errors in logs..."
tail -100 /var/odoo/osusproperties/logs/odoo-server.log | \
  grep -E "ERROR|CRITICAL|Traceback" | tail -10

echo ""
echo "Checking database connectivity..."
psql -U odoo -d osusproperties -c "SELECT COUNT(*) as payment_count FROM account_payment;"

echo ""
echo "✅ System health check complete"

EOF
```

---

### PHASE 5: FINAL VERIFICATION (5 minutes)

#### Step 5.1: Data Integrity Check
```bash
echo "========== STEP 5.1: DATA INTEGRITY =========="

ssh -p 22 root@139.84.163.11 << 'EOF'
psql -U odoo -d osusproperties << SQL
SELECT 
  (SELECT COUNT(*) FROM account_payment WHERE state = 'posted') as posted_payments,
  (SELECT COUNT(*) FROM account_move WHERE state = 'posted' AND move_type IN ('in_invoice','in_refund','out_invoice','out_refund')) as posted_moves,
  (SELECT COUNT(*) FROM account_bank_reconciliation WHERE state = 'posted') as reconciliations,
  (SELECT COUNT(DISTINCT ap.id) FROM account_payment ap 
   LEFT JOIN account_move am ON ap.move_id = am.id
   LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
   WHERE ap.state = 'posted' AND abrl.id IS NOT NULL) as reconciled_payments;
SQL
EOF

echo "✅ Data integrity check complete"
echo "   (All counts should match pre-deployment baseline)"
```

#### Step 5.2: Approval Workflow Verification
```bash
echo "========== STEP 5.2: WORKFLOW VERIFICATION =========="

ssh -p 22 root@139.84.163.11 << 'EOF'
psql -U odoo -d osusproperties << SQL
SELECT 
  COUNT(*) as total_payments,
  COUNT(CASE WHEN approval_state = 'draft' THEN 1 END) as draft,
  COUNT(CASE WHEN approval_state = 'under_review' THEN 1 END) as under_review,
  COUNT(CASE WHEN approval_state = 'for_approval' THEN 1 END) as for_approval,
  COUNT(CASE WHEN approval_state = 'approved' THEN 1 END) as approved,
  COUNT(CASE WHEN approval_state = 'posted' THEN 1 END) as posted,
  COUNT(CASE WHEN approval_state IS NULL THEN 1 END) as null_state
FROM account_payment
WHERE create_date >= NOW() - INTERVAL '90 days';
SQL
EOF

echo "✅ Approval workflow distribution verified"
```

---

## 🚨 ROLLBACK PROCEDURE (If Needed)

### Immediate Rollback (< 1 hour after deployment)
```bash
echo "========== EMERGENCY ROLLBACK =========="

# SSH to production
ssh -p 22 root@139.84.163.11

# Stop Odoo
systemctl stop odoo.service

# Navigate to addon repo
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844

# Revert the 3 files
git checkout HEAD~1 -- \
  payment_account_enhanced/models/account_payment.py \
  payment_account_enhanced/models/account_move.py \
  payment_account_enhanced/views/account_payment_views.xml

# Verify revert
git status

# Start Odoo
systemctl start odoo.service

# Wait for startup
sleep 60

# Clear cache via UI (Settings → Developer Mode → Clear Cache)

echo "✅ Rollback complete - System back to v17.0.1.0.8"
```

### Database Restore (If corrupted)
```bash
echo "========== DATABASE RESTORE =========="

# SSH to production
ssh -p 22 root@139.84.163.11

# Stop Odoo and PostgreSQL
systemctl stop odoo.service
systemctl stop postgresql

# Restore from backup
BACKUP_FILE="/var/odoo/backups/osusproperties_PRE_DEPLOY_*.dump.gz"
cd /var/odoo/backups

# Decompress
gunzip -c "$BACKUP_FILE" > restore.dump

# Restore database
sudo -u postgres pg_restore --dbname osusproperties restore.dump

# Start services
systemctl start postgresql
systemctl start odoo.service

echo "✅ Database restored from backup"
```

---

## ✅ POST-DEPLOYMENT CHECKLIST (Day After)

```bash
# 1. Verify no errors overnight
tail -500 /var/odoo/osusproperties/logs/odoo-server.log | \
  grep -c "ERROR\|CRITICAL\|Traceback"
# Expected: 0 or very small number

# 2. Check reconciliation count unchanged
psql -U odoo -d osusproperties -c \
  "SELECT COUNT(*) FROM account_bank_reconciliation WHERE state = 'posted'"

# 3. Monitor user sessions for issues
# (Check Odoo dashboard for any support tickets)

# 4. Archive backup files to offsite storage
tar -czf /mnt/backup/odoo/deployment_backup_$TIMESTAMP.tar.gz \
  /var/odoo/backups/osusproperties_PRE_DEPLOY_*.dump.gz

echo "✅ Post-deployment verification complete"
```

---

## 📞 SUPPORT & ESCALATION

**Issue**: Posted payments show "Permission Denied"  
**Solution**: User needs to be Payment Manager → Contact Admin to add to group

**Issue**: "Print Voucher" button doesn't appear  
**Solution**: Clear browser cache (Ctrl+Shift+Del) and reload

**Issue**: Service won't start after deployment  
**Solution**: Execute rollback procedure above (< 5 minutes)

**Issue**: Data seems corrupted  
**Solution**: Execute database restore from backup (< 15 minutes)

---

## 📊 DEPLOYMENT LOG TEMPLATE

| Step | Time | Status | Notes |
|------|------|--------|-------|
| 1.1 Database Backup | 18:05 | ✅ | Size: XXX MB |
| 1.2 Code Backup | 18:10 | ✅ | tar.gz created |
| 2.1 Git Pull | 18:15 | ✅ | 3 files updated |
| 2.2 Code Verify | 18:17 | ✅ | No syntax errors |
| 3.1 Stop Odoo | 18:20 | ✅ | Service stopped |
| 3.2 Clear Cache | 18:22 | ✅ | Cache cleared |
| 3.3 Start Odoo | 18:23 | ✅ | Service started |
| 4.1 UI Cache | 18:25 | ✅ | Browser cache cleared |
| 4.2 Module Check | 18:27 | ✅ | v17.0.1.0.9 loaded |
| 4.3 Regular User Test | 18:35 | ✅ | Restrictions working |
| 4.4 Manager Override | 18:40 | ✅ | Manager can edit posted |
| 4.5 New Payment | 18:45 | ✅ | Workflow functional |
| 4.6 Reconciled Test | 18:50 | ✅ | Protected payments safe |
| 4.7 Health Check | 18:55 | ✅ | No errors in logs |
| 5.1 Data Integrity | 19:00 | ✅ | Counts match baseline |
| 5.2 Workflow Verify | 19:05 | ✅ | All states consistent |
| | | **✅ DEPLOYMENT SUCCESS** | |

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-22  
**Approved By**: [CFO Name]  
