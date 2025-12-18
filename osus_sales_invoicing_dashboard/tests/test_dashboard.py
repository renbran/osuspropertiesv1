# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from datetime import date


class TestSalesInvoicingDashboard(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Dashboard = self.env['osus.sales.invoicing.dashboard']
        self.dashboard = self.Dashboard.create({})
        self.partner = self.env['res.partner'].create({'name': 'Test Customer'})

    def test_dashboard_singleton(self):
        # create should reuse existing record
        other = self.Dashboard.create({})
        self.assertEqual(self.dashboard.id, other.id)
        self.assertEqual(self.dashboard.name, 'Sales & Invoicing Dashboard')

    def test_date_filter_defaults(self):
        today = date.today()
        first_of_month = today.replace(day=1)
        self.assertEqual(self.dashboard.booking_date_from, first_of_month)
        self.assertEqual(self.dashboard.booking_date_to, today)

    def test_metrics_computation(self):
        # minimal order then confirm
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'booking_date': date.today(),
        })
        order.action_confirm()
        # recompute
        self.dashboard.invalidate_cache()
        self.dashboard._compute_metrics()
        self.assertTrue(self.dashboard.total_booked_sales >= 0)

    def test_export_actions(self):
        act = self.dashboard.action_export_order_types_csv()
        self.assertEqual(act['type'], 'ir.actions.act_url')
        self.assertIn('/osus_dashboard/export/order_types', act['url'])
