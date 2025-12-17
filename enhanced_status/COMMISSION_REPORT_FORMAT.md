# Commission Report - Professional Format (Updated)

## Overview
The commission report has been updated with a professional format that includes proper Odoo external_layout header and footer, similar to standard invoices and payment vouchers. All field references have been verified and corrected to match the actual commission_ax module fields.

## Recent Updates (December 3, 2025)

### 1. Fixed Field References
- Added `commission_ax` module as dependency
- All commission fields now properly reference the actual sale.order model fields
- Verified field names match commission_ax implementation

### 2. Dynamic Calculation Basis Display
Each commission type now shows its actual calculation basis:
- **Unit Price / Sales Value**: Direct percentage of property unit price
- **Order Total (Without Tax)**: Percentage of untaxed order amount
- **Order Total (With Tax)**: Percentage of total order including VAT

### 3. Forced Header and Footer
- Added custom paperformat with proper margins
- Header spacing: 50px
- Top margin: 60px for company header
- Bottom margin: 28px for footer
- Set `report_type='pdf'` to force external_layout rendering

### 4. Proper Report Configuration
- Dynamic filename: `Commission Report - [Order Number]`
- A4 format with portrait orientation
- DPI: 90 for optimal print quality
- Proper header/footer spacing

## Key Features

### 1. Professional Header & Footer
- Uses Odoo's `web.external_layout` template
- Automatic company logo, address, and contact information in header
- Standard footer with page numbers and company details
- Consistent with invoice and payment voucher format

### 2. Report Structure

#### A. Report Title Section
- Centered "COMMISSION REPORT" heading
- Generation timestamp
- Clean, professional appearance

#### B. Customer & Order Information Box
- Highlighted information box with brand color border
- Contains:
  - Order Number
  - Order Date
  - Customer Name
  - Order Status
  - Salesperson
  - Order Total Amount

#### C. Commission Details Table
Professional table with sections:

**EXTERNAL COMMISSIONS**
- Broker commissions
- Referrer commissions
- Cashback commissions
- Other external commissions
- Subtotal row

**INTERNAL COMMISSIONS**
- Agent 1 commissions
- Agent 2 commissions
- Manager commissions
- Director commissions
- Subtotal row

**LEGACY COMMISSIONS**
- Consultant commissions
- Manager (Legacy) commissions

**GRAND TOTAL**
- Highlighted total commission row

#### D. Commission Summary Box
- Bordered summary box
- Line-by-line breakdown:
  - Order Total
  - Total Commission
  - VAT (if applicable)
  - Net Commission Payable

#### E. Footer Note
- Confidentiality notice
- Internal use disclaimer

### 3. Design Elements

#### Colors
- Primary Brand Color: `#800020` (Burgundy)
- Secondary Backgrounds: `#f8f9fa`, `#f1f3f5`
- Text Colors: `#333`, `#666`, `#6c757d`

#### Typography
- Headers: 24px, 700 weight
- Subtitles: 12px
- Table Content: 11px
- Monospace for amounts: Courier New

#### Layout
- Clean, spacious design
- Proper borders and separators
- Responsive column widths
- Professional hover effects on table rows

### 4. Data Display

#### Amount Formatting
- Thousands separator: `,`
- Decimal places: 2
- Currency: AED
- Monospace font for alignment

#### Percentage Formatting
- Two decimal places
- Centered in column

#### Conditional Display
- Shows only sections with data
- "No Commissions Configured" message if empty
- Hides zero-value rows

### 5. Report Generation

#### Access
Available from Sale Order form view:
- Print menu → Commission Report

#### Output
- PDF format
- Professional print layout
- Company branding from Odoo settings

### 6. Technical Details

#### Template ID
- `commission_payout_report_template_final`
- Model: `sale.order`
- Report Type: `qweb-pdf`

#### Dependencies
- Requires `web.external_layout`
- Uses `web.html_container`
- Odoo 17 compatible

## Usage Notes

1. **Header/Footer Customization**
   - Configure company details in Settings → Companies
   - Upload company logo for header
   - Set address, phone, email, website

2. **Report Customization**
   - Modify CSS in template for styling changes
   - Adjust column widths in table structure
   - Update brand colors by changing `#800020`

3. **Multi-Language Support**
   - Report inherits language from context
   - Date formats adapt to user locale

4. **Print Settings**
   - Uses A4 paper size by default
   - Margins controlled by external_layout
   - Page breaks handled automatically

## Comparison with Previous Version

### Before
- Basic styling with inline CSS
- No proper header/footer
- Simple table layout
- Limited information display
- No company branding

### After
- Professional Odoo layout integration
- Company header with logo
- Standard footer with pagination
- Comprehensive information boxes
- Sectioned commission breakdown
- Summary box for quick reference
- Confidentiality notice
- Brand color scheme
- Responsive design

## Maintenance

### File Location
`/reports/commission_report_template.xml`

### Related Files
- `models/sale_order_simple.py` - Commission calculation logic
- `security/ir.model.access.csv` - Report access rights
- `views/commission_menu.xml` - Menu items

## Future Enhancements
- Multi-currency support
- Commission payment tracking
- Historical comparison
- Graphical commission breakdown
- Email template integration
- Batch report generation
