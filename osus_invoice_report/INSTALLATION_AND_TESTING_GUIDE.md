# Smart Report System - Complete Installation & Testing Guide

## 🚀 Installation Steps

### Step 1: Verify Files Are in Place

```bash
cd /d/GitHub/osus_main/cleanup\ osus/OSUSAPPS/osus_invoice_report

# Check key files exist
ls -la models/smart_report_helper.py
ls -la report/smart_invoice_report.xml
ls -la SMART_REPORT_*.md
```

### Step 2: Update Module in Odoo

```bash
# Update the osus_invoice_report module
docker-compose exec odoo odoo --stop-after-init -d odoo -u osus_invoice_report
```

**Expected Output:**
```
INFO odoo.modules.loading: updating osus_invoice_report
INFO odoo.modules.loading: osus_invoice_report loaded in X seconds
```

### Step 3: Verify Installation in Odoo UI

1. **Login to Odoo**
   - URL: http://localhost:8069
   - Username: admin
   - Password: admin

2. **Navigate to Reports**
   - Go to **Accounting > Invoices** or **Accounting > Bills**

3. **Test Smart Report**
   - Select an invoice or bill
   - Click **Print** → **OSUS Invoice** (or **OSUS Bill**)
   - Should render with adaptive template

---

## 📋 Component Checklist

| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| Smart Helper | `models/smart_report_helper.py` | ✅ Created | Core logic |
| Smart Template | `report/smart_invoice_report.xml` | ✅ Created | QWeb template |
| Invoice Model | `models/report_custom_invoice.py` | ✅ Updated | Uses smart helper |
| Bill Model | `models/report_custom_bill.py` | ✅ Updated | Uses smart helper |
| Model Init | `models/__init__.py` | ✅ Updated | Imports smart helper |
| Manifest | `__manifest__.py` | ✅ Updated | Registers template |
| Documentation | `SMART_REPORT_*.md` | ✅ Created | User guides |

---

## 🧪 Testing Scenarios

### Test 1: Customer Invoice Report

**Preconditions:**
- Have a posted customer invoice (move_type = 'out_invoice')
- Customer has complete address

**Steps:**
1. Go to **Accounting > Invoices**
2. Open a posted invoice
3. Click **Print** → **OSUS Invoice**
4. Download PDF

**Expected Results:**
- [ ] Header says "CUSTOMER INVOICE" in blue
- [ ] "FROM (Company)" and "TO (Customer)" labels shown
- [ ] All customer details displayed
- [ ] Line items table complete
- [ ] Subtotal, Tax, Total amounts shown
- [ ] Payment terms displayed (if configured)
- [ ] No draft banner (since posted)
- [ ] Footer with generation date visible

**Verify:**
```
✅ Title: "CUSTOMER INVOICE [Reference]"
✅ Color: Blue (#1a5c96)
✅ Party Labels: FROM/TO correct
✅ Layout: Professional 2-column
✅ Content: All fields populated
```

---

### Test 2: Vendor Bill Report

**Preconditions:**
- Have a posted vendor bill (move_type = 'in_invoice')
- Vendor has complete address

**Steps:**
1. Go to **Accounting > Bills**
2. Open a posted bill
3. Click **Print** → **OSUS Bill**
4. Download PDF

**Expected Results:**
- [ ] Header says "VENDOR BILL" in red
- [ ] "FROM (Vendor)" and "TO (Company)" labels shown
- [ ] Vendor details displayed correctly
- [ ] Company bank details shown in payment section
- [ ] IBAN and account number visible
- [ ] Payment terms displayed
- [ ] Professional styling applied
- [ ] All line items visible

**Verify:**
```
✅ Title: "VENDOR BILL [Reference]"
✅ Color: Red (#800020)
✅ Party Labels: FROM/TO correct for bill
✅ Bank Details: IBAN and account shown
✅ Payment Section: Complete
```

---

### Test 3: Draft Document

**Preconditions:**
- Have a draft invoice or bill

**Steps:**
1. Create or open a draft document
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] Yellow **"DRAFT DOCUMENT - NOT YET POSTED"** banner appears at top
- [ ] Draft banner has alert styling
- [ ] All data still visible
- [ ] No "Paid" stamp overlay

**Verify:**
```
✅ Draft Banner: Yellow warning visible
✅ Message: Clear and prominent
✅ Data: Complete despite draft status
```

---

### Test 4: Paid Document

**Preconditions:**
- Have a fully reconciled/paid invoice
- Payment status should show as 'paid'

