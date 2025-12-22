# 🔬 PRE-DEPLOYMENT DATA VALIDATION SCRIPT
**Purpose**: Verify database integrity before payment hardening deployment  
**Run Time**: 30-60 seconds  
**Output**: HTML report or console log  

---

## SQL VALIDATION QUERIES

### 1. Payment & Invoice Status Distribution
```sql
-- Check for orphaned or inconsistent records
SELECT 
  'PAYMENTS' as record_type,
  COUNT(*) as total_count,
  COUNT(CASE WHEN state = 'posted' THEN 1 END) as posted_count,
  COUNT(CASE WHEN state = 'draft' THEN 1 END) as draft_count,
  COUNT(CASE WHEN state = 'cancelled' THEN 1 END) as cancelled_count,
  COUNT(CASE WHEN approval_state IS NULL THEN 1 END) as missing_approval_state
FROM account_payment
WHERE create_date >= NOW() - INTERVAL '90 days'

UNION ALL

SELECT 
  'INVOICES' as record_type,
  COUNT(*) as total_count,
  COUNT(CASE WHEN state = 'posted' THEN 1 END) as posted_count,
  COUNT(CASE WHEN state = 'draft' THEN 1 END) as draft_count,
  COUNT(CASE WHEN state = 'cancel' THEN 1 END) as cancelled_count,
  COUNT(CASE WHEN approval_state IS NULL THEN 1 END) as missing_approval_state
FROM account_move
WHERE move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')
  AND create_date >= NOW() - INTERVAL '90 days';

-- Expected: All counts > 0, missing_approval_state = 0
```

### 2. Reconciliation Integrity Check
```sql
-- Verify no orphaned reconciliation links
SELECT 
  COUNT(*) as reconciliation_lines,
  COUNT(CASE WHEN move_id IS NOT NULL THEN 1 END) as lines_with_moves,
  COUNT(CASE WHEN reconciliation_id IS NOT NULL THEN 1 END) as lines_with_reconciliation
FROM account_bank_reconciliation_line
WHERE reconciliation_id IN (
  SELECT id FROM account_bank_reconciliation 
  WHERE create_date >= NOW() - INTERVAL '90 days'
);

-- Expected: reconciliation_lines = lines_with_moves = lines_with_reconciliation
```

### 3. Payment-Move Link Validation
```sql
-- Check all payments have valid move references
SELECT 
  COUNT(*) as total_payments,
  COUNT(CASE WHEN move_id IS NOT NULL THEN 1 END) as with_move,
  COUNT(CASE WHEN move_id IS NULL THEN 1 END) as orphaned_payments,
  COUNT(CASE WHEN am.id IS NULL THEN 1 END) as move_not_found
FROM account_payment ap
LEFT JOIN account_move am ON ap.move_id = am.id
WHERE ap.create_date >= NOW() - INTERVAL '90 days';

-- Expected: orphaned_payments = 0, move_not_found = 0
```

### 4. Posted Payments with Matched Reconciliations
```sql
-- Identify high-value reconciled payments
SELECT 
  ap.id,
  ap.name,
  ap.voucher_number,
  ap.amount,
  ap.currency_id,
  ap.state,
  ap.approval_state,
  COUNT(abrl.id) as reconciliation_match_count,
  br.name as reconciliation_ref
FROM account_payment ap
LEFT JOIN account_move am ON ap.move_id = am.id
LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
LEFT JOIN account_bank_reconciliation br ON abrl.reconciliation_id = br.id
WHERE ap.state = 'posted'
  AND abrl.id IS NOT NULL
  AND ap.create_date >= NOW() - INTERVAL '30 days'
GROUP BY ap.id, ap.name, ap.voucher_number, ap.amount, ap.currency_id, ap.state, ap.approval_state, br.name
ORDER BY ap.amount DESC
LIMIT 20;

-- Expected: All records match to single reconciliation, no duplicates
```

### 5. Approval Workflow Completeness
```sql
-- Verify all posted payments went through workflow
SELECT 
  ap.id,
  ap.name,
  ap.state,
  ap.approval_state,
  ap.reviewer_id,
  ap.approver_id,
  ap.authorizer_id,
  CASE 
    WHEN ap.approval_state = 'posted' AND ap.reviewer_id IS NULL THEN 'MISSING_REVIEWER'
    WHEN ap.approval_state = 'posted' AND ap.approver_id IS NULL THEN 'MISSING_APPROVER'
    WHEN ap.approval_state = 'posted' AND ap.requires_authorization AND ap.authorizer_id IS NULL THEN 'MISSING_AUTHORIZER'
    ELSE 'OK'
  END as status
FROM account_payment ap
WHERE ap.state = 'posted'
  AND ap.create_date >= NOW() - INTERVAL '30 days'
HAVING status != 'OK'
LIMIT 20;

-- Expected: No records found (all posted payments have complete workflow)
```

