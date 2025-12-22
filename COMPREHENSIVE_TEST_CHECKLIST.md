# 🧪 COMPREHENSIVE POST-DEPLOYMENT TESTING CHECKLIST
**Module Version**: 17.0.1.0.9  
**Deployment Date**: December 22, 2025  
**Testing Window**: 24-48 hours post-deployment  

---

## 📋 TEST EXECUTION CHECKLIST

### CATEGORY 1: REGULAR USER RESTRICTIONS (Non-Manager)

#### Test 1.1: Edit Posted Payment Fields
**Objective**: Verify regular users cannot edit posted payment details  
**User Role**: Payment User (not Payment Manager)  
**Steps**:
```
1. Login to Odoo as regular user
2. Navigate to: Accounting → Payments
3. Filter by: state = 'posted'
4. Open any posted payment
5. Try to edit a field (e.g., Memo/Remarks)
6. Click Save
```
**Expected Result**: 
```
❌ Error popup appears:
"Posted payments cannot be modified. Please create a 
reversal or contact a Payment Manager."
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 1.2: Reset Posted Payment to Draft
**Objective**: Verify regular users cannot reset posted payments to draft  
**User Role**: Payment User  
**Steps**:
```
1. From same posted payment (Test 1.1)
2. Look for button "Reset to Draft" or similar
3. Try clicking it
```
**Expected Result**:
```
❌ Error appears:
"Posted payments cannot be reset to Draft. Please use 
reversals or contact a Payment Manager."
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 1.3: Create Reversal Instead (Alternative Flow)
**Objective**: Verify users know to use reversal for posted payments  
**User Role**: Payment User  
**Steps**:
```
1. From posted payment
2. Look for "Create Reversal" or "Create Reverse Entry" button
3. Should be visible even if edit is blocked
```
**Expected Result**:
```
✅ Reversal button is visible and clickable
✅ Reversal workflow starts normally
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 2: PAYMENT MANAGER OVERRIDE

#### Test 2.1: Edit Posted Payment as Manager
**Objective**: Verify Payment Managers CAN edit posted payments  
**User Role**: Payment Manager (or System Admin)  
**Steps**:
```
1. Login as: Payment Manager user
2. Navigate to: Accounting → Payments
3. Open the SAME posted payment from Test 1.1
4. Try to edit a field (e.g., Memo)
5. Click Save
```
**Expected Result**:
```
✅ Edit succeeds without error
✅ Save button works
✅ Record updates successfully
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 2.2: Reset Posted Payment to Draft as Manager
**Objective**: Verify Payment Managers can reset posted to draft  
**User Role**: Payment Manager  
**Steps**:
```
1. From same posted payment
2. Look for "Reset to Draft" button
3. Click it (don't save - just verify click works)
4. Check button is accessible
```
**Expected Result**:
```
✅ Button is clickable and accessible
✅ No error message appears
✅ Manager has full override capability
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 3: JOURNAL ENTRY PROTECTION

#### Test 3.1: Reset Posted Invoice to Draft (Regular User)
**Objective**: Verify posted invoices cannot be reset to draft  
**User Role**: Payment User  
**Steps**:
```
1. Navigate to: Accounting → Invoices
2. Open any POSTED customer or vendor invoice
3. Look for "Reset to Draft" or "Action" menu
4. Try to access draft button
```
**Expected Result**:
```
❌ If button shows: Error when clicked:
"Posted journal entries cannot be reset to Draft. 
Create a reversal instead or contact a Payment Manager."
✅ If button hidden: "Reset to Draft" not visible for posted
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 3.2: Reset Posted Invoice to Draft (Manager)
**Objective**: Verify managers can reset posted invoices if needed  
**User Role**: Payment Manager  
**Steps**:
```
1. Login as Payment Manager
2. Open same posted invoice
3. Check "Reset to Draft" button accessibility
```
**Expected Result**:
```
✅ Button is visible and clickable for manager
✅ Manager can perform override if necessary
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 4: RECONCILED PAYMENT PROTECTION

#### Test 4.1: Edit Reconciled Payment (Should Block)
**Objective**: Verify reconciled payments are protected from edits  
**User Role**: Payment Manager (even manager should not break reconciled)  
**Steps**:
```
1. Go to: Accounting → Bank Reconciliation
2. Find a completed reconciliation with matched payments
3. Go to: Accounting → Payments
4. Open a payment that's matched in bank reconciliation
5. Try to edit critical fields (Amount, Partner, Account)
6. Click Save
```
**Expected Result**:
```
❌ Error appears:
"Cannot modify reconciled payment details. 
Payment is matched in bank reconciliation.

Restricted fields: [list of fields attempted]

