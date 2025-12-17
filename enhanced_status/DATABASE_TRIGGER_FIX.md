# Database Trigger Fix - Orphaned Audit Log

## Issue
PostgreSQL error when updating sale orders:
```
relation "sale_order_audit_log" does not exist
QUERY: INSERT INTO sale_order_audit_log ...
CONTEXT: PL/pgSQL function log_sale_order_changes()
```

## Root Cause
An orphaned database trigger `sale_order_audit_trigger` was calling function `log_sale_order_changes()` which tried to insert records into a non-existent table `sale_order_audit_log`.

This typically occurs when:
- A module with audit functionality was uninstalled but didn't clean up triggers
- Migration scripts created triggers but didn't create the corresponding table
- Manual database changes left orphaned objects

## Resolution

### Actions Taken
1. **Identified the orphaned trigger**:
   - Trigger name: `sale_order_audit_trigger`
   - On table: `sale_order`
   - Function: `log_sale_order_changes()`

2. **Removed orphaned objects**:
   ```sql
   DROP TRIGGER IF EXISTS sale_order_audit_trigger ON sale_order;
   DROP FUNCTION IF EXISTS log_sale_order_changes();
   ```

3. **Verified fix**:
   - ✓ Sale order queries working
   - ✓ Sale order updates working
   - ✓ No trigger errors

## Impact
- **Before**: Any sale order update failed with database error
- **After**: Sale orders can be created/updated normally
- **Risk**: None - the trigger was referencing non-existent functionality

## Prevention
If audit logging is needed in the future:
1. Create the `sale_order_audit_log` table first
2. Define proper Odoo model for the table
3. Then create triggers via migration scripts
4. Ensure module uninstall cleans up triggers

## Testing
```python
# Test performed successfully:
orders = self.env['sale.order'].search([], limit=1)
orders.write({'note': orders.note or ''})
# Result: ✓ No errors
```

---
**Date**: December 3, 2025  
**Fixed By**: Database maintenance  
**Status**: ✓ Resolved
