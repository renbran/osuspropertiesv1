#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone script to fix qty_invoiced rounding issues in sale orders.

Run this script using Odoo shell:
    docker-compose exec odoo odoo shell -d your_database_name < fix_qty_invoiced.py

Or from within Odoo shell:
    exec(open('fix_qty_invoiced.py').read())
"""

import logging

_logger = logging.getLogger(__name__)

def fix_qty_invoiced_rounding():
    """
    Fix qty_invoiced rounding issues in existing sale orders.
    This ensures that sale orders are correctly marked as fully invoiced.
    """
    print("=" * 80)
    print("FIXING QTY_INVOICED ROUNDING ISSUES IN SALE ORDERS")
    print("=" * 80)
    
    # Get all sale order lines that have invoices
    SaleOrderLine = env['sale.order.line']
    
    # Search for lines with invoices in sale or done state
    domain = [
        ('invoice_lines', '!=', False),
        ('state', 'in', ['sale', 'done'])
    ]
    
    sale_lines = SaleOrderLine.search(domain)
    
    print(f"\nFound {len(sale_lines)} sale order lines with invoices to process\n")
    
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
        # Allow tiny floating point differences (0.001)
        if abs(qty_invoiced - old_qty_invoiced) > 0.001:
            print(f"Fixing Sale Order: {line.order_id.name}")
            print(f"  Line: {line.product_id.name}")
            print(f"  Ordered Qty: {line.product_uom_qty}")
            print(f"  Old Invoiced: {old_qty_invoiced}")
            print(f"  New Invoiced: {qty_invoiced}")
            print(f"  Difference: {abs(qty_invoiced - old_qty_invoiced)}")
            print()
            
            # Update the qty_invoiced directly in database
            env.cr.execute(
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
    env.cr.commit()
    
    print("\n" + "=" * 80)
    print(f"MIGRATION COMPLETED")
    print(f"  Updated {updated_count} sale order lines")
    print(f"  Fixed invoice status for {len(fixed_orders)} sale orders")
    print("=" * 80)
    
    # Recompute invoice_status for affected orders
    if fixed_orders:
        print("\nRecomputing invoice_status for affected orders...")
        SaleOrder = env['sale.order']
        orders = SaleOrder.browse(list(fixed_orders))
        
        for order in orders:
            # Trigger recomputation of invoice_status
            order._compute_invoice_status()
            print(f"  Updated: {order.name} - Invoice Status: {order.invoice_status}")
        
        env.cr.commit()
        print("\nInvoice status recomputation completed!")
    
    print("\n" + "=" * 80)
    print("ALL DONE! Sale orders now have accurate invoice tracking.")
    print("=" * 80)

# Run the fix
if __name__ == '__main__':
    fix_qty_invoiced_rounding()
else:
    # When loaded in Odoo shell, run automatically
    fix_qty_invoiced_rounding()
