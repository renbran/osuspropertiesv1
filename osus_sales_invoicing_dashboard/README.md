# OSUS Sales & Invoicing Dashboard

## Features
- Real-time KPI tracking
- Interactive Chart.js visualizations
- Multi-dimensional filtering
- CSV data export
- Commission tracking
- Invoice aging analysis

## Installation
1. Copy module to `addons/` directory
2. Update app list: `odoo-bin -u osus_sales_invoicing_dashboard`
3. Chart.js loads via CDN with local fallback

## Usage
Navigate to: Sales > Sales & Invoicing Dashboard

## Configuration
- Set date range filters
- Select order types, customers, or salespersons
- Click "Refresh Dashboard" to update metrics

## Technical Details
- Odoo Version: 17.0
- Dependencies: sale, account, le_sale_type, commission_ax, website
- External Libraries: Chart.js 4.4.0 (CDN), fallback to Odoo's local copy
- License: LGPL-3

## Support
Contact: dev@osusproperties.com
