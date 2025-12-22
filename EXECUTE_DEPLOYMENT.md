# 🚀 PRODUCTION DEPLOYMENT EXECUTION GUIDE

## ⚠️ FINAL PRE-EXECUTION CHECKLIST

Before running any commands, confirm ALL items:

- [ ] **Business Approval**: Finance Manager has approved deployment
- [ ] **Maintenance Window**: Scheduled and users notified (recommended: 2-3 AM)
- [ ] **Backups**: Recent full database backup exists and verified
- [ ] **Team Assigned**: DevOps, QA, and Finance Manager present during deployment
- [ ] **Rollback Plan**: Team has read ROLLBACK_PLAN_v2_PAYMENT_HARDENING.md
- [ ] **Execution Log**: Print or open DEPLOYMENT_EXECUTION_LOG_TEMPLATE.md
- [ ] **Test Plan**: COMPREHENSIVE_TEST_CHECKLIST.md ready for post-deployment testing
- [ ] **Database Access**: Confirmed access to 139.84.163.11 (SSH key/password ready)
- [ ] **Network**: No maintenance scheduled for 139.84.163.11 in next 4 hours

**Proceed Only If ALL Boxes Are Checked** ✅

---

## 📍 STEP 1: PRE-DEPLOYMENT VALIDATION (LOCAL)

**Time Estimate**: 5 minutes  
**Location**: Your workstation (Windows)  

### Step 1.1: Verify Code Files
```bash
# Open File Explorer and verify these 3 files exist in workspace:
✓ payment_account_enhanced/models/account_payment.py
✓ payment_account_enhanced/models/account_move.py
✓ payment_account_enhanced/views/account_payment_views.xml
```

### Step 1.2: Read Code Changes (Verify no unexpected modifications)
```bash
# Quick sanity check - these should be the ONLY changes:
# In account_payment.py:
#   - Lines 30-40: _is_payment_reconciled() method
#   - Lines 593-654: write() with reconciliation guard
#   - Lines 1052-1062: action_draft() guard

# In account_move.py:
#   - Lines 147-157: button_draft() method

# In account_payment_views.xml:
#   - Line 45: Button label changed, visibility restricted
```

### Step 1.3: Verify Version in __manifest__.py
```python
# The version MUST be exactly: '17.0.1.0.9'
# Open: payment_account_enhanced/__manifest__.py
# Look for: 'version': '17.0.1.0.9',
```

**✅ Step 1 Complete**: All code verified locally

---

## 📍 STEP 2: CONNECT TO PRODUCTION SERVER

**Time Estimate**: 2 minutes  
**Requirements**: SSH access to 139.84.163.11

### Step 2.1: SSH into Production
```bash
# Windows PowerShell or PuTTY:
ssh root@139.84.163.11

# Password: [Enter your production SSH password]
# Expected prompt: root@osus-prod:/var/odoo/osusproperties#
```

### Step 2.2: Verify Server Health
```bash
# Check service status
systemctl status odoo.service

# Expected output: active (running)
# If not running: systemctl start odoo.service
```

**✅ Step 2 Complete**: Connected to production, Odoo is running

---

## 📍 STEP 3: EXECUTE PRE-DEPLOYMENT VALIDATION

**Time Estimate**: 10 minutes  
**Location**: Production server (SSH session)  
**Document**: PRE_DEPLOYMENT_VALIDATION.md contains all queries  

### Step 3.1: Run SQL Validation Queries
```bash
# Connect to PostgreSQL
sudo -u odoo psql -d osusproperties

# Run Query 1: Payment State Distribution
SELECT approval_state, COUNT(*) as count 
FROM account_payment 
WHERE create_date >= NOW() - INTERVAL '180 days' 
GROUP BY approval_state 
ORDER BY count DESC;

# Expected: Should show payments across multiple states (draft, review, approved, posted)
# Make note of:
# - Posted payments count: __________
# - Draft payments count: __________
# - Total payments: __________
```

