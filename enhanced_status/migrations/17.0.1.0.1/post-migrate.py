# -*- coding: utf-8 -*-
"""
Migration script to fix qty_invoiced rounding issues in existing sale orders.
This script recalculates qty_invoiced from actual invoice lines to ensure exact precision.

Run this script after updating the enhanced_status module.
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Recalculate qty_invoiced for all sale order lines to fix rounding issues.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info("Starting migration: Fixing qty_invoiced rounding issues...")
    
    # Get all sale order lines that have invoices
    sale_lines = env['sale.order.line'].search([
        ('invoice_lines', '!=', False),
        ('state', 'in', ['sale', 'done'])
    ])
    
    _logger.info(f"Found {len(sale_lines)} sale order lines with invoices to process")
    
    updated_count = 0
    fixed_orders = set()
    
    for line in sale_lines:
        # Get the current qty_invoiced (may be rounded)
        old_qty_invoiced = line.qty_invoiced
        
        # Recalculate from actual invoice lines
        qty_invoiced = 0.0
        for invoice_line in line.invoice_lines:
            if invoice_line.move_id.state != 'cancel':
                if invoice_line.move_id.move_type == 'out_invoice':
                    qty_invoiced += invoice_line.quantity
                elif invoice_line.move_id.move_type == 'out_refund':
                    qty_invoiced -= invoice_line.quantity
        
        # Update if there's a difference (due to rounding)
        if abs(qty_invoiced - old_qty_invoiced) > 0.001:  # Allow tiny floating point differences
            _logger.info(
                f"Fixing line {line.id} - Order: {line.order_id.name}, "
                f"Product: {line.product_id.name}, "
                f"Old qty_invoiced: {old_qty_invoiced}, "
                f"New qty_invoiced: {qty_invoiced}"
            )
            
            # Write the corrected value
            cr.execute(
                """
                UPDATE sale_order_line 
                SET qty_invoiced = %s 
                WHERE id = %s
                """,
                (qty_invoiced, line.id)
            )
            
            updated_count += 1
            fixed_orders.add(line.order_id.id)
    
    # Commit the changes
    cr.commit()
    
    _logger.info(f"Migration completed: Updated {updated_count} sale order lines")
    _logger.info(f"Fixed invoice status for {len(fixed_orders)} sale orders")
    
    # Recompute invoice_status for affected orders
    if fixed_orders:
        _logger.info("Recomputing invoice_status for affected orders...")
        orders = env['sale.order'].browse(list(fixed_orders))
        for order in orders:
            order._compute_invoice_status()
        cr.commit()
        _logger.info("Invoice status recomputation completed")
    
    _logger.info("Migration finished successfully!")
