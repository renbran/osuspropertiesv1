# Payment Voucher with QR Code Report

## Overview
This report template adds QR code functionality to payment and receipt vouchers in Odoo 17. It provides a professional, burgundy-themed voucher with integrated QR code verification.

## Features

### 🎨 Design Elements
- **Burgundy Premium Theme**: Professional gradient header with burgundy (#8B1538) and dark burgundy (#6B2B47)
- **Responsive Layout**: Optimized for A4 paper size
- **Modern Typography**: Clean, readable fonts with proper hierarchy
- **Color-Coded Badges**: Visual distinction between receipts (green) and payments (red)

### 🔍 QR Code Integration
The report includes QR code verification with fallback support:

1. **Primary**: `qr_code_invoice` field (from ingenuity_invoice_qr_code module)
2. **Fallback**: `qr_image` field
3. **No QR**: Displays "QR" placeholder text

The QR code is displayed in the header with "Scan to Verify" text for easy mobile verification.

### 📋 Information Sections

#### Header Section
- **QR Code Box**: 55x55px white box with QR code
- **Voucher Title**: Dynamic "RECEIPT VOUCHER" or "PAYMENT VOUCHER"
- **Voucher Number**: Uses `voucher_number` or `name` field
- **Date**: Formatted as dd/MM/yyyy
- **Company Info**: Name, address, and phone

#### Details Section
Two-column layout with the following fields:

**Left Column:**
- Received From / Paid To (based on transaction type)
- Phone (mobile or phone number)
- Email
- Payment Method

**Right Column:**
- Communication/Memo (from `payment_reference` or `ref`)
- Transaction Type (badge with color coding)
- Remarks (from `remarks` or `payment_description`)
- Status (from `approval_state` or `state`)

#### Amount Section
- **Amount in Words**: Full text representation
  - Uses `amount_total_words` (invoice_report_for_realestate)
  - Falls back to `check_amount_in_words`
  - Or uses currency's `amount_to_text()` method
- **Amount Banner**: Gold gradient banner with formatted amount

#### Signature Section
Three signature boxes:
1. **Created By**: Automatically filled with creator name and date
2. **Reviewed By**: Uses `reviewer_id` and `reviewer_date` fields
3. **Approved By**: Uses `approver_id`/`authorizer_id` and dates

#### Received By Section
- Partner name
- Signature line
- Mobile number
- Date
- ID Copy checkbox

#### Footer Section
- Creation and modification audit trail
- Company branding
- "Thank you" message

## Field Dependencies

### Required Fields (Standard Odoo)
- `payment_type`: Determines receipt vs payment
- `partner_id`: Customer/vendor information
- `date`: Transaction date
- `amount`: Payment amount
- `currency_id`: Currency for formatting
- `company_id`: Company information
- `create_uid`, `create_date`: Audit trail
- `write_uid`, `write_date`: Audit trail

### Optional Fields (payment_account_enhanced)
- `voucher_number`: Custom voucher numbering
- `payment_reference`: Payment memo/reference
- `remarks`: Additional notes
- `approval_state`: Approval workflow state
- `reviewer_id`, `reviewer_date`: Review information
- `approver_id`, `approver_date`: Approval information
- `authorizer_id`, `authorizer_date`: Authorization information

### QR Code Fields (ingenuity_invoice_qr_code)
- `qr_code_invoice`: Primary QR code field
- `qr_image`: Fallback QR code field

### Optional Fields (Other Modules)
- `amount_total_words`: From invoice_report_for_realestate
- `check_amount_in_words`: Alternative words field
- `payment_description`: Alternative description field

## Usage

### Installation
1. Ensure `payment_account_enhanced` module is installed
2. Install or upgrade `ingenuity_invoice_qr_code` module
3. The report will be available in the Print menu of payment records

### Accessing the Report
From any payment record:
1. Go to Accounting → Payments
2. Open any payment record
3. Click Print → "Payment/Receipt Voucher (with QR)"

### Customization
The report uses inline CSS for easy customization. Key CSS classes:

- `.header-section`: Burgundy header styling
- `.qr-box`: QR code container
- `.field-label`: Field labels (burgundy color)
- `.field-value`: Field values with underline
- `.transaction-badge`: Color-coded transaction type
- `.amount-banner`: Gold amount display
- `.signature-box`: Signature sections
- `.received-section`: Received by section

## Technical Details

### Report Definition
- **ID**: `action_report_payment_voucher_qr`
- **Model**: `account.payment`
- **Template**: `ingenuity_invoice_qr_code.report_payment_voucher_qr`
- **Report Type**: qweb-pdf
- **Paper Format**: A4 (base.paperformat_euro)

### File Location
- **Template**: `ingenuity_invoice_qr_code/report/payment_voucher_qr_report.xml`
- **Manifest**: `ingenuity_invoice_qr_code/__manifest__.py`

### Dependencies
```python
'depends': [
    'web',
    'account',
    'payment_account_enhanced'
]
```

## Comparison with Standard Payment Voucher

| Feature | Standard Voucher | QR Voucher |
|---------|-----------------|------------|
| QR Code | ❌ No | ✅ Yes |
| Theme | Various | Burgundy Premium |
| Layout | Varies | Fixed Professional |
| Mobile Scanning | ❌ No | ✅ Yes |
| Verification | Manual | QR + Manual |
| Fields | Standard | Enhanced + Custom |

## Best Practices

### When to Use This Report
- ✅ When QR code verification is required
- ✅ For payment tracking and audit purposes
- ✅ When professional branding is important
- ✅ For mobile verification capability

### When to Use Standard Report
- ✅ When QR codes are not needed
- ✅ For internal simple receipts
- ✅ When custom fields are not required

## Troubleshooting

### QR Code Not Showing
1. Check if `qr_code_invoice` or `qr_image` field has value
2. Verify QR code generation is enabled in payment settings
3. Ensure ingenuity_invoice_qr_code module is properly installed

### Missing Fields
1. Verify payment_account_enhanced module is installed
2. Check field access rights in security settings
3. Ensure payment record has required data

### Layout Issues
1. Verify paper format is set to A4
2. Check browser PDF rendering settings
3. Try different PDF viewer if printing

## Future Enhancements
- [ ] Add multi-currency support enhancements
- [ ] Include payment line items breakdown
- [ ] Add bank details section
- [ ] Support for custom company logos
- [ ] Email template integration
- [ ] SMS notification with QR code link

## Support
For issues or customization requests, refer to:
- Module: ingenuity_invoice_qr_code
- Developer: Ingenuity Info
- Website: https://ingenuityinfo.in

## License
AGPL-3

---
**Last Updated**: November 3, 2025
**Version**: 17.0.1.0
