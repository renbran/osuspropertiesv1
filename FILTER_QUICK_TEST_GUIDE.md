# Quick Filter Testing Guide

## ✅ What Should Work Now

When you change any filter in the dashboard, **all data should update instantly** without needing to refresh the page.

### Filters Available:

1. **📅 Date Range** → "Booking Date From" & "Booking Date To"
2. **📦 Order Types** → "Sales Order Types" (multi-select)
3. **👤 Salesperson** → "Salesperson (Agent1)"
4. **🏢 Customer** → "Customer"
5. **📊 Invoice Status** → Radio buttons (All, Not Invoiced, Pending, Fully Invoiced)
6. **💳 Payment Status** → Radio buttons (All, Not Paid, Partial, In Payment, Paid)

## 🧪 How to Test Each Filter

### Test 1: Date Range
```
1. Go to Sales & Invoicing Dashboard
2. Change "Booking Date From" to today's date
3. Notice: All KPI numbers change instantly
4. Chart "Monthly Booking Trend" updates
```

### Test 2: Order Type
```
1. In "Sales Order Types" field, select "Standard" (or any available type)
2. Notice: "Total Booked Sales" amount changes
3. "Sales by Order Type" pie chart updates instantly
4. Agent commission calculations update
```

### Test 3: Salesperson Filter
```
1. Click "Salesperson" dropdown
2. Select a salesperson name
3. Notice: "Agent Commission Performance" chart updates
4. "Agent Commissions" table shows only that agent's data
```

### Test 4: Customer Filter
```
1. Click "Customer" dropdown
2. Select a customer
3. Notice: "Detailed Orders" table shows only that customer's orders
4. Revenue KPIs update accordingly
```

### Test 5: Invoice Status
```
1. Click "Pending to Invoice" radio button
2. Notice: 
   - "Orders to Invoice" count appears
   - "Detailed Orders" table shows only pending orders
   - Revenue metrics change
```

### Test 6: Payment Status
```
1. Click "Partially Paid" radio button
2. Notice:
   - "Outstanding Amount" (amount_to_collect) updates
   - Invoice aging table updates
   - Payment status chart changes
```

### Test 7: Combined Filters (Most Important!)
```
1. Set date range: Last 30 days
2. Select order type: "Standard"
3. Select salesperson: "John Doe"
4. Select invoice status: "Pending to Invoice"
5. Select payment status: "Partial"

Expected: ALL KPIs, charts, and tables update smoothly in <2 seconds
```

## 🚨 Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| Filters don't seem to work | Hard refresh: `Ctrl+Shift+R` |
| Old data still showing | Clear cache: `Ctrl+Shift+Delete` |
| Charts blank/not loading | Wait 3 seconds, charts load async |
| Numbers show "0" when filtering | Check if data matches your filters |
| Update takes >5 seconds | Normal for large datasets (10k+ orders) |

## 📍 Where to Find the Dashboard

**URL:** `http://your-server/web#id=1&model=osus.sales.invoicing.dashboard&view_type=form`

**Menu Path:** 
- Sales > Sales & Invoicing Dashboard
- OR Settings > Technical > OSUS Sales & Invoicing Dashboard

## 🎯 Expected Behavior

✅ **When you change a filter:**
- All dependent KPI numbers update immediately
- Charts redraw with new data
- Tables recalculate and display filtered results
- **No manual refresh or page reload needed**

✅ **Performance:**
- Update should take < 2 seconds for normal datasets
- Smooth transitions, no flickering

✅ **Multiple filters:**
- You can combine any filters
- They work together logically (AND operator)
- Results automatically recalculate

## 🔧 How It Works (Technical)

1. You change a filter field in the form
2. Odoo triggers `_onchange_filters()` method
3. Method calls `self.invalidate_cache()` to clear stale data
4. Method accesses all computed fields to force recalculation
5. `_compute_metrics()` runs with new filter domain
6. KPIs, charts, tables all regenerate using new filters
7. Form updates with new values displayed
8. All happens in <2 seconds without page reload

## 📝 Filter Logic Reference

**Invoice Status Filter:**
- `All` = Show all orders (no filter)
- `Not Invoiced` = invoice_status = 'no'
- `Pending to Invoice` = invoice_status = 'to invoice'
- `Fully Invoiced` = invoice_status = 'invoiced'

**Payment Status Filter:**
- `All` = Show all invoices (no payment filter)
- `Not Paid` = payment_state = 'not_paid'
- `Partial` = payment_state = 'partial'
- `In Payment` = payment_state = 'in_payment'
- `Paid` = payment_state = 'paid'

**Date Range:**
- `From` = Orders with booking_date >= selected date
- `To` = Orders with booking_date <= selected date
- Both can be used together

## ✅ Deployment Status

**Version:** 17.0.1.0.2
**Server:** 139.84.163.11 (production)
**Database:** osusproperties
**Status:** ✅ Live and working

---

**Last Updated:** December 18, 2025
**Fix Applied:** Filter recalculation with cache invalidation