To modify, please:
1. Unreconcile in bank reconciliation
2. Then modify this payment
3. Reconcile again"
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 4.2: Edit Non-Critical Fields of Reconciled Payment
**Objective**: Verify workflow fields (memo, approvers) can still update  
**User Role**: Payment Manager  
**Steps**:
```
1. Same reconciled payment from Test 4.1
2. Try to edit ALLOWED fields:
   - Remarks/Memo
   - Approval state (via workflow buttons)
3. Click Save
```
**Expected Result**:
```
✅ Memo/remarks update succeeds
✅ Workflow fields update succeeds
✅ Only protected fields block edits
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 4.3: View Bank Reconciliation (No Changes)
**Objective**: Verify reconciliation data is intact  
**User Role**: Any user  
**Steps**:
```
1. Go to: Accounting → Bank Reconciliation
2. Open a completed reconciliation
3. View matched payments/invoices list
4. Verify all expected items appear
5. Check counts match pre-deployment baseline
```
**Expected Result**:
```
✅ All reconciled items visible
✅ No orphaned records
✅ Counts unchanged from baseline
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 5: WORKFLOW FUNCTIONALITY

#### Test 5.1: Create New Payment (Draft → Posted)
**Objective**: Verify new payments can go through full workflow  
**User Role**: Payment Reviewer  
**Steps**:
```
1. Go to: Accounting → Payments → Create
2. Fill fields:
   - Partner: [Select vendor]
   - Payment Type: Vendor Payment (Outbound)
   - Amount: 5,000 AED
   - Account: [Select payment account]
3. Click "Submit for Review"
```
**Expected Result**:
```
✅ Payment created successfully
✅ Status changes to "Under Review"
✅ reviewer_date is populated
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 5.2: Approve and Post Payment
**Objective**: Verify workflow progression works  
**User Role**: Payment Approver  
**Steps**:
```
1. Open the payment created in Test 5.1
2. Click "Review" button
3. Verify status → "For Approval"
4. Click "Approve" button
5. Verify status → "Approved"
6. As Payment Poster, click "Post Payment"
7. Verify status → "Posted"
```
**Expected Result**:
```
✅ Each workflow step succeeds
✅ Correct users assigned (reviewer, approver, poster)
✅ Dates populated correctly
✅ Final status is "Posted"
✅ Journal entry created
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 5.3: High-Value Payment Authorization
**Objective**: Verify payments ≥ 10,000 AED require authorization  
**User Role**: Payment Approver → Payment Authorizer  
**Steps**:
```
1. Create new payment with Amount: 15,000 AED
2. Submit for review
3. Review → Approve
4. Check if status goes to "For Authorization"
5. As Payment Authorizer, click "Authorize"
6. Status should → "Approved" (ready to post)
```
**Expected Result**:
```
✅ High-value payments show "For Authorization" state
✅ Authorizer role required for amounts ≥ 10,000 AED
✅ Cannot skip authorization stage
✅ Proper sequencing maintained
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 5.4: Low-Value Payment Simplified Workflow
**Objective**: Verify low-value payments skip authorization  
**User Role**: Payment Reviewer  
**Steps**:
```
1. Create new payment with Amount: 2,000 AED
2. Submit for review
3. Review → should go directly to "Approved"
4. Post the payment
```
**Expected Result**:
```
✅ Low-value payments skip "For Authorization" stage
✅ Reviewer can post directly
✅ Faster workflow for small amounts
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 6: UI CHANGES

#### Test 6.1: Button Label Changed to "Print Voucher"
**Objective**: Verify "View Payment" button renamed  
**User Role**: Any user  
**Steps**:
```
1. Open any POSTED payment
2. Look for payment display button in header
3. Check button label
```
**Expected Result**:
```
✅ Button shows "Print Voucher" (not "View Payment")
✅ Button is visible only when approval_state = 'posted'
✅ Button is visible for all accounting users
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 6.2: Print Voucher Button Not Visible for Draft
**Objective**: Verify button hidden for non-posted payments  
**User Role**: Any user  
**Steps**:
```
1. Open a DRAFT payment
2. Look for "Print Voucher" button
```
**Expected Result**:
```
✅ Button is NOT visible for draft payments
✅ Button only shows for posted payments
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 7: DATA INTEGRITY

#### Test 7.1: Payment Counts Unchanged
**Objective**: Verify no data loss  
**Steps**:
```
SQL Query:
SELECT COUNT(*) FROM account_payment;
(Compare with pre-deployment baseline)
```
**Expected Result**:
```
✅ Count is identical to baseline
✅ No payments deleted or lost
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 7.2: Invoice/Bill Counts Unchanged
**Objective**: Verify no journal entry loss  
**Steps**:
```
SQL Query:
SELECT COUNT(*) FROM account_move 
WHERE move_type IN ('in_invoice', 'in_refund', 'out_invoice', 'out_refund')
  AND state = 'posted';
