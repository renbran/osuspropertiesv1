# OSUS Properties Odoo 17 Codebase Instructions

## Project Overview
This is an **Odoo 17.0 enterprise property management system** with 60+ custom modules for real estate sales, invoicing, commissions, and property management. The architecture follows standard Odoo conventions with custom OSUS-specific enhancements.

## Core Architecture

### Module Structure Pattern
- **Custom OSUS modules**: `osus_*` (sales dashboard, reports, templates)  
- **Third-party modules**: External addons with original licensing
- **Enhanced modules**: Extensions to base Odoo (commission_lines, enhanced_status)

### Key Dependencies Chain
```
Base: sale, account, website, mail
↓
Enhanced: le_sale_type, commission_ax  
↓
OSUS: osus_sales_invoicing_dashboard, advanced_property_management
```

## Development Workflows

### Local Development (Docker-based)
```bash
# Start environment
setup.bat start  # Windows
./setup.sh start  # Linux

# Module updates
setup.bat update_mod MODULE_NAME
docker exec odoo17_local_testing odoo -u MODULE_NAME -d odoo17_test
```

### Deployment Pipeline
1. **Local testing**: Docker compose with PostgreSQL 15
2. **File deployment**: Use `deploy_dashboard.py` or manual SCP to `139.84.163.11`
3. **Module upgrade**: SSH + `/opt/odoo/odoo-bin -u MODULE -d DB --stop-after-init`
4. **Service restart**: `systemctl restart odoo.service`

## Critical Coding Patterns

### Manifest Files (`__manifest__.py`)
- **Version format**: `17.0.MAJOR.MINOR.PATCH` (e.g., `17.0.1.0.8`)
- **Dependency chain**: Always include `['sale', 'account']` + specific needs
- **Assets structure**: Separate JS/CSS/XML in `web.assets_backend`

### Model Conventions
- **Inheritance pattern**: `_inherit = 'sale.order'` for extensions
- **Field naming**: Use descriptive prefixes (`commission_line_ids`, `osus_*`)
- **API methods**: Use `@api.onchange` + complementary API endpoints for UI filters
- **Logging**: `_logger = logging.getLogger(__name__)` for debugging

### Dashboard Architecture
The `osus.sales.invoicing.dashboard` model demonstrates the pattern:
- **Transient data model** with computed fields
- **Filter fields** + `@api.onchange` methods  
- **Dual API approach**: onchange for UI + HTTP endpoints for persistence
- **JavaScript RPC calls** to `/web/dataset/call_kw` for data updates

### Commission System Integration
- **sale.order** → `commission_line_ids` (One2many)
- **commission.line** → `sale_order_id` + `partner_id` (commission agent)
- **purchase.order** → Commission payment tracking via `origin_sale_order_id`

## File Organization Standards

### Security Files
- `security/ir.model.access.csv`: Model access rights
- `security/MODULE_security.xml`: Record rules and groups

### Assets Management  
- **JS**: `static/src/js/` - Use ES6 + Odoo RPC patterns
- **CSS/SCSS**: `static/src/scss/` - Follow BEM naming
- **XML Templates**: `static/src/xml/` - QWeb templates for frontend

## Debugging & Testing

### Filter Issues Resolution
When dashboard filters don't work:
1. **Check version bump** in `__manifest__.py` (cache invalidation)
2. **Verify @api.onchange** methods have proper field dependencies
3. **Add API endpoint** for JavaScript RPC calls  
4. **Test JavaScript console** for RPC errors

### Module Update Process
```bash
# Clear browser cache + restart Odoo service
# Check logs: docker-compose logs -f odoo
# Verify database: SELECT * FROM ir_module_module WHERE name = 'MODULE';
```

### Common Gotchas
- **Module dependencies**: Missing deps cause silent failures
- **Field inheritance**: Use `_inherit` not `_name` for extensions  
- **Asset loading**: Version bump required for JS/CSS changes
- **Database persistence**: `@api.onchange` runs in memory only

## Property Management Specifics

### Property Model Extensions
- **Advanced Property Management**: Full property lifecycle (sale/rental/auction)
- **Commission Integration**: Agent commissions tied to property sales
- **Geolocation**: Uses `base_geolocalize` for property mapping

### Website Integration  
- **Frontend assets**: `web.assets_frontend` for public-facing features
- **Portal extensions**: Customer property dashboards and applications

## Quick Commands Reference

```bash
# Environment
setup.bat start|stop|restart|logs|build|shell

# Module operations  
docker exec odoo17_local_testing odoo -i MODULE_NAME -d odoo17_test
docker exec odoo17_local_testing odoo -u MODULE_NAME -d odoo17_test

# Database access
docker exec -it odoo17_postgres psql -U odoo -d odoo17_test

# Production deployment
python deploy_dashboard.py  # Automated deployment script
```

## Performance & Caching
- **@ormcache decorator**: Use for expensive computations
- **Computed fields**: Store=True for frequently accessed data
- **Database indexing**: Add indexes for filtered fields in large tables