# Dashboard Deployment Commands

## Summary of Changes
- ✅ Real-time data updates with cache invalidation
- ✅ Professional UI/UX redesign with modern styling
- ✅ Proper field relationships for accurate data pulling
- ✅ New monetary metrics: Total Invoiced Amount, Total Pending Amount
- ✅ Friendly payment state labels in charts
- ✅ Enhanced chart styling with borders and colors
- ✅ Responsive design for all devices

## Server Deployment

Run these commands on the remote server (139.84.163.11):

```bash
# SSH to server
ssh -i ~/.ssh/id_ed25519_osus root@139.84.163.11

# Once connected, run:
cd /var/odoo/osusproperties

# 1. Update and rebuild the dashboard module
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d osusproperties --no-http --stop-after-init -u osus_sales_invoicing_dashboard

# 2. Restart Odoo service (adjust service name as needed)
sudo systemctl restart odoo
# OR if using supervisor:
# sudo supervisorctl restart odoo-server
# OR if running in Docker:
# docker-compose restart odoo (or your container name)

# 3. Verify logs
tail -f logs/odoo.log
```

## Browser Testing

After deployment:
1. Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Navigate to **Sales > Sales & Invoicing Dashboard**
3. Verify:
   - ✅ Dashboard loads without errors
   - ✅ Charts render properly
   - ✅ KPI buttons show counts
   - ✅ Amount summary displays monetary values
   - ✅ Filters work correctly
   - ✅ Charts update when filters change
   - ✅ Mobile responsive design works

## Quick Commands

### Check Dashboard Module Status
```bash
cd /var/odoo/osusproperties
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf << EOF
env['osus.sales.invoicing.dashboard'].search([])
EOF
```

### Check Module Logs
```bash
cd /var/odoo/osusproperties
grep "osus_sales_invoicing_dashboard" logs/odoo.log | tail -20
```

### Rollback (if needed)
```bash
cd /var/odoo/osusproperties
git -C /var/odoo/osusproperties checkout HEAD~3  # Adjust number as needed
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d osusproperties --no-http --stop-after-init -u osus_sales_invoicing_dashboard
sudo systemctl restart odoo
```

## Git Changes
- Commit 1: Dashboard CSS redesign + real-time updates
- Commit 2: Refactored data pulling with proper field relationships
- Commit 3: Added monetary amount metrics to UI