**Steps:**
1. Open a paid invoice
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] "PAID" watermark overlay appears (semi-transparent)
- [ ] Watermark rotated at 45 degrees
- [ ] Watermark doesn't obscure important data
- [ ] All content still readable
- [ ] Payment status shows as "Paid" in status section

**Verify:**
```
✅ Paid Stamp: Visible watermark
✅ Rotation: 45 degrees diagonal
✅ Opacity: Properly transparent (not blocking)
✅ Readability: Content still clear
```

---

### Test 5: Credit Note

**Preconditions:**
- Have a credit note (move_type = 'in_refund' or 'out_refund')

**Steps:**
1. Open a credit note
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] Header indicates "CREDIT NOTE"
- [ ] Appropriate styling applied
- [ ] Negative amounts displayed correctly
- [ ] Original reference shown (if linked)
- [ ] Professional layout maintained

**Verify:**
```
✅ Title: References "CREDIT NOTE"
✅ Amounts: Negative values clear
✅ References: Source document visible
✅ Layout: Professional despite credit nature
```

---

### Test 6: Multi-Line Document

**Preconditions:**
- Have an invoice with 20+ line items

**Steps:**
1. Open invoice with many lines
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] All lines displayed (no truncation)
- [ ] Proper pagination if document is multiple pages
- [ ] Footer appears on each page
- [ ] Header visible on first page
- [ ] Line items table maintains alignment across pages
- [ ] Totals on last page only

**Verify:**
```
✅ Line Count: All visible
✅ Pagination: Proper page breaks
✅ Alignment: Table consistent across pages
✅ Formatting: Maintained through pages
```

---

### Test 7: Tax Breakdown

**Preconditions:**
- Have an invoice with multiple tax rates (e.g., 5% and 20%)

**Steps:**
1. Open invoice with multiple tax rates
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] Tax breakdown section appears
- [ ] Each tax rate listed separately
- [ ] Tax amounts calculated correctly
- [ ] Detailed breakdown: "Tax (5%): X.XX AED"
- [ ] Format consistent with style

**Verify:**
```
✅ Breakdown: Shows all tax rates
✅ Calculations: Amounts correct
✅ Formatting: "Tax (X%): Amount" format
✅ Styling: Colored section with proper contrast
```

---

### Test 8: Commission Document

**Preconditions:**
- Have an invoice with "commission" in reference or notes

**Steps:**
1. Open commission-related invoice
2. Verify reference contains "commission" keyword
3. Click **Print** → Report name
4. Download PDF

**Expected Results:**
- [ ] Document recognized as commission doc
- [ ] Smart helper correctly detects
- [ ] Appropriate styling applied
- [ ] Commission-specific fields shown (if present)

**Verify:**
```
✅ Detection: Commission identified
✅ Styling: Appropriate applied
✅ Content: Commission details visible
```

---

### Test 9: Notes & Narration

**Preconditions:**
- Have an invoice with narration/notes

**Steps:**
1. Open invoice with notes in narration field
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] Notes section appears (blue background)
- [ ] Notes heading visible
- [ ] Full narration text displayed
- [ ] Line breaks preserved
- [ ] Professional styling

**Verify:**
```
✅ Section: Notes visible
✅ Styling: Blue background
✅ Content: Full text displayed
✅ Formatting: Line breaks preserved
```

---

### Test 10: Empty/Minimal Fields

**Preconditions:**
- Have an invoice with minimal information

**Steps:**
1. Open invoice with minimal data (few lines, no notes, etc.)
2. Click **Print** → Report name
3. Download PDF

**Expected Results:**
- [ ] No empty sections visible
- [ ] Notes section hidden (no content)
- [ ] Payment terms hidden (if not set)
- [ ] Layout still looks professional
- [ ] No errors in rendering

**Verify:**
```
✅ Sections: Hidden when empty
✅ Layout: Professional despite minimal data
✅ Errors: None in console
✅ Rendering: Clean output
```

---

## 🔍 Detailed Verification Checklist

### Header Section
- [ ] Document title correct for type
- [ ] Color matches document type
- [ ] Date format is DD/MM/YYYY
- [ ] State badge displays correctly
- [ ] Status color appropriate

### Party Section
- [ ] FROM label correct
- [ ] TO label correct
- [ ] Partner name displayed
- [ ] Address complete
- [ ] City/zip formatted
- [ ] Country shown
- [ ] VAT ID visible (if present)
- [ ] 2-column layout