### Step 3.2: Run Query 2: Reconciliation Count
```bash
# Still in psql:
SELECT COUNT(*) as total_reconciliations 
FROM account_bank_reconciliation_line 
WHERE reconciliation_date IS NOT NULL;

# Expected: >= 100 (large number)
# Record: __________

# CRITICAL: This number should NOT change after deployment
```

### Step 3.3: Run Query 3: Reconciled Payments Baseline
```bash
# Still in psql:
SELECT COUNT(*) as reconciled_payments 
FROM account_payment ap 
WHERE EXISTS (
  SELECT 1 FROM account_bank_reconciliation_line 
  WHERE payment_id = ap.id AND match_status = 'matched'
);

# Expected: >= 50
# **RECORD THIS NUMBER**: __________

# THIS IS CRITICAL - it must NOT decrease after deployment
```

### Step 3.4: Run Query 4: Payment Manager Verification
```bash
# Still in psql:
SELECT u.login, u.name 
FROM res_users u 
JOIN res_groups_users_rel gur ON gur.uid = u.id 
JOIN res_groups g ON g.id = gur.gid 
WHERE g.name = 'Payment Manager';

# Expected: Should return at least 1 user
# Names: __________
```

### Step 3.5: Exit SQL and Continue
```bash
# Exit psql
\q

# Back to root prompt
```

**📋 Record These Critical Baseline Numbers**:
- Posted payments: __________
- Reconciled payments: __________
- Total payment records: __________
- Payment Manager users: __________

**✅ Step 3 Complete**: Baseline captured, ready for deployment

---

## 📍 STEP 4: CREATE BACKUPS

**Time Estimate**: 15-30 minutes  
**Location**: Production server (SSH session)  
**Critical**: Do NOT skip this step

### Step 4.1: Create Database Backup
```bash
# Create backup directory if not exists
mkdir -p /var/odoo/backups

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create database dump
sudo -u odoo pg_dump -d osusproperties -Fc -v -f /var/odoo/backups/osusproperties_BEFORE_DEPLOY_${TIMESTAMP}.dump

# Expected: File will be created, may take 5-10 minutes
# Watch for: "Dumping data for table..." messages

# Verify backup size
ls -lh /var/odoo/backups/osusproperties_BEFORE_DEPLOY_${TIMESTAMP}.dump

# Expected: File should be > 100MB (normal database size)
# Backup file size: __________
```

### Step 4.2: Create Code Backup
```bash
# Backup current addon
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/

# Create tar backup
tar -czf /var/odoo/backups/payment_account_enhanced_BEFORE_DEPLOY_${TIMESTAMP}.tar.gz payment_account_enhanced/

# Verify
ls -lh /var/odoo/backups/payment_account_enhanced_BEFORE_DEPLOY_${TIMESTAMP}.tar.gz

# Expected: > 1MB
# Backup file size: __________
```

### Step 4.3: Create Snapshot Marker
```bash
# Create marker file with deployment metadata
cat > /var/odoo/backups/DEPLOYMENT_SNAPSHOT_${TIMESTAMP}.txt <<EOF
Deployment Snapshot
Created: $(date)
Server: 139.84.163.11
Database: osusproperties
Module: payment_account_enhanced
Version: 17.0.1.0.9
Operator: $(whoami)
EOF

# Verify
cat /var/odoo/backups/DEPLOYMENT_SNAPSHOT_${TIMESTAMP}.txt
```

**✅ Step 4 Complete**: Backups created and verified

---

## 📍 STEP 5: DEPLOY CODE CHANGES

**Time Estimate**: 5 minutes  
**Location**: Production server (SSH session)  
**Critical**: Code changes are small (3 files only)

### Step 5.1: Navigate to Git Repository
```bash
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/

# Check current status
git status

# Expected output: Should show modified files for payment_account_enhanced
```

