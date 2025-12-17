#!/bin/bash
# Quick Start & Verification Script for sale_deal_tracking v2.0
# Run this after installing the module to verify everything works

echo "======================================================================"
echo "  Sale Deal Tracking v2.0 - Quick Start & Verification"
echo "======================================================================"
echo ""

# Configuration
DB_NAME="${1:-odoo}"  # Use first argument or default to 'odoo'
MODULE_NAME="sale_deal_tracking"

echo "Database: $DB_NAME"
echo "Module: $MODULE_NAME"
echo ""

# Function to run Odoo shell commands
run_odoo_shell() {
    docker-compose exec odoo odoo shell -d "$DB_NAME" <<EOF
$1
EOF
}

echo "======================================================================"
echo "  STEP 1: Verify Module Installation"
echo "======================================================================"

echo "Checking if module is installed..."
run_odoo_shell "
module = env['ir.module.module'].search([('name', '=', '$MODULE_NAME')])
if module:
    print(f'✓ Module found: {module.name}')
    print(f'  State: {module.state}')
    print(f'  Version: {module.latest_version}')
    if module.state == 'installed':
        print('  ✓ Status: INSTALLED')
    else:
        print(f'  ✗ Status: NOT INSTALLED ({module.state})')
else:
    print('✗ Module not found!')
"

echo ""
echo "======================================================================"
echo "  STEP 2: Verify Models Extended"
echo "======================================================================"

echo "Checking sale.order extensions..."
run_odoo_shell "
fields = ['opportunity_id', 'source_id', 'campaign_id', 'medium_id', 'deal_stage', 'deal_stage_updated']
missing = []
for field in fields:
    if field in env['sale.order']._fields:
        print(f'  ✓ sale.order.{field} exists')
    else:
        print(f'  ✗ sale.order.{field} MISSING!')
        missing.append(field)

if not missing:
    print('✓ All sale.order fields present')
"

echo ""
echo "Checking crm.lead extensions..."
run_odoo_shell "
fields = ['deal_stage', 'deal_stage_updated', 'sale_order_count']
missing = []
for field in fields:
    if field in env['crm.lead']._fields:
        print(f'  ✓ crm.lead.{field} exists')
    else:
        print(f'  ✗ crm.lead.{field} MISSING!')
        missing.append(field)

if not missing:
    print('✓ All crm.lead fields present')
"

echo ""
echo "======================================================================"
echo "  STEP 3: Verify UTM Models Accessible"
echo "======================================================================"

echo "Checking UTM models..."
run_odoo_shell "
models = ['utm.source', 'utm.campaign', 'utm.medium']
for model in models:
    try:
        count = env[model].search_count([])
        print(f'  ✓ {model}: {count} records found')
    except Exception as e:
        print(f'  ✗ {model}: ERROR - {e}')
"

echo ""
echo "======================================================================"
echo "  STEP 4: Verify Views Loaded"
echo "======================================================================"

echo "Checking sale order views..."
run_odoo_shell "
views = env['ir.ui.view'].search([
    ('name', 'ilike', 'deal.tracking'),
    ('model', '=', 'sale.order')
])
print(f'Found {len(views)} sale.order views:')
for view in views:
    print(f'  ✓ {view.name} (priority: {view.priority})')
"

echo ""
echo "Checking crm lead views..."
run_odoo_shell "
views = env['ir.ui.view'].search([
    ('name', 'ilike', 'deal.stage'),
    ('model', '=', 'crm.lead')
])
print(f'Found {len(views)} crm.lead views:')
for view in views:
    print(f'  ✓ {view.name}')
"

echo ""
echo "======================================================================"
echo "  STEP 5: Test Data Creation"
echo "======================================================================"

echo "Creating test UTM source..."
run_odoo_shell "
source = env['utm.source'].search([('name', '=', 'Test Source')], limit=1)
if not source:
    source = env['utm.source'].create({'name': 'Test Source'})
    print(f'  ✓ Created test UTM source (ID: {source.id})')
else:
    print(f'  ✓ Test UTM source already exists (ID: {source.id})')
"

echo ""
echo "Creating test opportunity with deal stage..."
run_odoo_shell "
# Check if test opportunity exists
test_opp = env['crm.lead'].search([('name', '=', 'Test Deal Tracking Opportunity')], limit=1)

if not test_opp:
    # Create test opportunity
    test_opp = env['crm.lead'].create({
        'name': 'Test Deal Tracking Opportunity',
        'type': 'opportunity',
        'partner_id': env['res.partner'].search([], limit=1).id,
        'deal_stage': 'new',
    })
    env.cr.commit()
    print(f'  ✓ Created test opportunity (ID: {test_opp.id})')
    print(f'    Deal Stage: {test_opp.deal_stage}')
else:
    print(f'  ✓ Test opportunity already exists (ID: {test_opp.id})')
    print(f'    Deal Stage: {test_opp.deal_stage}')
"

echo ""
echo "======================================================================"
echo "  STEP 6: Test Synchronization"
echo "======================================================================"

echo "Testing opportunity → sale order sync..."
run_odoo_shell "
# Get or create test opportunity
test_opp = env['crm.lead'].search([('name', '=', 'Test Deal Tracking Opportunity')], limit=1)

if test_opp:
    # Update deal stage
    test_opp.write({'deal_stage': 'hot'})
    print(f'  ✓ Updated opportunity deal_stage to: hot')
    
    # Create quotation
    try:
        action = test_opp.action_sale_quotations_new()
        if action.get('res_id'):
            order = env['sale.order'].browse(action['res_id'])
            print(f'  ✓ Created quotation (ID: {order.id})')
            print(f'    Opportunity linked: {bool(order.opportunity_id)}')
            print(f'    Deal stage synced: {order.deal_stage}')
            if order.deal_stage == 'hot':
                print('  ✅ SYNC TEST PASSED!')
            else:
                print(f'  ✗ SYNC TEST FAILED (expected: hot, got: {order.deal_stage})')
        else:
            print('  ⚠ Quotation created but no res_id returned')
    except Exception as e:
        print(f'  ✗ Error creating quotation: {e}')
else:
    print('  ✗ Test opportunity not found')
"

echo ""
echo "======================================================================"
echo "  STEP 7: Check for Errors in Logs"
echo "======================================================================"

echo "Checking recent Odoo logs for errors related to $MODULE_NAME..."
echo "(Last 50 lines)"
docker-compose logs --tail=50 odoo | grep -i "$MODULE_NAME\|error" | tail -20

echo ""
echo "======================================================================"
echo "  VERIFICATION COMPLETE"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "1. Open Odoo in browser: http://localhost:8069"
echo "2. Go to Sales → Orders → Create"
echo "3. Verify 'Deal Tracking' and 'Marketing Source' sections appear"
echo "4. Go to CRM → Opportunities → Create"
echo "5. Verify 'Deal Stage' statusbar appears in header"
echo "6. Test creating quotation from opportunity and check sync"
echo ""
echo "For more information, see:"
echo "  - README.md (user guide)"
echo "  - IMPLEMENTATION_SUMMARY.md (technical details)"
echo "  - MIGRATION_GUIDE.md (upgrade from v1.0)"
echo ""
echo "======================================================================"
