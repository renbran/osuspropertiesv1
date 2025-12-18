# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_progress = fields.Selection(
        selection=[
            ('none', 'Not Invoiced'),
            ('partial', 'Pending to Invoice'),
            ('full', 'Fully Invoiced'),
        ],
        string='Invoicing Progress',
        compute='_compute_invoice_progress',
        store=True,
    )
    
    # Hidden fields for pivot analysis
    invoiced_amount = fields.Monetary(
        string='Invoiced Amount',
        compute='_compute_invoice_amounts',
        store=True,
        currency_field='currency_id',
        help='Total amount invoiced (visible in pivot/graph views)'
    )
    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_invoice_amounts',
        store=True,
        currency_field='currency_id',
        help='Remaining unpaid amount (visible in pivot/graph views)'
    )
    collected_amount = fields.Monetary(
        string='Collected Amount',
        compute='_compute_invoice_amounts',
        store=True,
        currency_field='currency_id',
        help='Amount already collected (visible in pivot/graph views)'
    )

    @api.depends('invoice_status')
    def _compute_invoice_progress(self):
        """Simple classification badge - no amounts shown"""
        for order in self:
            status = order.invoice_status
            if status == 'invoiced':
                order.invoice_progress = 'full'
            elif status == 'to invoice':
                order.invoice_progress = 'partial'
            else:
                order.invoice_progress = 'none'

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_ids.amount_total', 
                 'invoice_ids.amount_residual', 'invoice_ids.payment_state')
    def _compute_invoice_amounts(self):
        """Store amounts for pivot/graph analysis - hidden from form/tree"""
        for order in self:
            # Get only posted customer invoices
            invoices = order.invoice_ids.filtered(
                lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted'
            )
            invoiced = sum(invoices.mapped('amount_total'))
            outstanding = sum(invoices.mapped('amount_residual'))
            collected = max(invoiced - outstanding, 0.0)
            
            order.invoiced_amount = invoiced
            order.outstanding_amount = outstanding
            order.collected_amount = collected