### Step 5.2: Review Changes (Final Verification)
```bash
# See what will be deployed
git diff payment_account_enhanced/

# Should show ONLY these 3 files changed:
# - payment_account_enhanced/models/account_payment.py
# - payment_account_enhanced/models/account_move.py
# - payment_account_enhanced/views/account_payment_views.xml

# If other files show as modified: **STOP** and contact support
```

### Step 5.3: Commit Changes
```bash
git add payment_account_enhanced/

git commit -m "Payment Workflow Hardening v17.0.1.0.9 - Production Deployment

- Add reconciliation integrity protection
- Block posted payment edits for non-managers  
- Block posted JE draft reset for non-managers
- UI: Rename 'View Payment' to 'Print Voucher'
- Clear error messages for workflow protection

Deployment: $(date)
Operator: $(whoami)"
```

### Step 5.4: Push to Git
```bash
git push

# Expected: Changes are now in git repository
# Confirmation: "master ... -> master"
```

### Step 5.5: Verify Deployment
```bash
# Check manifest version
cat payment_account_enhanced/__manifest__.py | grep version

# Expected output: 'version': '17.0.1.0.9',
```

**✅ Step 5 Complete**: Code deployed to Git

---

## 📍 STEP 6: STOP ODOO SERVICE

**Time Estimate**: 1 minute  
**Location**: Production server (SSH session)  
**⚠️ Users will be disconnected now**

### Step 6.1: Stop Odoo Service
```bash
# Stop Odoo
systemctl stop odoo.service

# Verify it stopped
sleep 3
systemctl status odoo.service

# Expected: inactive (dead) or stopped
# Wait for full stop: __________
```

### Step 6.2: Clear Cache
```bash
# Clear Python cache
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /var/odoo -name "*.pyc" -delete

# Clear session cache
rm -rf /var/lib/odoo/.cache 2>/dev/null || true
rm -rf /var/lib/odoo/.local 2>/dev/null || true

# Clear Odoo temporary files
find /tmp -name "odoo*" -type d -exec rm -rf {} + 2>/dev/null || true

# Expected: Cache directories removed
echo "Cache cleared"
```

**✅ Step 6 Complete**: Odoo stopped, caches cleared

---

## 📍 STEP 7: START ODOO SERVICE

**Time Estimate**: 30-60 seconds  
**Location**: Production server (SSH session)

### Step 7.1: Start Service
```bash
# Start Odoo
systemctl start odoo.service

# Monitor startup
sleep 5
systemctl status odoo.service

# Expected: active (running)
# Startup time: __________
```

### Step 7.2: Monitor Logs
```bash
# Watch logs for 30 seconds
tail -f /var/odoo/osusproperties/logs/odoo-server.log &

# Wait 30 seconds, then stop with: Ctrl+C

# Then check for errors
tail -50 /var/odoo/osusproperties/logs/odoo-server.log | grep -i "error\|critical\|exception"

# Expected: No payment_account_enhanced errors
# Errors found: __________
```

### Step 7.3: Verify Service Health
```bash
# Check process is running
ps aux | grep odoo | grep -v grep

# Expected: Should see odoo process
# Status: __________
```

**✅ Step 7 Complete**: Odoo started and running

---

## 📍 STEP 8: VERIFY DEPLOYMENT IN DATABASE

**Time Estimate**: 5 minutes  
**Location**: Production server (SSH session)

### Step 8.1: Check Module Installation
```bash
sudo -u odoo psql -d osusproperties -c \
"SELECT name, state, installed_version FROM ir_module_module 
WHERE name = 'payment_account_enhanced';"

# Expected output:
# name                    | state     | installed_version
# ----------------------- | --------- | ---------
# payment_account_enhanced| installed | 17.0.1.0.9

# If not showing 17.0.1.0.9: Module may need to be upgraded
```