### Line Items Table
- [ ] Header row visible
- [ ] Header colors match theme
- [ ] Column headers: Description, Qty, Unit Price, VAT, Total
- [ ] All lines displayed
- [ ] Quantities correct
- [ ] Prices formatted with 2 decimals
- [ ] Tax percentages shown
- [ ] Line totals calculated correctly
- [ ] Table borders clear

### Amounts Section
- [ ] Subtotal line
- [ ] Tax line (or tax breakdown if multi-rate)
- [ ] Total line prominent
- [ ] Currency symbol on each amount
- [ ] Amounts formatted correctly
- [ ] Colors match theme

### Payment Section (for bills)
- [ ] Section visible
- [ ] Bank name: ABU DHABI COMMERCIAL BANK
- [ ] Account name: OSUS REAL ESTATE BROKERAGE LLC
- [ ] Account number: 14041417820001 - AED
- [ ] IBAN: AE350030014041417820001
- [ ] Clear formatting

### Footer Section
- [ ] "Computer generated" notice visible
- [ ] Generation date shown
- [ ] Footer on first page
- [ ] Date format correct (DD/MM/YYYY)

### PDF Quality
- [ ] No rendering errors
- [ ] Fonts readable
- [ ] Colors print clearly
- [ ] Tables not broken across pages
- [ ] Images (if any) render correctly
- [ ] File size reasonable (<5MB)

---

## 🐛 Troubleshooting

### Issue: Report Not Appearing in Print Menu

**Check:**
1. Module is installed: `docker-compose exec odoo odoo -m osus_invoice_report`
2. Report action in manifest: Check `__manifest__.py`
3. Template XML valid: `xmllint osus_invoice_report/report/smart_invoice_report.xml`

**Fix:**
```bash
docker-compose exec odoo odoo --stop-after-init -d odoo -u osus_invoice_report
```

---

### Issue: Colors Not Showing in PDF

**Check:**
1. PDF reader supports colors
2. Browser PDF viewer rendering correctly
3. Inline styles not overridden

**Fix:**
- Try different PDF viewer
- Export to file and open in Adobe Reader
- Check browser console for CSS errors

---

### Issue: Data Missing from Report

**Debug:**
```xml
<!-- Add to template to debug -->
<div style="background-color: #fcc; padding: 10px;">
    DEBUG: Move Type = <span t-field="o.move_type"/>
    DEBUG: Partner = <span t-field="o.partner_id.name"/>
</div>
```

**Fix:**
- Verify fields exist on record
- Check field access rights
- Reload module

---

### Issue: Pagination Problems

**Check:**
- Number of lines
- Page break CSS
- Paper format

**Fix:**
```bash
# Check paper format in data/report_paperformat.xml
# Adjust margins or page size if needed
```

---

## ✅ Sign-Off Checklist

After all tests pass:

- [ ] All 10 test scenarios passed
- [ ] Detailed verification complete
- [ ] No errors in Odoo logs
- [ ] PDF quality acceptable
- [ ] Performance acceptable (<5s per report)
- [ ] Documentation complete
- [ ] Customization examples tested
- [ ] Ready for production

---

## 📊 Test Results Template

```
Test Date: [DATE]
Tester: [NAME]
Odoo Version: 17.0
Module Version: 17.0.1.0.0

TEST 1 - Customer Invoice: ✅ PASS / ❌ FAIL
TEST 2 - Vendor Bill: ✅ PASS / ❌ FAIL
TEST 3 - Draft Document: ✅ PASS / ❌ FAIL
TEST 4 - Paid Document: ✅ PASS / ❌ FAIL
TEST 5 - Credit Note: ✅ PASS / ❌ FAIL
TEST 6 - Multi-Line Document: ✅ PASS / ❌ FAIL
TEST 7 - Tax Breakdown: ✅ PASS / ❌ FAIL
TEST 8 - Commission Document: ✅ PASS / ❌ FAIL
TEST 9 - Notes & Narration: ✅ PASS / ❌ FAIL
TEST 10 - Empty Fields: ✅ PASS / ❌ FAIL

OVERALL: ✅ APPROVED / ❌ NEEDS REVISION

Notes:
[Additional observations]
```

---

## 📞 Support

**For issues:**
1. Check troubleshooting section above
2. Review SMART_REPORT_DOCUMENTATION.md
3. Check Odoo logs: `docker-compose logs -f odoo`
4. Contact: dev@osus.ae

**Module:** osus_invoice_report
**Version:** 17.0.1.0.0
**Status:** Production Ready ✅