### 6. Journal Entry Consistency
```sql
-- Check for unmatched invoice/bill states
SELECT 
  am.id,
  am.name,
  am.move_type,
  am.state,
  am.approval_state,
  COUNT(aml.id) as line_count,
  SUM(CASE WHEN aml.account_id IN (SELECT id FROM account_account WHERE deprecated = true) THEN 1 ELSE 0 END) as deprecated_accounts
FROM account_move am
LEFT JOIN account_move_line aml ON am.id = aml.move_id
WHERE am.move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')
  AND am.state = 'posted'
  AND am.create_date >= NOW() - INTERVAL '30 days'
GROUP BY am.id, am.name, am.move_type, am.state, am.approval_state
HAVING deprecated_accounts > 0 OR line_count = 0
LIMIT 20;

-- Expected: No records found (all moves have valid lines and accounts)
```

### 7. User Permissions Check
```sql
-- Verify Payment Manager group exists and has members
SELECT 
  rg.id,
  rg.name,
  COUNT(gru.id) as user_count
FROM res_groups rg
LEFT JOIN res_groups_users_rel gru ON rg.id = gru.gid
WHERE rg.name IN ('Payment Manager', 'Payment Reviewer', 'Payment Approver', 
                  'Payment Authorizer', 'Payment Poster', 'Payment User')
GROUP BY rg.id, rg.name
ORDER BY rg.name;

-- Expected: All groups exist, at least 1 Payment Manager user
```

### 8. Data Integrity Summary
```sql
-- Complete data health check
SELECT 
  (SELECT COUNT(*) FROM account_payment WHERE state = 'posted') as posted_payments,
  (SELECT COUNT(*) FROM account_move WHERE state = 'posted' 
   AND move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')) as posted_invoices,
  (SELECT COUNT(*) FROM account_bank_reconciliation WHERE state = 'posted') as completed_reconciliations,
  (SELECT COUNT(*) FROM account_payment WHERE state = 'posted' 
   AND id IN (SELECT DISTINCT ap_id FROM account_bank_reconciliation_line 
              WHERE move_id IS NOT NULL)) as reconciled_payments,
  (SELECT COUNT(DISTINCT movement_date) FROM account_move_line WHERE move_id 
   IN (SELECT id FROM account_move WHERE state = 'posted')) as posting_dates
UNION ALL
SELECT 
  (SELECT COUNT(*) FROM account_payment WHERE approval_state IS NULL) as null_approval_states,
  (SELECT COUNT(*) FROM account_payment ap WHERE state = 'draft' AND approval_state = 'posted') as inconsistent_states,
  (SELECT COUNT(*) FROM account_bank_reconciliation_line WHERE move_id IS NULL) as orphaned_reconciliation_lines,
  0, 0;

-- Expected: First row shows all positive counts, second row all zeros
```

---

## PYTHON VALIDATION SCRIPT

