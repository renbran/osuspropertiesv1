# Quick Reference: Percentage Quantity Fix

## 🎯 One-Command Deploy

```bash
docker-compose exec odoo odoo --update=enhanced_status --stop-after-init && docker-compose restart odoo
```

---

## ✅ What Changed

| Before | After |
|--------|-------|
| 0.0200 Units | 2.00% |
| 0.0380 Units | 3.80% |
| 3.8% → 4% (rounded) | 3.80% (exact) |
| Wrong invoice status | Correct invoice status |

---

## 📋 Quick Verification

### 1. Check a Sale Order
- Open any sale order
- **Quantity** column shows `X.XX%` ✓
- **Invoiced** column shows `X.XX%` ✓
- Exactly 2 decimal places

### 2. Check an Invoice
- Open any invoice
- **Quantity** column shows `X.XX%` ✓
- Format matches sale order

### 3. Check Invoice Status
- Fully invoiced orders = `Fully Invoiced` status
- Partially invoiced = `To Invoice` status
- No rounding errors

---

## 🐛 Quick Fixes

### Percentages not showing?
```bash
# Clear cache + hard refresh
Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

### Migration didn't run?
```bash
# Run manual script
docker-compose exec odoo bash
cd /mnt/extra-addons/enhanced_status
odoo shell -d your_database_name < fix_qty_invoiced.py
```

### Wrong invoice status?
```bash
# Recompute manually
docker-compose exec odoo odoo shell -d your_database_name
>>> env['sale.order'].search([('state', 'in', ['sale', 'done'])])._compute_invoice_status()
>>> env.cr.commit()
```

---

## 📞 Files Changed

- `views/sale_order_simple_view.xml` - Percentage widgets
- `__manifest__.py` - Version → 17.0.1.0.1
- `migrations/17.0.1.0.1/post-migrate.py` - Data fix
- `fix_qty_invoiced.py` - Manual script

---

## 🔄 Rollback

```bash
docker-compose stop odoo
docker-compose exec db psql -U odoo odoo < backup_file.sql
# Revert version in __manifest__.py to 17.0.1.0.0
docker-compose restart odoo
```

---

**Time:** 5-10 minutes | **Risk:** Low | **Reversible:** Yes
