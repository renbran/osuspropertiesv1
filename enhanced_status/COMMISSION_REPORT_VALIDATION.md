# Commission Report Field Validation

## Date: December 3, 2025

## Validated Fields and Their Sources

### External Commission Fields (from commission_ax)
| Field Name | Display Name | Calculation Base Field | Rate Field | Amount Field | Status |
|------------|--------------|------------------------|------------|--------------|--------|
| broker_partner_id | Broker Partner | broker_calculation_base | broker_rate | broker_amount | ✅ Validated |
| referrer_partner_id | Referrer Partner | referrer_calculation_base | referrer_rate | referrer_amount | ✅ Validated |
| cashback_partner_id | Cashback Partner | cashback_calculation_base | cashback_rate | cashback_amount | ✅ Validated |
| other_external_partner_id | Other External | other_external_calculation_base | other_external_rate | other_external_amount | ✅ Validated |

### Internal Commission Fields (from commission_ax)
| Field Name | Display Name | Calculation Base Field | Rate Field | Amount Field | Status |
|------------|--------------|------------------------|------------|--------------|--------|
| agent1_partner_id | Agent 1 | agent1_calculation_base | agent1_rate | agent1_amount | ✅ Validated |
| agent2_partner_id | Agent 2 | agent2_calculation_base | agent2_rate | agent2_amount | ✅ Validated |
| manager_partner_id | Manager | manager_calculation_base | manager_rate | manager_amount | ✅ Validated |
| director_partner_id | Director | director_calculation_base | director_rate | director_amount | ✅ Validated |

### Legacy Commission Fields (from commission_ax)
| Field Name | Display Name | Rate Field | Amount Field | Status |
|------------|--------------|------------|--------------|--------|
| consultant_id | Consultant | consultant_comm_percentage | salesperson_commission | ✅ Validated |
| manager_id | Manager (Legacy) | manager_comm_percentage | manager_commission | ✅ Validated |

### Computed Total Fields (from commission_ax)
| Field Name | Purpose | Status |
|------------|---------|--------|
| total_external_commission_amount | Sum of all external commissions | ✅ Validated |
| total_internal_commission_amount | Sum of all internal commissions | ✅ Validated |
| total_commission_amount | Grand total of all commissions | ✅ Validated |

### Calculation Base Options
Each commission type can be calculated based on:
1. **unit_price**: Unit Price / Sales Value
2. **order_total_untaxed**: Order Total (Without Tax)
3. **order_total**: Order Total (With Tax)

The report dynamically displays the actual calculation basis for each commission type.

## Report Rendering Configuration

### Paper Format Settings
```xml
<record id="paperformat_commission_report" model="report.paperformat">
    <field name="format">A4</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">60</field>     <!-- Space for header -->
    <field name="margin_bottom">28</field>   <!-- Space for footer -->
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_spacing">50</field>  <!-- Force header rendering -->
    <field name="dpi">90</field>
</record>
```

### Report Variables
```xml
<t t-set="o" t-value="o.with_context(lang=lang)"/>
<t t-set="company" t-value="o.company_id"/>
<t t-set="report_type" t-value="'pdf'"/>
```

These variables ensure:
- Language context is preserved
- Company information is accessible for header/footer
- Report type is explicitly set to PDF for proper rendering

## Subtotals and Grand Total Logic

### External Commission Subtotal
```python
total_external = broker_amount + referrer_amount + cashback_amount + other_external_amount
```
Displayed when: `has_external = True` (any external commission > 0)

### Internal Commission Subtotal
```python
total_internal = agent1_amount + agent2_amount + manager_amount + director_amount
```
Displayed when: `has_internal = True` (any internal commission > 0)

### Grand Total Calculation
```python
total_commission = total_external_commission_amount + total_internal_commission_amount + legacy_commissions
```
Displayed when: `has_external OR has_internal OR has_legacy = True`

## Commission Summary Box

### Display Order
1. Order Total (from `o.amount_total`)
2. Total Commission (from `o.total_commission_amount`)
3. VAT (5%) (from `o.amount_tax`) - Only if > 0
4. Net Commission Payable (from `o.total_commission_amount`)

### Data Flow
```
Sale Order → Commission Calculation → Commission Lines → Report Generation
     ↓              ↓                         ↓                  ↓
  Fields      Compute Methods          Storage            Display
```

## Testing Checklist

### Before Printing Report
- [ ] Verify order has commission data configured
- [ ] Check commission_status field
- [ ] Ensure commission calculations are up to date
- [ ] Validate partner assignments

### Report Elements to Verify
- [ ] Company logo appears in header
- [ ] Company contact info in header
- [ ] Order number and date displayed
- [ ] Customer name shown
- [ ] All configured commissions appear
- [ ] Calculation basis is correct for each
- [ ] Rates display with 2 decimals
- [ ] Amounts show with thousands separator
- [ ] Subtotals are accurate
- [ ] Grand total is correct
- [ ] Page numbers in footer
- [ ] Confidential notice at bottom

## Dependencies

### Required Modules
1. **sale**: Base Sales module
2. **le_sale_type**: Sale type management
3. **sale_deal_tracking**: Deal tracking functionality
4. **commission_ax**: Commission calculation engine

### Module Load Order
```
sale → le_sale_type → sale_deal_tracking → commission_ax → enhanced_status
```

## File Locations

### Template
`/reports/commission_report_template.xml`

### Model
`/models/commission_report.py` (Abstract model for report generation)

### Dependencies
`/__manifest__.py` (depends field updated)

## Validation Results

✅ **All fields validated against commission_ax module**
✅ **Calculation bases properly mapped**
✅ **Subtotal logic verified**
✅ **Grand total computation confirmed**
✅ **Header/footer forced with paperformat**
✅ **Report variables properly set**
✅ **Dynamic filename configured**
✅ **No syntax errors in template**
✅ **Module upgrade successful**

## Sample Data from Screenshot

Order: ES/10/7661
- Broker (DESEA GLOBAL): 5.00% of Unit Price = 33,750.00 AED
- Agent 1 (WESSAM SIMON): 0.30% of Untaxed Total = 2,025.00 AED
- Manager (SETAREH TOFIGHI): 0.15% of Untaxed Total = 1,012.50 AED
- Director (HISHAM ELASSAAD): 0.50% of Unit Price = 3,375.00 AED

**External Subtotal**: 33,750.00 AED
**Internal Subtotal**: 6,412.50 AED
**Total Commission**: 40,162.50 AED

All calculations matched the screenshot data! ✅
