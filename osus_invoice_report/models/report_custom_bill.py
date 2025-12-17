from odoo import models


class ReportCustomBill(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_bills'
    _description = 'OSUS Custom Bill Report'

    def _get_report_values(self, docids, data=None):
        """Get report values with smart helper logic"""
        # Filter to only get active (non-cancelled) account moves
        docs = self.env['account.move'].browse(docids).filtered(lambda m: m.state != 'cancel')
        smart_helper = self.env['report.smart.helper']

        return {
            'docs': docs,
            'smart_helper': smart_helper,
            'detect_document_type': smart_helper.detect_document_type,
            'get_document_title': smart_helper.get_document_title,
            'get_header_color': smart_helper.get_header_color,
            'get_accent_color': smart_helper.get_accent_color,
            'format_amount': smart_helper.format_amount,
            'format_currency': smart_helper.format_currency,
            'get_payment_instructions': smart_helper.get_payment_instructions,
            'should_show_payment_instructions': smart_helper.should_show_payment_instructions,
            'should_show_notes': smart_helper.should_show_notes,
            'should_show_draft_banner': smart_helper.should_show_draft_banner,
            'should_show_paid_stamp': smart_helper.should_show_paid_stamp,
            'get_tax_summary': smart_helper.get_tax_summary,
            'should_show_tax_breakdown': smart_helper.should_show_tax_breakdown,
            'get_currency_symbol': smart_helper.get_currency_symbol,
            'format_date_uk': smart_helper.format_date_uk,
        }
