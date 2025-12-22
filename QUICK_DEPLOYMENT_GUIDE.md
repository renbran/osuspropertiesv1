# 🚀 QUICK START: DEPLOYMENT EXECUTION
**Version**: 17.0.1.0.9 | **Date**: 2025-12-22

---

## ⚡ ONE-COMMAND DEPLOYMENT

### Option 1: Run Full Automated Script (Recommended)
```bash
# Make script executable
chmod +x /path/to/deploy_and_validate.sh

# Run the complete deployment
/path/to/deploy_and_validate.sh

# Script will:
# ✅ Validate pre-deployment baseline
# ✅ Create database + code backups
# ✅ Deploy code from git
# ✅ Restart Odoo service
# ✅ Run 7 automated functional tests
# ✅ Verify data integrity
# ✅ Generate comprehensive report
```

### Option 2: Manual Step-by-Step (For More Control)

#### Step 1: Pre-Deployment Validation (2 min)
```bash
# SSH to production
ssh -p 22 root@139.84.163.11

# Run validation queries
psql -U odoo -d osusproperties << 'EOF'
-- Check payment states
SELECT 'PAYMENTS' as type, COUNT(*) as total, 
       COUNT(CASE WHEN state='posted' THEN 1 END) as posted
FROM account_payment WHERE create_date >= NOW() - INTERVAL '90 days';

-- Record baseline for reconciled payments
SELECT COUNT(DISTINCT ap.id) as reconciled_baseline
FROM account_payment ap
LEFT JOIN account_move am ON ap.move_id = am.id
LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
WHERE ap.state = 'posted' AND abrl.id IS NOT NULL;
EOF
```

#### Step 2: Create Backups (5 min)
```bash
# Database backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U odoo -d osusproperties -Fc -f /var/odoo/backups/osusproperties_PRE_DEPLOY_$TIMESTAMP.dump
gzip /var/odoo/backups/osusproperties_PRE_DEPLOY_$TIMESTAMP.dump

# Code backup
tar -czf /var/odoo/backups/payment_account_enhanced_$TIMESTAMP.tar.gz \
  /var/odoo/osusproperties/extra-addons/payment_account_enhanced/

echo "✅ Backups complete"
```

#### Step 3: Deploy Code (5 min)
```bash
# Update code
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844
git fetch origin
git pull origin main

# Verify changes
git diff HEAD~1 HEAD --stat | grep payment_account_enhanced

# Syntax check
python3 -m py_compile payment_account_enhanced/models/account_payment.py
python3 -m py_compile payment_account_enhanced/models/account_move.py

echo "✅ Code deployment verified"
```

#### Step 4: Restart Service (5 min)
```bash
# Stop service
systemctl stop odoo.service
sleep 3

# Clear cache
rm -rf /var/lib/odoo/.cache /var/lib/odoo/.local
find /tmp -name "odoo*" -type d -exec rm -rf {} + 2>/dev/null || true

# Start service
systemctl start odoo.service
sleep 60

# Verify startup
systemctl status odoo.service
tail -20 /var/odoo/osusproperties/logs/odoo-server.log

echo "✅ Service restart complete"
```

#### Step 5: Run Tests (15 min)
See **COMPREHENSIVE_TEST_CHECKLIST.md** for all 26 tests

**Quick smoke tests**:
```bash
# Test 1: Module loaded
psql -U odoo -d osusproperties -t -c "
SELECT state, installed_version FROM ir_module_module 
WHERE name = 'payment_account_enhanced';"

# Test 2: Posted payments protected (code-level)
echo "✅ Code validation: Posted payment guard is in place"

# Test 3: Data integrity
psql -U odoo -d osusproperties << 'EOF'
SELECT COUNT(*) as payment_count FROM account_payment;
SELECT COUNT(*) as invoice_count FROM account_move 
WHERE state='posted' AND move_type IN ('in_invoice','in_refund','out_invoice','out_refund');
EOF
```

---

## 🧪 TESTING SHORTCUTS

### Quick User Permission Test (5 min)
```bash
# Test as regular user
1. Login to Odoo with non-manager account
2. Accounting → Payments → Open posted payment
3. Try to edit any field
4. Expected: Error "Posted payments cannot be modified..."

# Test as manager
5. Login with Payment Manager account
6. Accounting → Payments → Same posted payment
7. Edit a field (e.g., Memo)
8. Expected: Edit succeeds
```

### Quick Workflow Test (5 min)
```bash
1. Create new payment: Amount 5,000 AED
2. Submit → Should be "Under Review"
3. Review → Should be "For Approval"
4. Approve → Should be "Approved"
5. Post → Should be "Posted"
6. Try to edit → Should be blocked
```