```python
#!/usr/bin/env python3
# Run directly: python3 validate_deployment.py

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from tabulate import tabulate

# Configuration
DB_NAME = os.getenv('ODOO_DB_NAME', 'osusproperties')
DB_USER = os.getenv('ODOO_DB_USER', 'odoo')
DB_HOST = os.getenv('ODOO_DB_HOST', 'localhost')
DB_PORT = os.getenv('ODOO_DB_PORT', '5432')
REPORT_FILE = f'/var/odoo/backups/validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(msg, level='INFO'):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    color = {
        'INFO': Colors.BLUE,
        'SUCCESS': Colors.GREEN,
        'ERROR': Colors.RED,
        'WARNING': Colors.YELLOW
    }.get(level, '')
    reset = Colors.END if color else ''
    print(f"[{timestamp}] {color}[{level}]{reset} {msg}")

def validate_payment_states(cursor):
    """Check payment and invoice state distribution"""
    log("Checking payment/invoice state distribution...", 'INFO')
    
    cursor.execute("""
    SELECT 
      'PAYMENTS' as type,
      COUNT(*) as total,
      COUNT(CASE WHEN state = 'posted' THEN 1 END) as posted,
      COUNT(CASE WHEN state = 'draft' THEN 1 END) as draft,
      COUNT(CASE WHEN approval_state IS NULL THEN 1 END) as null_approval
    FROM account_payment
    WHERE create_date >= NOW() - INTERVAL '90 days'
    
    UNION ALL
    
    SELECT 
      'INVOICES',
      COUNT(*),
      COUNT(CASE WHEN state = 'posted' THEN 1 END),
      COUNT(CASE WHEN state = 'draft' THEN 1 END),
      COUNT(CASE WHEN approval_state IS NULL THEN 1 END)
    FROM account_move
    WHERE move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')
      AND create_date >= NOW() - INTERVAL '90 days'
    """)
    
    results = cursor.fetchall()
    headers = ['Type', 'Total', 'Posted', 'Draft', 'Null Approval']
    
    print("\n" + tabulate(results, headers=headers, tablefmt='grid'))
    
    # Check for issues
    issues = []
    for row in results:
        if row[4] > 0:  # null_approval_state
            issues.append(f"⚠️  {row[0]} has {row[4]} records with NULL approval_state")
    
    if issues:
        log(f"Found issues: {'; '.join(issues)}", 'WARNING')
        return False
    
    log("✅ Payment/invoice states OK", 'SUCCESS')
    return True

def validate_reconciliation_integrity(cursor):
    """Check reconciliation links are valid"""
    log("Checking reconciliation integrity...", 'INFO')
    
    cursor.execute("""
    SELECT 
      COUNT(*) as total_lines,
      COUNT(CASE WHEN move_id IS NOT NULL THEN 1 END) as with_move,
      COUNT(CASE WHEN reconciliation_id IS NOT NULL THEN 1 END) as with_reconciliation,
      COUNT(CASE WHEN move_id IS NULL THEN 1 END) as orphaned
    FROM account_bank_reconciliation_line
    WHERE reconciliation_id IN (
      SELECT id FROM account_bank_reconciliation 
      WHERE create_date >= NOW() - INTERVAL '90 days'
    )
    """)
    
    result = cursor.fetchone()
    
    print(f"\nReconciliation Lines: {result[0]}")
    print(f"  ├─ With move: {result[1]}")
    print(f"  ├─ With reconciliation: {result[2]}")
    print(f"  └─ Orphaned: {result[3]}")
    
    if result[3] > 0:
        log(f"❌ Found {result[3]} orphaned reconciliation lines", 'ERROR')
        return False
    
    if result[0] != result[1] or result[0] != result[2]:
        log("❌ Reconciliation line inconsistency detected", 'ERROR')
        return False
    
    log("✅ Reconciliation integrity OK", 'SUCCESS')
    return True

def validate_reconciled_payments(cursor):
    """Check reconciled payments are consistent"""
    log("Checking reconciled payments...", 'INFO')
    
    cursor.execute("""
    SELECT COUNT(*) as reconciled_payments
    FROM account_payment ap
    LEFT JOIN account_move am ON ap.move_id = am.id
    LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
    WHERE ap.state = 'posted'
      AND abrl.id IS NOT NULL
      AND ap.create_date >= NOW() - INTERVAL '30 days'
    """)
    
    count = cursor.fetchone()[0]
    print(f"\nReconciled Posted Payments: {count}")
    
    log(f"✅ Found {count} reconciled posted payments (will be protected)", 'SUCCESS')
    return True

def validate_workflow_completeness(cursor):
    """Check all posted payments have complete workflow"""
    log("Checking workflow completeness...", 'INFO')
    
    cursor.execute("""
    SELECT 
      COUNT(*) as incomplete_workflows,
      COUNT(CASE WHEN reviewer_id IS NULL THEN 1 END) as missing_reviewer,
      COUNT(CASE WHEN approver_id IS NULL THEN 1 END) as missing_approver,
      COUNT(CASE WHEN requires_authorization AND authorizer_id IS NULL THEN 1 END) as missing_authorizer
    FROM account_payment
    WHERE state = 'posted'
      AND approval_state = 'posted'
      AND create_date >= NOW() - INTERVAL '30 days'
    """)
    
    result = cursor.fetchone()
    
    print(f"\nWorkflow Issues Found:")
    print(f"  ├─ Total Incomplete: {result[0]}")
    print(f"  ├─ Missing Reviewer: {result[1]}")
    print(f"  ├─ Missing Approver: {result[2]}")
    print(f"  └─ Missing Authorizer: {result[3]}")
    
    if result[0] > 0:
        log(f"⚠️  Found {result[0]} payments with incomplete workflow", 'WARNING')
    else:
        log("✅ All posted payments have complete workflow", 'SUCCESS')
    
    return result[0] == 0

def validate_user_permissions(cursor):
    """Check required groups and users exist"""
    log("Checking user permissions setup...", 'INFO')
    
    cursor.execute("""
    SELECT 
      rg.name,
      COUNT(gru.id) as user_count
    FROM res_groups rg
    LEFT JOIN res_groups_users_rel gru ON rg.id = gru.gid
    WHERE rg.name IN ('Payment Manager', 'Payment Reviewer', 'Payment Approver', 
                      'Payment Authorizer', 'Payment Poster')
    GROUP BY rg.id, rg.name
    ORDER BY rg.name
    """)
    
    results = cursor.fetchall()
    headers = ['Group', 'User Count']
    print("\n" + tabulate(results, headers=headers, tablefmt='grid'))
    
    # Check manager group has at least 1 user
    manager_found = any(row[0] == 'Payment Manager' and row[1] > 0 for row in results)
    
    if not manager_found:
        log("❌ No Payment Manager users found", 'ERROR')
        return False
    
    log("✅ Permission setup OK (Payment Manager exists with users)", 'SUCCESS')
    return True

def run_validation():
    """Run all validation checks"""
    log("Starting pre-deployment validation...", 'INFO')
    log(f"Database: {DB_NAME} | Host: {DB_HOST} | Port: {DB_PORT}", 'INFO')
    
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        log("✅ Database connection established", 'SUCCESS')
        
    except Exception as e:
        log(f"❌ Database connection failed: {str(e)}", 'ERROR')
        return False
    
    # Run all checks
    checks = [
        ('Payment/Invoice States', validate_payment_states),
        ('Reconciliation Integrity', validate_reconciliation_integrity),
        ('Reconciled Payments', validate_reconciled_payments),
        ('Workflow Completeness', validate_workflow_completeness),
        ('User Permissions', validate_user_permissions),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            result = check_func(cursor)
            results[check_name] = '✅ PASS' if result else '⚠️  WARN'
        except Exception as e:
            log(f"❌ Check '{check_name}' failed: {str(e)}", 'ERROR')
            results[check_name] = '❌ FAIL'
    
    cursor.close()
    conn.close()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    for check, status in results.items():
        print(f"{check:<30} {status}")
    
    passed = sum(1 for v in results.values() if '✅' in v)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        log("✅✅✅ All validation checks passed - Safe to deploy! ✅✅✅", 'SUCCESS')
        return True
    else:
        log(f"⚠️  Some checks failed/warned - Review before deploying", 'WARNING')
        return False

if __name__ == '__main__':
    success = run_validation()
    sys.exit(0 if success else 1)
```

