# 🚀 QUICK START DEPLOYMENT GUIDE
## OSUS Sales & Invoicing Dashboard v17.0.2.0.0

---

## ⚡ FAST DEPLOYMENT (5 Minutes)

### Pre-Requisites
- ✅ Odoo 17.0 installed
- ✅ Modules: sale, account, le_sale_type, website, commission_ax
- ✅ PostgreSQL 13+
- ✅ Python 3.10+

---

## 📋 DEPLOYMENT STEPS

### 1. Backup (1 minute)
```bash
# Backup database
pg_dump -U odoo your_database > /backup/db_$(date +%Y%m%d_%H%M%S).sql

# Backup current module (if exists)
cd /path/to/odoo/addons
cp -r osus_sales_invoicing_dashboard osus_sales_invoicing_dashboard.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
```

### 2. Deploy Files (1 minute)
```bash
# Copy module to addons directory
cp -r osus_sales_invoicing_dashboard /path/to/odoo/addons/

# Set correct permissions
sudo chown -R odoo:odoo /path/to/odoo/addons/osus_sales_invoicing_dashboard
sudo chmod -R 755 /path/to/odoo/addons/osus_sales_invoicing_dashboard
```

### 3. Clear Cache (1 minute)
```bash
# Clear database view cache
psql -U odoo -d your_database << 'EOF'
DELETE FROM ir_ui_view WHERE model = 'osus.sales.invoicing.dashboard';
DELETE FROM ir_model_data WHERE module = 'osus_sales_invoicing_dashboard' AND model = 'ir.ui.view';
VACUUM ANALYZE;
EOF
```

### 4. Upgrade Module (1 minute)
```bash
# Stop Odoo
sudo systemctl stop odoo

# Upgrade module
/var/odoo/osusproperties/src/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d your_database \
  -u osus_sales_invoicing_dashboard \
  --stop-after-init

# Start Odoo
sudo systemctl start odoo
```

### 5. Clear Browser Cache (1 minute)
- Press `Ctrl + Shift + Delete`
- Select "Cached images and files"
- Click "Clear data"
- Close all browser tabs
- Open new incognito window

### 6. Verify Deployment (< 1 minute)
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo-server.log | grep -i "osus_sales"

# You should see:
# INFO ... osus_sales_invoicing_dashboard: Loading module...
# INFO ... osus_sales_invoicing_dashboard: Module loaded successfully
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Access Dashboard
1. Login to Odoo
2. Navigate to: **Sales → Sales Dashboard**
3. Dashboard should load in < 2 seconds

### Test Filters (All 7)
1. ✅ Booking Date From/To
2. ✅ Sales Order Types (multi-select)
3. ✅ Invoice Status
4. ✅ Payment Status
5. ✅ Salesperson
6. ✅ Customer
7. ✅ Company

### Verify Charts (All 6)
1. ✅ Sales Funnel (bar chart)
2. ✅ Booking Trend (line chart)
3. ✅ Sales by Type (pie chart)
4. ✅ Payment Status (doughnut chart)
5. ✅ Top Customers (bar chart)
6. ✅ Agent Performance (grouped bar chart)

### Check Tables (All 4)
1. ✅ Order Type Analysis
2. ✅ Agent Commission Breakdown
3. ✅ Detailed Orders (last 50)
4. ✅ Invoice Aging

### Test Exports (All 4)
1. ✅ Export Order Types CSV
2. ✅ Export Agent Commissions CSV
3. ✅ Export Detailed Orders CSV
4. ✅ Export Invoice Aging CSV

---

## 🎯 EXPECTED RESULTS

### Performance
- Dashboard load: < 2 seconds ✅
- Chart render: < 500ms each ✅
- Filter response: < 300ms ✅
- Export generation: < 5 seconds ✅

### Browser Console
- Zero JavaScript errors ✅
- Chart.js loaded successfully ✅
- All widgets initialized ✅

### Odoo Logs
- No Python errors ✅
- No XML parsing errors ✅
- Module upgraded successfully ✅

---

## 🔧 TROUBLESHOOTING

### Issue: Dashboard not loading
**Solution:**
```bash
# Clear browser cache completely
# Restart browser
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo-server.log
```

### Issue: Charts not rendering
**Solution:**
```bash
# Verify Chart.js CDN is accessible
curl -I https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js

# Check browser console for errors
# Press F12 → Console tab
```

### Issue: Filters not working
**Solution:**
```bash
# Restart Odoo service
sudo systemctl restart odoo

# Clear all caches
# Re-test in incognito mode
```

