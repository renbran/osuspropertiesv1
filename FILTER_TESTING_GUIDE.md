# Dashboard Filter Testing - Quick Guide

## ✅ What Should Now Work

Dashboard filters should now update **instantly and smoothly** without needing to refresh the page.

---

## 🧪 Quick Test

### Step 1: Open Dashboard
```
URL: http://your-server/web#id=1&model=osus.sales.invoicing.dashboard&view_type=form
OR
Menu: Sales > Sales & Invoicing Dashboard
```

### Step 2: Clear Browser Cache
```
Press: Ctrl+Shift+Delete (Windows/Linux) or Cmd+Shift+Delete (Mac)
Select: Clear all or "All time"
Press: Clear
```

### Step 3: Refresh Dashboard
```
Press: Ctrl+Shift+R (hard refresh)
Wait for page to fully load
```

### Step 4: Change a Filter

**Test 1 - Date Range:**
```
1. Find "Booking Date From" field
2. Click and change to TODAY's date
3. WATCH: All numbers should change within 2 seconds
   ✓ Total Booked Sales
   ✓ Pending to Invoice amount
   ✓ Charts redraw with new data
```

**Test 2 - Order Type:**
```
1. Find "Sales Order Types" field (multi-select tags)
2. Select an order type (e.g., "Standard")
3. WATCH: 
   ✓ "Sales by Order Type" pie chart updates
   ✓ Commission numbers change
   ✓ All KPIs update
```

**Test 3 - Salesperson:**
```
1. Find "Salesperson" dropdown
2. Select a salesperson name
3. WATCH:
   ✓ "Agent Commission Performance" chart updates
   ✓ Commission table shows only that agent
```

**Test 4 - Customer:**
```
1. Find "Customer" dropdown
2. Select a customer name
3. WATCH:
   ✓ "Detailed Orders" table filters
   ✓ All amounts adjust
```

**Test 5 - Invoice Status:**
```
1. Find "Invoice Status" radio buttons
2. Click "Pending to Invoice"
3. WATCH:
   ✓ "Orders to Invoice" count appears/changes
   ✓ Only pending orders show in "Detailed Orders"
```

**Test 6 - Payment Status:**
```
1. Find "Payment Status" radio buttons
2. Click "Partially Paid"
3. WATCH:
   ✓ "Outstanding Amount" updates
   ✓ "Invoice Aging" table changes
```

### Step 5: Combine Multiple Filters

```
1. Set date range: Last 30 days
2. Select 2 order types
3. Select a salesperson
4. Select "Pending to Invoice"
5. Select "Partial" payment status

EXPECTED: All data updates smoothly in <2 seconds
          No page refresh needed
          All KPIs, charts, tables show filtered data correctly
```

---

## ✓ Expected Behavior

| Action | Before Fix | After Fix |
|--------|-----------|-----------|
| Change date | Data stays same | Updates in 1s ✅ |
| Change order type | Stale data | Fresh data ✅ |
| Change salesperson | No change | Updates in 2s ✅ |
| Multiple filters | Doesn't work | Works smoothly ✅ |
| Page refresh needed | YES ❌ | NO ✅ |
| Auto-save on change | NO ❌ | YES ✅ |

---

## 🚨 Troubleshooting

### Issue: Filters still not updating

**Solution 1 - Clear cache completely:**
```
1. Press Ctrl+Shift+Delete
2. Check "Cookies and other site data"
3. Clear
4. Reload dashboard
```

**Solution 2 - Disable browser cache:**
```
1. Open DevTools (F12)
2. Go to Settings (⚙️ icon)
3. Check "Disable cache (while DevTools is open)"
4. Reload dashboard
```

**Solution 3 - Hard refresh multiple times:**
```
1. Ctrl+Shift+R (hard refresh)
2. Wait for full load
3. Try filter change again
```

### Issue: Charts show "Loading..." forever

**Solution:**
```
1. Wait 5 seconds (charts load async)
2. If still loading, hard refresh: Ctrl+Shift+R
3. Check browser console (F12) for JavaScript errors
```

### Issue: Update takes 5+ seconds

**Expected for:**
- Large datasets (10k+ orders)
- Complex filter combinations
- First load of charts

**Normal for:**
- Standard system usage
- <2 seconds typical

---

## 📊 Dashboard Structure

```
┌─ FILTERS (top)
│  ├─ Date Range
│  ├─ Order Types
│  ├─ Salesperson
│  ├─ Customer
│  ├─ Invoice Status
│  └─ Payment Status
│
├─ KEY METRICS (KPIs)
│  ├─ Total Booked Sales
│  ├─ Pending to Invoice
│  ├─ Total Invoiced
│  ├─ Outstanding Amount
│  ├─ Amount Collected
│  └─ Commission Due
│
├─ CHARTS (auto-update when filters change)
│  ├─ Sales → Invoice → Collection Flow
│  ├─ Monthly Booking Trend
│  ├─ Sales by Order Type
│  ├─ Invoice Payment Status
│  ├─ Top 10 Customers Outstanding
│  └─ Agent Commission Performance
│
└─ TABLES (with filtered data)
   ├─ Order Type Analysis
   ├─ Agent Commissions
   ├─ Detailed Orders
   └─ Invoice Aging
```

---

## 🎯 Performance Expectations

| Action | Time |
|--------|------|
| Filter change recognized | Instant |
| KPIs recalculate | <1 second |
| Charts redraw | <2 seconds |
| Tables refresh | <2 seconds |
| **Total** | **<2.5 seconds** |

---

## ✅ When Everything Works

You'll see:
- ✓ Filter changes instantly affect all displays
- ✓ Numbers update smoothly
- ✓ Charts redraw with new data
- ✓ Tables show filtered results
- ✓ No errors in console
- ✓ No "undefined" values
- ✓ No "loading" spinner stuck

---

## 📝 Report Issues

If something doesn't work:

1. **Note the exact filter combination** you used
2. **Check the time** it takes to update
3. **Open DevTools (F12)** and check Console for errors
4. **Take a screenshot** of the issue
5. **Report:** Dashboard not updating after changing X filter

---

**Last Updated:** December 18, 2025  
**Module Version:** 17.0.1.0.3  
**Status:** ✅ Live on Production
