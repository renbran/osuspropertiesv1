# Smart Invoice/Bill Report System
**Odoo 17 Dynamic Report Framework**

## Overview
The Smart Report System is an advanced, adaptive reporting framework that intelligently adjusts invoice and bill layouts based on document type, content, and configuration. It provides a unified, professional template that displays differently for:
- **Customer Invoices** (out_invoice)
- **Vendor Bills** (in_invoice)
- **Credit Notes** (out_refund, in_refund)

---

## Architecture

### Components

#### 1. **Smart Report Helper** (`smart_report_helper.py`)
Core logic model providing detection and formatting utilities:

```python
# Document Type Detection
detect_document_type(move) → 'invoice' | 'bill' | 'credit_note'
is_bill(move) → bool
is_invoice(move) → bool
is_credit_note(move) → bool
is_commission_document(move) → bool

# Header Customization
get_document_title(move) → str
get_header_color(move) → hex color
get_accent_color(move) → hex color

# Amount Formatting
format_amount(amount, currency_symbol) → formatted string
format_currency(amount) → formatted decimal
amount_to_words(amount, currency) → words representation
```

#### 2. **Report Templates**
- `smart_invoice_report.xml` - Main adaptive template
- `report_custom_invoice.py` - Customer invoice model with smart logic
- `report_custom_bill.py` - Vendor bill model with smart logic

#### 3. **Dynamic Rendering Engine**
The template uses conditional logic to:
- Show/hide sections based on document type
- Adapt colors for different document categories
- Dynamically render partner information
- Customize payment instructions
- Display draft/paid status appropriately

---

## Key Features