### Issue: Old view still showing
**Solution:**
```bash
# Force clear view cache
psql -U odoo -d your_database << 'EOF'
DELETE FROM ir_ui_view WHERE model = 'osus.sales.invoicing.dashboard';
VACUUM FULL ir_ui_view;
EOF

# Restart Odoo
sudo systemctl restart odoo

# Clear browser cache (Ctrl+Shift+Delete)
```

---

## 📊 MONITORING

### Check Module Status
```bash
# Verify module installed
odoo-bin shell -c /etc/odoo/odoo.conf -d your_database << 'EOF'
env['ir.module.module'].search([('name', '=', 'osus_sales_invoicing_dashboard')])
EOF
```

### Monitor Performance
```bash
# Watch Odoo logs in real-time
tail -f /var/log/odoo/odoo-server.log | grep -E "(osus_sales|dashboard)"

# Monitor database queries
psql -U odoo -d your_database -c "SELECT * FROM pg_stat_activity WHERE query LIKE '%osus%';"
```

### Check Resource Usage
```bash
# CPU and Memory
top -p $(pgrep -f odoo)

# Database connections
psql -U odoo -d your_database -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🎨 CUSTOMIZATION TIPS

### Change Dashboard Title
**File:** `views/dashboard_views.xml:20`
```xml
<h1><i class="fa fa-dashboard"/> Your Custom Title</h1>
```

### Modify Date Range Default
**File:** `models/sales_invoicing_dashboard.py:168-171`
```python
vals['booking_date_from'] = date.today().replace(day=1)  # First of month
vals['booking_date_to'] = date.today()  # Today
```

### Add New Filter
1. Add field to model: `models/sales_invoicing_dashboard.py`
2. Add field to view: `views/dashboard_views.xml`
3. Update @api.depends decorators
4. Update _get_order_domain method
5. Update _onchange_filters method

### Customize Chart Colors
**File:** `models/sales_invoicing_dashboard.py` (chart compute methods)
```python
'backgroundColor': ['#your-color-1', '#your-color-2', ...]
```

---

## 📞 SUPPORT

### Documentation
- Full documentation: `README.md`
- Production report: `PRODUCTION_READY_REPORT_v2.0.0.md`
- Test report: `OSUS_DASHBOARD_TEST_REPORT_20251219.md`

### Logs Location
- Odoo logs: `/var/log/odoo/odoo-server.log`
- PostgreSQL logs: `/var/log/postgresql/`
- Module tests: `osus_sales_invoicing_dashboard/tests/`

### Common Paths
- Module directory: `/path/to/odoo/addons/osus_sales_invoicing_dashboard`
- Odoo binary: `/var/odoo/osusproperties/src/odoo-bin`
- Odoo config: `/etc/odoo/odoo.conf`

---

## 🏆 SUCCESS CRITERIA

All checks below should be ✅ after deployment:

### Installation
- [✅] Module appears in Apps list
- [✅] Module state: "Installed"
- [✅] Module version: 17.0.2.0.0
- [✅] Dependencies installed

### Functionality
- [✅] Dashboard accessible from menu
- [✅] All 7 filters working
- [✅] All 6 charts rendering
- [✅] All 4 tables populating
- [✅] All 4 exports downloading

### Performance
- [✅] Page load < 2 seconds
- [✅] Charts render < 500ms
- [✅] Filters update < 300ms
- [✅] No lag or freezing

### Quality
- [✅] No JavaScript errors
- [✅] No Python errors
- [✅] No XML parsing errors
- [✅] Mobile responsive
- [✅] Browser compatible

---

## 🚀 QUICK COMMANDS REFERENCE

### Restart Odoo
```bash
sudo systemctl restart odoo
```

### View Logs
```bash
tail -f /var/log/odoo/odoo-server.log
```

### Clear Cache
```bash
psql -U odoo -d your_database -c "DELETE FROM ir_ui_view WHERE model = 'osus.sales.invoicing.dashboard';"
```

### Upgrade Module
```bash
odoo-bin -c /etc/odoo/odoo.conf -d your_database -u osus_sales_invoicing_dashboard --stop-after-init
```

### Check Module Version
```bash
grep "'version'" osus_sales_invoicing_dashboard/__manifest__.py
```

---

## ✨ DEPLOYMENT COMPLETE!

**If all verification steps pass, your deployment is successful!**

**Access your world-class dashboard at:**
`Sales → Sales Dashboard`

**Enjoy your enterprise-grade analytics! 🎉**

---

**Document Version:** 1.0
**Module Version:** 17.0.2.0.0
**Last Updated:** 2025-12-19
**Status:** Production Ready ✅