---

## HOW TO RUN VALIDATION

### Option 1: SQL Queries Only (Quick)
```bash
# SSH to production
ssh -p 22 root@139.84.163.11

# Connect to database
psql -U odoo -d osusproperties

# Copy-paste queries from "SQL VALIDATION QUERIES" section above
# Review output for any red flags
```

### Option 2: Python Script (Recommended)
```bash
# SSH to production
ssh -p 22 root@139.84.163.11

# Run validation script
cd /var/odoo/osusproperties
python3 validate_deployment.py

# Check output for ✅ or ❌ marks
# Report saved to: /var/odoo/backups/validation_report_*.txt
```

### Option 3: Odoo CLI Check
```bash
# Via Docker if development environment exists
docker exec odoo17_local_testing odoo --db osusproperties -c /etc/odoo/odoo.conf \
  -m payment_account_enhanced --test-only

# Should complete without errors
```

---

## EXPECTED RESULTS

### ✅ All Checks Pass When:
- Posted payments count matches workflow completion (reviewer + approver + authorizer)
- Reconciled payments are protected (no orphaned links)
- All payment moves reference valid move_id records
- Payment Manager group has at least 1 active user
- No NULL approval_state values in production data
- Reconciliation line count = move count (no orphans)

### ⚠️ Warnings That Are Safe:
- Some payments missing approver (expected for low-value, only reviewer needed)
- Some invoices without approval_state (legacy data, will be grandfathered in)
- Payment Manager group with > 1 user (good for redundancy)

### ❌ Critical Issues (Do NOT Deploy):
- > 5 orphaned reconciliation lines
- Reconciliation count != move count (data corruption)
- Posted payments with NULL reviewer_id
- No Payment Manager users (cannot escalate locked payments)
- Database connection fails (infrastructure issue)

---

## VALIDATION CHECKLIST

Before running deployment:
- [ ] Created database backup
- [ ] Created code backup (addon directory)
- [ ] Ran pre-deployment validation
- [ ] All critical checks passed (0 ❌ marks)
- [ ] Documented any ⚠️ warnings for post-deployment review
- [ ] Got approval from Finance Manager
- [ ] Scheduled maintenance window
- [ ] Notified users of brief downtime

---

**Generated**: 2025-12-22  
**Module Version**: 17.0.1.0.9  
**Estimated Runtime**: 30-60 seconds  