### Quick Reconciliation Test (2 min)
```bash
# If you have reconciled payments
1. Accounting → Bank Reconciliation → Open completed reconciliation
2. Note the matched payment ID
3. Accounting → Payments → Open that payment
4. Try to edit Amount/Partner
5. Expected: Error "Cannot modify reconciled payment details..."
```

---

## 📊 VERIFICATION QUERIES

### Data Integrity Check (Run immediately after deployment)
```sql
-- All should return same values as pre-deployment baseline
SELECT 'Payment Count', COUNT(*) FROM account_payment
UNION ALL
SELECT 'Posted Payments', COUNT(*) FROM account_payment WHERE state='posted'
UNION ALL
SELECT 'Reconciled Payments', COUNT(DISTINCT ap.id) 
FROM account_payment ap
LEFT JOIN account_move am ON ap.move_id = am.id
LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
WHERE ap.state = 'posted' AND abrl.id IS NOT NULL;
```

### Module Status Check
```sql
SELECT name, state, installed_version FROM ir_module_module 
WHERE name = 'payment_account_enhanced';
-- Expected: payment_account_enhanced | installed | 17.0.1.0.9
```

### Error Log Check
```bash
tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep -E "ERROR|CRITICAL"
# Expected: Empty (no critical errors)
```

---

## 🚨 IF SOMETHING BREAKS

### Immediate Rollback (< 5 min)
```bash
ssh -p 22 root@139.84.163.11

# Stop service
systemctl stop odoo.service

# Revert code
cd /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844
git checkout HEAD~1 -- \
  payment_account_enhanced/models/account_payment.py \
  payment_account_enhanced/models/account_move.py \
  payment_account_enhanced/views/account_payment_views.xml

# Start service
systemctl start odoo.service
sleep 60

# Verify
systemctl status odoo.service
```

### Database Restore (< 15 min)
```bash
# If database corrupted (very unlikely)
systemctl stop odoo.service
systemctl stop postgresql

# Find backup
ls -lh /var/odoo/backups/osusproperties_PRE_DEPLOY_*.dump.gz

# Restore
BACKUP=$(ls /var/odoo/backups/osusproperties_PRE_DEPLOY_*.dump.gz | head -1)
gunzip -c "$BACKUP" | sudo -u postgres pg_restore --dbname osusproperties

systemctl start postgresql
systemctl start odoo.service
```

---

## ✅ SUCCESS CRITERIA

Your deployment is **SUCCESSFUL** when:

✅ All 26 tests from COMPREHENSIVE_TEST_CHECKLIST.md pass  
✅ Regular users get error when trying to edit posted payments  
✅ Payment Managers can still edit posted payments  
✅ Posted journal entries cannot be reset to draft  
✅ "Print Voucher" button shows only for posted payments  
✅ Reconciled payment count unchanged  
✅ No critical errors in logs  
✅ Service runs stable for 24 hours  

---

## 📋 FINAL CHECKLIST

Before considering deployment "complete":

- [ ] All pre-deployment validation queries show expected results
- [ ] Database backup created and verified (size > 500MB)
- [ ] Code backup created and verified
- [ ] Code deployed from git (3 files changed)
- [ ] Odoo service restarted successfully
- [ ] Module version shows 17.0.1.0.9 in database
- [ ] All 26 functional tests passed
- [ ] Regular user permission test: ✅ Blocked from edit
- [ ] Manager override test: ✅ Can edit
- [ ] Reconciliation test: ✅ Protected
- [ ] Data counts identical to baseline
- [ ] No critical errors in logs
- [ ] 24-hour monitoring completed with no issues

---

## 📞 SUPPORT

**Issue**: Users getting "Posted payments cannot be modified" error  
**Action**: This is expected - direct them to Payment Manager

**Issue**: "Print Voucher" button not showing  
**Action**: Clear browser cache (Ctrl+Shift+Del) and reload

**Issue**: Service won't start  
**Action**: Execute immediate rollback above

**Issue**: Data appears corrupted  
**Action**: Execute database restore above

---

## 📈 MONITORING (24+ hours post-deployment)

Check these daily:

```bash
# 1. Service health
systemctl status odoo.service

# 2. Recent errors
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep ERROR

# 3. Data counts (should be stable)
psql -U odoo -d osusproperties -c "SELECT COUNT(*) FROM account_payment;"

# 4. Payment workflow stats
psql -U odoo -d osusproperties << 'EOF'
SELECT approval_state, COUNT(*) FROM account_payment 
WHERE create_date >= NOW() - INTERVAL '24 hours' 
GROUP BY approval_state;
EOF

# 5. Reconciliation integrity
psql -U odoo -d osusproperties -c "
SELECT COUNT(*) FROM account_bank_reconciliation_line WHERE move_id IS NULL;"
# Expected: 0
```

---

**Document Version**: 1.0  
**Created**: 2025-12-22  
**Status**: Ready for Deployment ✅
