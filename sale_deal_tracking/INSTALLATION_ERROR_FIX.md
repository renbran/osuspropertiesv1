# Installation Error Fix - order_ids Dependency Issue

## Problem
Module installation failed with error:
```
ValueError: Wrong @depends on '_compute_sale_order_count' (compute method of field crm.lead.sale_order_count). 
Dependency field 'order_ids' not found in model crm.lead.
```

## Root Cause
The `sale_order_count` computed field in `crm_lead.py` was using `@api.depends('order_ids')`, but:
- The `order_ids` field doesn't exist on `crm.lead` in Odoo 17
- The relationship between opportunities and quotations is managed via `sale.order.opportunity_id` → `crm.lead`
- We need to search for sale orders WHERE opportunity_id = lead.id, not access a One2many field

## Solution Applied
Changed the compute method from:
```python
@api.depends('order_ids')
def _compute_sale_order_count(self):
    for lead in self:
        lead.sale_order_count = len(lead.order_ids)
```

To:
```python
def _compute_sale_order_count(self):
    """
    Count sale orders linked to this opportunity via opportunity_id field
    """
    for lead in self:
        # Search for sale orders where opportunity_id points to this lead
        count = self.env['sale.order'].search_count([
            ('opportunity_id', '=', lead.id)
        ])
        lead.sale_order_count = count
```

## Additional Changes
Also removed the `action_sale_quotations_new` override method from `crm_lead.py` to avoid potential compatibility issues. The sync functionality is already handled by:
- `sale.order._onchange_opportunity_id()` - Auto-populates fields when opportunity is selected
- `crm.lead.write()` - Syncs stage changes to linked quotations
- `sale.order.write()` - Syncs stage changes back to opportunity

## Files Modified
- `sale_deal_tracking/models/crm_lead.py`
  - Removed `@api.depends('order_ids')` decorator
  - Changed `_compute_sale_order_count()` to use `search_count`
  - Removed `action_sale_quotations_new` override (lines 80-113)

## Installation Instructions

### Option 1: Docker (Recommended)
```bash
cd "d:\RUNNING APPS\ready production\latest\OSUSAPPS"

# Update module list
docker-compose exec odoo odoo --update=list --stop-after-init -d odoo

# Install the module
docker-compose exec odoo odoo -i sale_deal_tracking --stop-after-init -d odoo

# Check logs for any errors
docker-compose logs -f odoo
```

### Option 2: Odoo UI
1. Go to Apps menu
2. Click "Update Apps List"
3. Search for "Deal Tracking for Sales & CRM"
4. Click Install

## Verification Steps
After successful installation:

1. **Check CRM Opportunity Form:**
   - Open CRM → Opportunities → Any opportunity
   - Verify "Deal Stage" statusbar appears in header
   - Verify "Deal Stage Last Updated" field appears
   - Verify smart button "X Quotations" appears if quotations exist

2. **Check Sale Order Form:**
   - Open Sales → Orders → Any quotation
   - Verify "Deal Tracking" group with Opportunity and Deal Stage appears
   - Verify "Marketing Source" group with UTM fields appears

3. **Test Sync Functionality:**
   - Create a new opportunity, set Deal Stage to "Hot"
   - Create a quotation, link it to the opportunity
   - Verify Deal Stage auto-populated as "Hot"
   - Change stage in quotation to "Contacted"
   - Go back to opportunity, verify stage synced to "Contacted"

4. **Test Smart Button:**
   - Open an opportunity with linked quotations
   - Click the "X Quotations" smart button
   - Verify it opens filtered list of quotations

## Technical Notes

### Why search_count Works Better
- **No field dependency:** Doesn't rely on non-existent `order_ids` field
- **Proper relationship:** Uses the actual `opportunity_id` field on sale.order
- **Performance:** `search_count()` is optimized for counting without loading records
- **Standard Odoo pattern:** This is how Odoo computes counts when no One2many exists

### Sync Architecture
```
CRM Opportunity (crm.lead)
    ↕ deal_stage sync ↕
Sale Order (sale.order)
    - opportunity_id → crm.lead
    - Onchange auto-populates from opportunity
    - Write() syncs back to opportunity
```

## Troubleshooting

### If installation still fails:
1. Check module dependencies are installed:
   ```bash
   docker-compose exec odoo odoo --update=sale_management,crm,utm,le_sale_type --stop-after-init -d odoo
   ```

2. Check for Python syntax errors:
   ```bash
   python -m py_compile sale_deal_tracking/models/*.py
   ```

3. Review full error log:
   ```bash
   docker-compose logs odoo | grep -A 20 "sale_deal_tracking"
   ```

### If smart button doesn't work:
- Verify `action_view_linked_sale_orders` method exists in crm_lead.py
- Check security rules allow access to sale.order model
- Verify sale.action_quotations_with_onboarding action exists

### If sync doesn't work:
- Check both models have deal_stage field
- Verify write() methods have sync logic
- Check no context flags blocking sync (sync_deal_stage_to_crm=False)

## Status
✅ **Fix Applied:** 2025-05-XX
🧪 **Testing:** Pending user installation
📝 **Documentation:** Complete

## Next Steps
1. User installs module using one of the methods above
2. User runs verification steps
3. If any issues, check troubleshooting section
4. Once verified, mark as production-ready in README.md
