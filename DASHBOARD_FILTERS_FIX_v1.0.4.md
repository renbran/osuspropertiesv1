# Dashboard Filters Fix - Version 17.0.1.0.4

## Problem
Filters were not taking effect when changed in the dashboard form. Users reported that changing any filter (date range, customer, salesperson, etc.) did not update the dashboard data (KPIs, charts, tables).

## Root Cause Analysis
The issue was that Odoo's `@api.onchange` decorator runs in memory but does **not automatically persist changes to the database**. This meant:

1. When a user changed a filter field, the onchange method ran
2. Computed fields recalculated from the **in-memory filter values**
3. However, the record was never saved, so the **database still had old filter values**
4. On the next form refresh or reload, stale filter values from the database were shown
5. This created an illusion that filters don't work

## Solution Implemented

### 1. Enhanced Python Onchange Handler
**File:** `models/sales_invoicing_dashboard.py`

The `_onchange_filters()` method now:
- Explicitly invalidates the record cache: `self.invalidate_cache()`
- Accesses all computed fields to force recalculation from current (in-memory) filter values
- This triggers Odoo's form framework to detect changed computed fields and refresh them in the UI

```python
@api.onchange(...filter_fields...)
def _onchange_filters(self):
    self.invalidate_cache()
    # Access all computed fields to trigger computation
    _ = self.posted_invoice_count
    _ = self.chart_sales_by_type
    # ... etc for all 18 computed fields
```

### 2. New API Method for Data Refresh
**File:** `models/sales_invoicing_dashboard.py`

Created `update_filters_and_refresh(filters_data)` method that:
- Takes a dict of filter field names and values
- Saves filters to the database via `rec.flush()`
- Clears caches to ensure fresh computation
- Returns all 18 computed field values
- Can be called via RPC for AJAX-style updates

This provides a fallback if form onchange doesn't work as expected.

### 3. Enhanced Dashboard Filter Handler
**File:** `static/src/js/dashboard_filters.js`

Updated JavaScript module with:
- `refreshDashboardData(filterValues)` async method that calls the API endpoint
- `initializeFilterListeners(params)` method for setting up event listeners
- Proper error handling and debugging output
- Support for both direct API calls and form-based refresh

### 4. Form View Updates
**File:** `views/dashboard_views.xml`

- Added CSS class `o_dashboard_filter` to all 7 filter fields
- Added instructional message: "💡 Filters update automatically - just change values below"
- These classes can be used by JavaScript to identify filter fields for event binding

## How It Works Now

### Scenario: User changes a filter (e.g., date range)

1. **User Interface:** User modifies a filter field value (e.g., sets booking_date_from)
2. **Odoo Framework:** Form's onchange handler is triggered
3. **Server-Side:** `_onchange_filters()` method runs:
   - Clears cache
   - Accesses all computed fields (KPIs, charts, tables)
   - These fields recalculate from the NEW in-memory filter values
4. **Form Update:** Odoo detects that computed fields have changed values
5. **UI Refresh:** Form automatically displays updated values for all computed fields
6. **Result:** User sees dashboard data update immediately

### Optional: JavaScript Auto-Save (Future)

If the form-based approach encounters issues, the JavaScript module can:
1. Listen to filter field changes
2. Automatically trigger form save
3. Call the server API to update filters
4. Refresh the dashboard data

## Version Changes

- **v17.0.1.0.3:** Initial filter implementation with empty onchange
- **v17.0.1.0.4:** Fixed onchange handler + API method + enhanced JS module

## Testing Checklist

- [ ] Change booking_date_from → KPIs update within 1-2 seconds
- [ ] Change booking_date_to → Charts redraw
- [ ] Select order type → Data filters correctly
- [ ] Select salesperson → Commission data changes
- [ ] Select customer → Tables filter to that customer
- [ ] Combine multiple filters → All work together
- [ ] Reload dashboard → Filters persist (saved to DB)
- [ ] Open browser console → No JavaScript errors
- [ ] Check Odoo logs → No Python exceptions

## Files Modified

1. `__manifest__.py` - Version bump to 17.0.1.0.4
2. `models/sales_invoicing_dashboard.py` - Enhanced onchange + API method
3. `static/src/js/dashboard_filters.js` - Improved RPC handler
4. `views/dashboard_views.xml` - Added CSS classes + help text

## Deployment Steps

1. Upload all modified files to server
2. Log in to Odoo web interface
3. Go to Apps → Update Apps List
4. Search for "OSUS Sales & Invoicing Dashboard"
5. Click the module → Upgrade button
6. Wait for module to upgrade (should complete in seconds)
7. Navigate to Dashboard
8. Test filters - they should now work

## If Filters Still Don't Work

**Advanced Debugging:**

1. Open browser console (F12)
2. Check for JavaScript errors
3. Check Python logs on server: `tail -f /var/log/odoo/odoo.log`
4. Try the JavaScript-based API call:

```javascript
// In browser console
var rpc = require('web.rpc');
rpc.query({
    model: 'osus.sales.invoicing.dashboard',
    method: 'update_filters_and_refresh',
    args: [{
        'booking_date_from': '2025-01-01',
        'booking_date_to': '2025-12-31',
    }]
}).then(result => console.log('Success:', result))
   .catch(error => console.error('Error:', error));
```

## Technical Notes

- The singleton pattern (one dashboard record) ensures all users see the same filters
- Computed fields automatically recalculate when their @api.depends fields change
- Cache invalidation is critical - without it, Odoo returns cached values
- The form framework automatically detects computed field changes and refreshes them
- No manual field return values needed - Odoo handles the refresh automatically

---

**Version:** 17.0.1.0.4  
**Date:** 2025-12-19  
**Author:** OSUS Development  
**Status:** Ready for Testing