### Step 8.2: Reconciliation Count Check
```bash
# Verify reconciliation count is UNCHANGED
sudo -u odoo psql -d osusproperties -c \
"SELECT COUNT(*) as reconciled_payments 
FROM account_payment ap 
WHERE EXISTS (
  SELECT 1 FROM account_bank_reconciliation_line 
  WHERE payment_id = ap.id AND match_status = 'matched'
);"

# Expected: Should match Step 3.3 baseline
# Current count: __________
# Baseline count: __________
# Match: ☐ YES ☐ NO (If NO = ROLLBACK!)
```

### Step 8.3: Payment Count Check
```bash
# Total payments check
sudo -u odoo psql -d osusproperties -c \
"SELECT COUNT(*) FROM account_payment;"

# Expected: Should match or be higher than baseline
# Current count: __________
# Baseline count: __________
# Match: ☐ YES ☐ NO (If LOWER = ROLLBACK!)
```

**⚠️ CRITICAL**: If reconciled payments count DECREASED, ROLLBACK IMMEDIATELY!
```bash
# Rollback command (only if needed):
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/
git revert HEAD
systemctl restart odoo.service
```

**✅ Step 8 Complete**: Deployment verified, data intact

---

## 📍 STEP 9: RUN FUNCTIONAL TESTS

**Time Estimate**: 10 minutes  
**Location**: Production Odoo UI (web browser)

### Test 9.1: Access Odoo
```
URL: https://139.84.163.11/web
Login: admin / [password]
Expected: Dashboard loads, no errors
Status: ☐ PASS ☐ FAIL
```

### Test 9.2: Navigate to Payment List
```
Menu: Accounting > Payables > Payments
Expected: Payment list loads with data
Visible columns should include: 
  - Name, Partner, Amount, State, Approval State
Status: ☐ PASS ☐ FAIL
```

### Test 9.3: Open Posted Payment
```
Click on any "Posted" payment
Expected: Form opens, buttons visible
Status: ☐ PASS ☐ FAIL
```

### Test 9.4: Check "Print Voucher" Button
```
Look for button: "Print Voucher" (previously "View Payment")
Expected: Button should be visible and renamed
Location: Bottom of form, with group restrictions
Status: ☐ PASS ☐ FAIL
```

### Test 9.5: Verify Access Restrictions (Regular User)
```
Login as: Regular user (not Payment Manager)
Navigate to: Posted payment
Try to: Click Edit button
Expected: Edit button should be read-only or disabled
Status: ☐ PASS ☐ FAIL
```

### Test 9.6: Verify Manager Override (Payment Manager)
```
Login as: Payment Manager user
Navigate to: Posted payment
Try to: Click Edit button
Expected: Edit button should work (with warnings about reconciliation)
Status: ☐ PASS ☐ FAIL
```

**✅ Step 9 Complete**: Core functionality verified

---

## 📍 STEP 10: RUN COMPREHENSIVE TEST SUITE

**Time Estimate**: 30-60 minutes  
**Location**: Follow COMPREHENSIVE_TEST_CHECKLIST.md  
**Assigned To**: QA/Testing team member

### Actions:
1. Open [COMPREHENSIVE_TEST_CHECKLIST.md](COMPREHENSIVE_TEST_CHECKLIST.md)
2. Follow each test case in sequence
3. Document results in the checklist
4. Sign off when all tests pass

### Key Tests (Must Pass):
- ✅ Test 1: Regular User Edit Restriction
- ✅ Test 2: Manager Override Works
- ✅ Test 3: New Payment Workflow
- ✅ Test 4: Reconciled Payment Protection
- ✅ Test 5: Print Voucher Button
- ... (23 more tests)

**Expected Duration**: 30-60 minutes  
**Expected Result**: 26/26 tests passing  

**✅ Step 10 Complete**: All tests passed

---

## 📍 STEP 11: DOCUMENT DEPLOYMENT

**Time Estimate**: 10 minutes  
**Location**: Your workstation  

### Actions:
1. Open [DEPLOYMENT_EXECUTION_LOG_TEMPLATE.md](DEPLOYMENT_EXECUTION_LOG_TEMPLATE.md)
2. Fill in all sections with actual values from deployment
3. Record baseline numbers, test results, any issues
4. Get sign-off from:
   - DevOps/System Admin
   - Finance Manager
   - QA Lead
