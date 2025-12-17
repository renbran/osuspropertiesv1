# Commission Report Security Configuration

## Overview
The Commission Payout Report has been restricted to authorized users only for confidentiality and data protection.

## Security Group

### `group_commission_report_viewer`
- **Name**: Commission Report Viewer
- **Category**: Sales Management
- **Implied Groups**: `sales_team.group_sale_manager`
- **Purpose**: Controls access to commission payout reports

## Access Restrictions

### Report Access
The Commission Payout Report is now restricted to users with the `Commission Report Viewer` group.

**Report ID**: `commission_payout_report`
**Binding**: Sale Order (`sale.order`)
**Groups Required**: `enhanced_status.group_commission_report_viewer`

### Who Can Access?
1. **Sales Managers** - Automatically granted via implied groups
2. **Workflow Managers** - Can be granted explicit access
3. **Custom Roles** - Must be explicitly assigned the group

## Configuration

### Assigning Access to Users

#### Method 1: Via Settings UI
1. Navigate to: **Settings** → **Users & Companies** → **Users**
2. Select the user
3. Go to **Access Rights** tab
4. Under **Sales Management**, enable **Commission Report Viewer**
5. Save

#### Method 2: Via Groups
1. Navigate to: **Settings** → **Users & Companies** → **Groups**
2. Search for "Commission Report Viewer"
3. Add users to the group

### Default Access
- **Sales Managers**: ✓ Automatic access (via implied groups)
- **Sales Users**: ✗ No access by default
- **Base Users**: ✗ No access

## Security Benefits

1. **Confidentiality**: Commission data is sensitive financial information
2. **GDPR Compliance**: Restricts personal earnings data to authorized personnel
3. **Audit Trail**: Odoo logs all report access attempts
4. **Role-Based**: Follows principle of least privilege

## Report Features

### Available in Print Menu
When users with proper access view a Sale Order:
- **Print** → **Commission Payout Report** (visible only to authorized users)

### Report Content (Confidential)
- External commissions (Broker, Agent 1, Agent 2, Referrer, Cashback, Other)
- Internal commissions (Manager, Director, Salesperson)
- Legacy commissions (Consultant, Manager)
- Calculation basis per commission type
- Total commission amounts and subtotals

## Troubleshooting

### Report Not Visible
**Symptom**: Commission Payout Report doesn't appear in Print menu

**Solution**:
1. Verify user has `Commission Report Viewer` group assigned
2. Check if user has `Sales Manager` role (auto-includes access)
3. Clear browser cache and refresh
4. Re-login to update session permissions

### Access Denied Error
**Symptom**: "You are not allowed to access this document" error

**Solution**:
1. Contact your administrator
2. Request `Commission Report Viewer` access
3. Verify you need access for your job role

## Technical Details

### XML Configuration

**Security Group Definition** (`security/security.xml`):
```xml
<record id="group_commission_report_viewer" model="res.groups">
    <field name="name">Commission Report Viewer</field>
    <field name="category_id" ref="base.module_category_sales_management"/>
    <field name="implied_ids" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    <field name="comment">Can view and print commission payout reports - Restricted to Sales Managers and above</field>
</record>
```

**Report Action** (`reports/commission_report_template.xml`):
```xml
<record id="commission_payout_report" model="ir.actions.report">
    <field name="groups_id" eval="[(4, ref('enhanced_status.group_commission_report_viewer'))]"/>
    <!-- ... other fields ... -->
</record>
```

## Compliance Notes

- **Data Classification**: Confidential - Financial Data
- **Retention**: Per company policy for financial records
- **Access Logging**: Enabled via Odoo audit log
- **Review Period**: Access rights should be reviewed quarterly

## Related Documentation
- [COMMISSION_REPORT_FORMAT.md](./COMMISSION_REPORT_FORMAT.md) - Report format and layout
- [COMMISSION_REPORT_VALIDATION.md](./COMMISSION_REPORT_VALIDATION.md) - Field validation details
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Module overview

---
**Last Updated**: December 2024  
**Module Version**: 17.0.1.0.0  
**Security Level**: Confidential