### 1. **Dynamic Header**
- **Title**: Changes based on document type ("CUSTOMER INVOICE", "VENDOR BILL", "CREDIT NOTE")
- **Colors**: 
  - Invoices: Dark Blue (#1a5c96)
  - Bills: Dark Red (#800020)
  - Customizable via `get_header_color()`

### 2. **Smart Party Display**
- Automatically labels parties correctly:
  - "FROM (Company)" / "TO (Customer)" for invoices
  - "FROM (Vendor)" / "TO (Company)" for bills
  - Shows relevant contact details

### 3. **Dynamic Tax Breakdown**
- Calculates tax summary by rate
- Shows detailed tax breakdown only if multiple rates exist
- Format: "Tax (5%): 50.00 AED"

### 4. **Conditional Payment Instructions**
**For Bills (in_invoice):**
- Shows bank details (IBAN, account number, etc.)
- Payment deadline
- Company bank information

**For Invoices (out_invoice):**
- Shows payment terms
- Payment status
- Custom payment methods

### 5. **Status Indicators**
- **Draft Banner**: Yellow warning if document not yet posted
- **Paid Stamp**: Watermark overlay if fully reconciled
- **State Badge**: Dynamic color-coded status indicator

### 6. **Responsive Layout**
- Professional 2-column party layout
- Table-based line items with proper alignment
- Mobile-friendly formatting
- Proper pagination support for large documents

### 7. **Commission & Project Awareness**
- Detects commission documents via keywords
- Can display project associations
- Extensible for custom fields

---

## Usage

### Basic Report Generation

```python
# In your report model
class ReportCustomInvoice(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_invoice'
    
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        smart_helper = self.env['report.smart.helper']
        
        return {
            'docs': docs,
            'smart_helper': smart_helper,
            'get_document_title': smart_helper.get_document_title,
            'get_header_color': smart_helper.get_header_color,
            # ... other helpers
        }
```

### In QWeb Template

```xml
<t t-set="doc_title" t-value="get_document_title(o)"/>
<t t-set="header_color" t-value="get_header_color(o)"/>

<h2 t-attf-style="color: {{ header_color }};">
    <span t-out="doc_title"/> <span t-field="o.name"/>
</h2>
```

---

## Customization

### Adding Custom Colors

Extend `SmartReportHelper` in your module:

```python
class CustomSmartReportHelper(models.AbstractModel):
    _name = 'report.smart.helper'
    _inherit = 'report.smart.helper'
    
    @staticmethod
    def get_header_color(move):
        if move.partner_id.is_vip:
            return '#FFD700'  # Gold for VIP
        return super().get_header_color(move)
```

### Adding Custom Sections

Edit `smart_invoice_report.xml`:

```xml
<!-- Add after amounts section -->
<t t-if="should_show_custom_section(o)">
    <div style="margin-bottom: 20px;">
        <h5>Custom Section</h5>
        <!-- Your content -->
    </div>
</t>
```

### Extending Helper Logic

```python
def should_show_custom_section(move):
    """Your custom logic"""
    return move.custom_field and move.state == 'posted'
```

---

## Smart Features

### 1. **Type Detection**
Automatically determines document category:
```python
move.move_type in ['out_invoice', 'out_refund']  # Customer invoice
move.move_type in ['in_invoice', 'in_refund']    # Vendor bill
```

### 2. **Conditional Rendering**
Shows/hides content based on availability:
- Partner addresses only if populated
- Payment terms only if configured
- Notes section only if content exists
- Tax breakdown only for multi-rate scenarios

### 3. **Flexible Formatting**
- Automatic currency symbol insertion
- Date format in UK style (DD/MM/YYYY)
- Number formatting with thousand separators
- VAT/Tax ID display when available

### 4. **Professional Styling**
- Color-coded headers and accents
- Consistent spacing and alignment
- Proper table borders and padding
- State-appropriate badges and stamps

---

## Fields Used

### Required Document Fields
- `move_type` - Document classification
- `name` - Document reference
- `invoice_date` - Creation date
- `invoice_date_due` - Payment due date
- `state` - Document state (draft, posted, cancel)
- `partner_id` - Vendor/customer details
- `company_id` - Company details
- `invoice_line_ids` - Line items

### Optional Fields (Auto-detected)
- `narration` - Notes (shown if present)
- `invoice_payment_term_id` - Payment terms
- `payment_state` - Payment status
- `partner_ref` - Vendor reference number
- `ref` - Commission/reference info
- `invoice_origin` - Source document

---

## Report Actions

Register reports in XML:

```xml
<record id="action_report_smart_invoice" model="ir.actions.report">
    <field name="name">Smart Invoice Report</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">osus_invoice_report.report_osus_invoice_document_smart</field>
    <field name="binding_model_id" ref="account.model_account_move"/>
    <field name="binding_type">report</field>
    <field name="paperformat_id" ref="base.paperformat_euro"/>
    <field name="print_report_name">'Report - %s' % (object.name)</field>
</record>
```

---

## Performance Considerations

### Condensed Layout
For documents with many lines (>15):
```python
should_use_condensed_layout(move) → bool
```

### Caching
Smart helper uses static methods for efficiency:
- No database queries in helper methods
- Fast conditional evaluation
- Suitable for bulk reporting

---

## Future Enhancements

### Planned Features
1. **QR Code Integration** - Auto-generate payment QR codes
2. **Multi-Currency Support** - Automatic conversion display
3. **Signature Blocks** - Digital signature integration
4. **Audit Trail** - Document approval/sign-off tracking
5. **Custom Fonts** - User-defined styling per company
6. **Template Variants** - Different layouts per company/department

### Extension Points
```python
# Override in custom module
def get_additional_sections(move):
    """Add custom sections to report"""
    pass

def customize_colors(move):
    """Apply custom branding"""
    pass
```

---

## Best Practices

### 1. **Always Check Document Type**
```xml
<t t-if="o.move_type in ['in_invoice', 'in_refund']">
    <!-- Bill-specific content -->
</t>
```

### 2. **Use Helper Functions**
```xml
<!-- Good -->
<span t-out="get_document_title(o)"/>
<div t-attf-style="color: {{ get_header_color(o) }}">

<!-- Avoid hardcoding -->
<span>Invoice</span>
<div style="color: #800020">
```

### 3. **Format Amounts Consistently**
```xml
<!-- Good -->
<span t-esc="format_number(line.price_total)"/>

<!-- Avoid -->
<span t-field="line.price_total"/>
```

### 4. **Handle Missing Data**
```xml
<!-- Good -->
<t t-if="o.partner_id.vat">
    <div>VAT: <span t-field="o.partner_id.vat"/></div>
</t>

<!-- Avoid showing empty sections -->
<div>VAT: <span t-field="o.partner_id.vat"/></div>
```

---

## Troubleshooting

### Report Not Appearing
1. Ensure `smart_invoice_report.xml` is in manifest data
2. Clear cache: `docker-compose exec odoo odoo --stop-after-init -d odoo`
3. Check report action is registered

### Colors Not Applying
1. Verify `t-attf-style` syntax is correct
2. Check CSS precedence in report assets
3. Use inline styles as override

### Data Not Showing
1. Verify fields exist on move object
2. Check field access rights
3. Use `t-if` to handle missing fields

---

## Migration Guide

### From Legacy Reports

**Before:**
```xml
<h2>INVOICE <span t-field="o.name"/></h2>
```

**After:**
```xml
<h2 t-attf-style="color: {{ header_color }};">
    <span t-out="doc_title"/> <span t-field="o.name"/>
</h2>
```

---

## Support & Maintenance

- Template version: 17.0.1.0.0
- Last updated: October 2025
- Odoo version: 17.0+
- Python version: 3.10+

For issues or enhancements, contact: dev@osus.ae