5. Save and archive

**✅ Step 11 Complete**: Deployment documented

---

## ✅ DEPLOYMENT COMPLETE

### Confirm All Steps:
- ☐ Step 1: Code verified locally
- ☐ Step 2: Connected to production
- ☐ Step 3: Pre-deployment validation passed
- ☐ Step 4: Backups created and verified
- ☐ Step 5: Code deployed
- ☐ Step 6: Odoo stopped
- ☐ Step 7: Odoo restarted
- ☐ Step 8: Data integrity verified
- ☐ Step 9: Functional tests passed
- ☐ Step 10: Comprehensive tests passed
- ☐ Step 11: Deployment documented

### Success Metrics:
✅ All deployment phases completed  
✅ All critical data counts match baseline  
✅ All 26 tests passed  
✅ No error messages in logs  
✅ Payment workflow protections active  
✅ Manager override working  
✅ Reconciliation integrity intact  

---

## 📞 NEXT STEPS (Post-Deployment)

### Immediate (0-4 hours):
- ✅ Monitor logs: `tail -f /var/odoo/osusproperties/logs/odoo-server.log`
- ✅ Watch for user complaints
- ✅ Verify finance team can still process payments

### 24-Hour Window:
- ✅ Run COMPREHENSIVE_TEST_CHECKLIST again
- ✅ Verify no data loss
- ✅ Check system performance (no slowdowns)
- ✅ Confirm Payment Manager group is using override features

### 1-Week Window:
- ✅ Review logs for any payment-related errors
- ✅ Validate that non-managers cannot edit posted payments
- ✅ Verify reconciliation workflow still functional
- ✅ Get sign-off from Finance Manager

---

## ⚠️ IF SOMETHING GOES WRONG

### Immediate Action: ROLLBACK

See [ROLLBACK_PLAN_v2_PAYMENT_HARDENING.md](ROLLBACK_PLAN_v2_PAYMENT_HARDENING.md) for detailed procedures

Quick rollback (< 5 minutes):
```bash
# SSH to production
ssh root@139.84.163.11

# Revert code changes
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/
git revert HEAD --no-edit
git push

# Restart service
systemctl restart odoo.service

# Verify rollback
systemctl status odoo.service
tail /var/odoo/osusproperties/logs/odoo-server.log
```

### If Database Rollback Needed (15-20 minutes):
```bash
# Stop Odoo
systemctl stop odoo.service

# Restore database from backup
TIMESTAMP=[TIMESTAMP_FROM_BACKUP]
sudo -u odoo pg_restore -d osusproperties /var/odoo/backups/osusproperties_BEFORE_DEPLOY_${TIMESTAMP}.dump

# Restart service
systemctl start odoo.service
```

---

## 📋 DEPLOYMENT CHECKLIST

Print this and check off each item:

**Pre-Deployment**
- [ ] Business approval obtained
- [ ] Maintenance window scheduled
- [ ] Team members assigned
- [ ] Backups verified
- [ ] Documentation reviewed

**Execution**
- [ ] Code verified locally
- [ ] Connected to production server
- [ ] Baseline data captured
- [ ] Backups created
- [ ] Code deployed
- [ ] Service restarted
- [ ] Data integrity verified
- [ ] Tests executed

**Post-Deployment**
- [ ] All tests passed
- [ ] Logs reviewed
- [ ] Team sign-off obtained
- [ ] Deployment documented
- [ ] 24-hour monitoring started

**Success Criteria**
- [ ] ✅ Payment workflow protections active
- [ ] ✅ Manager override working
- [ ] ✅ No data loss
- [ ] ✅ No errors in logs
- [ ] ✅ Users can still process payments
- [ ] ✅ Finance team satisfied

---

**Ready to Deploy?** Execute each step in sequence, document everything, and reach out if you encounter any issues.

Good luck! 🚀
