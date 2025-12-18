# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SalesInvoicingDashboard(models.Model):
    _name = 'osus.sales.invoicing.dashboard'
    _rec_name = 'name'
    _description = 'Sales & Invoicing Dashboard'

    # Simple label so the record always has a display name in forms/kanban
    name = fields.Char(default='Sales & Invoicing Dashboard', readonly=True)

    # Filters
    sales_order_type_id = fields.Many2one(
        'sale.order.type', string='Sales Order Type'
    )
    booking_date_from = fields.Date(string='Booking Date From')
    booking_date_to = fields.Date(string='Booking Date To')
    invoice_status_filter = fields.Selection(
        [
            ('all', 'All'),
            ('no', 'Not Invoiced'),
            ('to invoice', 'Pending to Invoice'),
            ('invoiced', 'Fully Invoiced'),
        ],
        string='Invoice Status',
        default='all',
    )
    payment_status_filter = fields.Selection(
        [
            ('all', 'All'),
            ('not_paid', 'Not Paid'),
            ('partial', 'Partially Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
        ],
        string='Payment Status',
        default='all',
    )

    posted_invoice_count = fields.Integer(
        string='Posted Invoices', compute='_compute_metrics', store=False
    )
    pending_to_invoice_order_count = fields.Integer(
        string='Orders To Invoice', compute='_compute_metrics', store=False
    )
    unpaid_invoice_count = fields.Integer(
        string='Unpaid Invoices', compute='_compute_metrics', store=False
    )

    chart_sales_by_type = fields.Json(
        string='Chart Sales by Type', compute='_compute_chart_sales_by_type'
    )
    chart_booking_trend = fields.Json(
        string='Chart Booking Trend', compute='_compute_chart_booking_trend'
    )
    chart_payment_state = fields.Json(
        string='Chart Payment State', compute='_compute_chart_payment_state'
    )

    def _get_order_domain(self):
        domain = [('state', 'in', ['sale', 'done'])]
        if self.sales_order_type_id:
            domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.booking_date_from:
            domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            domain.append(('booking_date', '<=', self.booking_date_to))
        return domain

    def _get_invoice_domain(self, include_payment_filter=True, unpaid_only=False):
        domain = [
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        order_ids = []
        order_domain = self._get_order_domain()
        if order_domain:
            orders = self.env['sale.order'].search(order_domain)
            order_ids = orders.ids
            if order_ids:
                domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
        if unpaid_only:
            domain.append(('payment_state', 'in', ['not_paid', 'partial', 'in_payment']))
        if include_payment_filter and self.payment_status_filter and self.payment_status_filter != 'all':
            domain.append(('payment_state', '=', self.payment_status_filter))
        return domain

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
    )
    def _compute_metrics(self):
        for rec in self:
            order_domain = rec._get_order_domain()

            matching_orders = self.env['sale.order'].search(order_domain)
            order_ids = matching_orders.ids

            # Posted invoices count (filtered by selected orders and payment status if provided)
            posted_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ]
            if order_ids:
                posted_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            if rec.payment_status_filter and rec.payment_status_filter != 'all':
                posted_domain.append(('payment_state', '=', rec.payment_status_filter))
            rec.posted_invoice_count = self.env['account.move'].search_count(posted_domain)

            # Orders to invoice count (respecting filters, but always focusing 'to invoice')
            pending_domain = list(order_domain)
            # If invoice_status_filter is 'all', focus on 'to invoice'
            if rec.invoice_status_filter == 'all':
                # Replace any existing invoice_status in order_domain
                pending_domain = [d for d in pending_domain if not (isinstance(d, tuple) and d[0] == 'invoice_status')]
                pending_domain.append(('invoice_status', '=', 'to invoice'))
            rec.pending_to_invoice_order_count = self.env['sale.order'].search_count(pending_domain)

            # Unpaid invoices count (filtered by orders and payment status)
            unpaid_domain = [
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('payment_state', 'in', ['not_paid', 'partial', 'in_payment']),
            ]
            if order_ids:
                unpaid_domain.append(('line_ids.sale_line_ids.order_id', 'in', order_ids))
            if rec.payment_status_filter and rec.payment_status_filter != 'all':
                # Override the payment_state list with the selected filter
                unpaid_domain = [d for d in unpaid_domain if not (isinstance(d, tuple) and d[0] == 'payment_state')]
                unpaid_domain.append(('payment_state', '=', rec.payment_status_filter))
            rec.unpaid_invoice_count = self.env['account.move'].search_count(unpaid_domain)

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
    )
    def _compute_chart_sales_by_type(self):
        palette = ['#0060df', '#00a651', '#f0ad4e', '#d9534f', '#5bc0de', '#7b7b7b']
        for rec in self:
            domain = rec._get_order_domain()
            groups = self.env['sale.order'].read_group(
                domain, ['amount_total'], ['sale_order_type_id']
            )
            labels = []
            data = []
            for idx, group in enumerate(groups):
                label = group['sale_order_type_id'][1] if group.get('sale_order_type_id') else 'Unspecified'
                labels.append(label)
                data.append(group.get('amount_total', 0.0))
            colors = [palette[i % len(palette)] for i in range(len(data))]
            rec.chart_sales_by_type = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales by Type',
                        'data': data,
                        'backgroundColor': colors,
                    }
                ],
            }

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
    )
    def _compute_chart_booking_trend(self):
        palette = ['#0060df']
        for rec in self:
            labels = []
            data = []
            try:
                    domain = rec._get_order_domain()
                    groups = self.env['sale.order'].read_group(
                        domain,
                        ['amount_total'],
                        ['booking_date:month'],
                        orderby='booking_date:month',
                        lazy=False
                    )
                    for group in groups:
                        # Safe dict access - don't trigger field machinery
                        month_label = str(group.get('booking_date:month') or 'Unspecified')
                        labels.append(month_label)
                        data.append(float(group.get('amount_total', 0) or 0))
            except Exception:
                # If any error occurs, show empty chart
                labels = ['No data available']
                data = [0]

            rec.chart_booking_trend = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Booking Amount',
                        'data': data,
                        'backgroundColor': palette * max(1, len(data)),
                        'borderColor': palette * max(1, len(data)),
                        'fill': False,
                        'tension': 0.25,
                    }
                ],
            }

    @api.depends(
        'sales_order_type_id',
        'booking_date_from',
        'booking_date_to',
        'invoice_status_filter',
        'payment_status_filter',
    )
    def _compute_chart_payment_state(self):
        palette = ['#5bc0de', '#f0ad4e', '#d9534f', '#00a651']
        for rec in self:
            domain = rec._get_invoice_domain(include_payment_filter=False, unpaid_only=False)
            groups = self.env['account.move'].read_group(
                domain,
                ['amount_total', 'payment_state'],
                ['payment_state'],
            )
            labels = []
            data = []
            for group in groups:
                label = group.get('payment_state') or 'unknown'
                labels.append(label)
                data.append(group.get('amount_total', 0.0))
            colors = [palette[i % len(palette)] for i in range(len(data))]
            rec.chart_payment_state = {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Invoices by Payment State',
                        'data': data,
                        'backgroundColor': colors,
                    }
                ],
            }

    def action_open_posted_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = [
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ]
        order_domain = [('state', 'in', ['sale', 'done'])]
        if self.sales_order_type_id:
            order_domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.invoice_status_filter and self.invoice_status_filter != 'all':
            order_domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.booking_date_from:
            order_domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            order_domain.append(('booking_date', '<=', self.booking_date_to))
        orders = self.env['sale.order'].search(order_domain)
        if orders:
            domain.append(('line_ids.sale_line_ids.order_id', 'in', orders.ids))
        if self.payment_status_filter and self.payment_status_filter != 'all':
            domain.append(('payment_state', '=', self.payment_status_filter))
        action['domain'] = domain
        action['context'] = {'search_default_posted': 1}
        return action

    def action_open_pending_orders(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = [('state', 'in', ['sale', 'done'])]
        if self.invoice_status_filter == 'all':
            domain.append(('invoice_status', '=', 'to invoice'))
        else:
            domain.append(('invoice_status', '=', self.invoice_status_filter))
        if self.sales_order_type_id:
            domain.append(('sale_order_type_id', '=', self.sales_order_type_id.id))
        if self.booking_date_from:
            domain.append(('booking_date', '>=', self.booking_date_from))
        if self.booking_date_to:
            domain.append(('booking_date', '<=', self.booking_date_to))
        action['domain'] = domain
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
        }
        return action

    def action_open_unpaid_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = self._get_invoice_domain(include_payment_filter=True, unpaid_only=True)
        action['domain'] = domain
        action['context'] = {'search_default_unpaid': 1}
        return action

    def action_open_sales_graph(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot,form'
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'sale_order_type_id',
        }
        return action

    def action_open_invoice_payment_graph(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        domain = self._get_invoice_domain(include_payment_filter=True)
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot'
        action['context'] = {
            'search_default_posted': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'payment_state',
        }
        return action

    def action_open_booking_trend_graph(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        domain = self._get_order_domain()
        action['domain'] = domain
        action['view_mode'] = 'graph,tree,pivot,form'
        action['context'] = {
            'search_default_sale': 1,
            'search_default_done': 1,
            'graph_measure': 'amount_total',
            'graph_groupby': 'booking_date:month',
        }
        return action
