from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Unified deal stage selection (shared with sale.order)
    DEAL_STAGE_SELECTION = [
        ('new', 'New'),
        ('attempt', 'Attempt'),
        ('contacted', 'Contacted'),
        ('option_sent', 'Option Sent'),
        ('hot', 'Hot'),
        ('idle', 'Idle'),
        ('junk', 'Junk (Completely Lost)'),
        ('unsuccessful', 'Unsuccessful (Follow up after 60 days)'),
        ('customer', 'Customer (Won)'),
    ]

    deal_stage = fields.Selection(
        DEAL_STAGE_SELECTION,
        string='Deal Stage',
        default='new',
        tracking=True,
        help='Current stage of the deal for tracking pipeline progress. '
             'Synchronized with linked Sale Orders automatically.'
    )
    
    # Computed field to show when deal stage was last updated
    deal_stage_updated = fields.Datetime(
        string='Deal Stage Last Updated',
        readonly=True,
        help='Timestamp of last deal stage change'
    )
    
    # Count of linked sale orders for this opportunity
    sale_order_count = fields.Integer(
        string='Quotations Count',
        compute='_compute_sale_order_count',
        help='Number of quotations linked to this opportunity'
    )

    def _compute_sale_order_count(self):
        """
        Count sale orders linked to this opportunity via opportunity_id field
        """
        for lead in self:
            # Search for sale orders where opportunity_id points to this lead
            count = self.env['sale.order'].search_count([
                ('opportunity_id', '=', lead.id)
            ])
            lead.sale_order_count = count

    def write(self, vals):
        """
        Track when deal_stage is updated and sync to linked sale orders
        """
        if 'deal_stage' in vals:
            vals['deal_stage_updated'] = fields.Datetime.now()
            
            # Sync deal stage to all linked sale orders if configured
            if self.env.context.get('sync_deal_stage_to_sale', True):
                for lead in self:
                    # Find all sale orders linked via opportunity_id
                    linked_orders = self.env['sale.order'].search([
                        ('opportunity_id', '=', lead.id)
                    ])
                    
                    if linked_orders:
                        # Update without triggering infinite loop
                        linked_orders.with_context(sync_deal_stage_to_crm=False).write({
                            'deal_stage': vals['deal_stage']
                        })
        
        return super(CrmLead, self).write(vals)

    @api.model
    def create(self, vals):
        """
        Set deal_stage_updated timestamp on creation if deal_stage is provided
        """
        if 'deal_stage' in vals:
            vals['deal_stage_updated'] = fields.Datetime.now()
        
        return super(CrmLead, self).create(vals)

    def action_view_linked_sale_orders(self):
        """
        Smart button action to view sale orders linked to this opportunity
        """
        self.ensure_one()
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['domain'] = [('opportunity_id', '=', self.id)]
        action['context'] = {
            'default_opportunity_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_deal_stage': self.deal_stage,
        }
        return action