(Compare with pre-deployment baseline)
```
**Expected Result**:
```
✅ Count matches baseline
✅ No invoices lost or corrupted
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 7.3: Reconciliation Counts Stable
**Objective**: Verify no reconciliation orphans created  
**Steps**:
```
SQL Query:
SELECT COUNT(*) FROM account_bank_reconciliation 
WHERE state = 'posted';
(Compare with pre-deployment baseline)
```
**Expected Result**:
```
✅ Count identical to baseline
✅ No orphaned reconciliation records
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 7.4: Reconciled Payments Still Matched
**Objective**: Verify matched payments remain intact  
**Steps**:
```
SQL Query:
SELECT COUNT(DISTINCT ap.id) FROM account_payment ap
LEFT JOIN account_move am ON ap.move_id = am.id
LEFT JOIN account_bank_reconciliation_line abrl ON am.id = abrl.move_id
WHERE ap.state = 'posted' AND abrl.id IS NOT NULL;
(Compare with pre-deployment baseline)
```
**Expected Result**:
```
✅ Count matches pre-deployment baseline
✅ All reconciled payments still matched
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 8: ERROR HANDLING & LOGS

#### Test 8.1: Check Logs for Critical Errors
**Objective**: Verify no system errors introduced  
**Steps**:
```
SSH to server and run:
tail -200 /var/odoo/osusproperties/logs/odoo-server.log | grep -E "ERROR|CRITICAL|payment_account_enhanced"
```
**Expected Result**:
```
✅ No CRITICAL errors
✅ No SyntaxError or ImportError from payment_account_enhanced
✅ Informational messages only (workflow validations are OK)
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 8.2: User Error Messages Are Clear
**Objective**: Verify error messages guide users properly  
**Steps**:
```
1. Trigger each permission error from Tests 1.1-1.2
2. Read the error message carefully
3. Verify it tells user what to do (contact manager, create reversal)
```
**Expected Result**:
```
✅ Error messages are clear and actionable
✅ Users understand the restriction
✅ Messages suggest alternatives (reversal, manager contact)
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 9: PERFORMANCE

#### Test 9.1: Page Load Time (Payments List)
**Objective**: Verify no performance degradation  
**Steps**:
```
1. Go to: Accounting → Payments
2. Open browser DevTools → Network tab
3. Reload page
4. Check page load time
```
**Expected Result**:
```
✅ Page loads in < 3 seconds
✅ No timeouts
✅ Reconciliation check doesn't slow page
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 9.2: Open Posted Payment (Detail View)
**Objective**: Verify form load performance  
**Steps**:
```
1. Open any posted payment detail
2. Check load time in DevTools
```
**Expected Result**:
```
✅ Form loads in < 2 seconds
✅ All fields visible and responsive
✅ No lag or delays
```
**Status**: ☐ PASS ☐ FAIL

---

### CATEGORY 10: SYSTEM HEALTH

#### Test 10.1: Service Status
**Objective**: Verify Odoo service is stable  
**Steps**:
```
SSH and run:
systemctl status odoo.service
```
**Expected Result**:
```
✅ Status: active (running)
✅ No service crashes
✅ Process memory stable
```
**Status**: ☐ PASS ☐ FAIL

---

#### Test 10.2: Database Connections
**Objective**: Verify database is healthy  
**Steps**:
```
SSH and run:
psql -U odoo -d osusproperties -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname='osusproperties';"
```
**Expected Result**:
```
✅ Connection count normal (10-20 concurrent)
✅ No long-running locks
✅ Database responsive
```
**Status**: ☐ PASS ☐ FAIL

---

## 📊 SUMMARY SCORECARD

| Category | Tests | Passed | Failed | Status |
|----------|-------|--------|--------|--------|
| Regular User Restrictions | 3 | ☐ | ☐ | ☐ |
| Payment Manager Override | 2 | ☐ | ☐ | ☐ |
| Journal Entry Protection | 2 | ☐ | ☐ | ☐ |
| Reconciled Payments | 3 | ☐ | ☐ | ☐ |
| Workflow Functionality | 4 | ☐ | ☐ | ☐ |
| UI Changes | 2 | ☐ | ☐ | ☐ |
| Data Integrity | 4 | ☐ | ☐ | ☐ |
| Error Handling & Logs | 2 | ☐ | ☐ | ☐ |
| Performance | 2 | ☐ | ☐ | ☐ |
| System Health | 2 | ☐ | ☐ | ☐ |
| **TOTAL** | **26** | **☐** | **☐** | **☐** |

---

## ✅ DEPLOYMENT SIGN-OFF

**Tested By**: ______________________  
**Date/Time**: ______________________  
**Overall Result**: 
- ☐ ALL TESTS PASSED ✅
- ☐ MINOR ISSUES (document below)
- ☐ CRITICAL ISSUES (require rollback)

**Issues Found** (if any):
```
1. ________________________
2. ________________________
3. ________________________
```

**Tester Signature**: ______________________  
**Manager Approval**: ______________________  

---

**Document Version**: 1.0  
**Created**: 2025-12-22  
