from odoo import models, fields, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Renamed from lead_id to avoid confusion with rental_management module
    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Opportunity/Lead',
        tracking=True,
        help='Link this Sale Order to a CRM Opportunity or Lead for tracking purposes'
    )

    # Use standard Odoo UTM fields (compatible with existing integrations)
    # These are related fields that pull from the linked opportunity
    # or can be set directly if no opportunity is linked
    source_id = fields.Many2one(
        'utm.source',
        string='Lead Source',
        tracking=True,
        help='Marketing source (e.g., Website, Referral, Social Media). '
             'Automatically populated from linked Opportunity or can be set manually.'
    )
    
    campaign_id = fields.Many2one(
        'utm.campaign',
        string='Campaign',
        tracking=True,
        help='Marketing campaign that generated this lead. '
             'Automatically populated from linked Opportunity or can be set manually.'
    )
    
    medium_id = fields.Many2one(
        'utm.medium',
        string='Medium',
        tracking=True,
        help='Marketing medium (e.g., Email, CPC, Social). '
             'Automatically populated from linked Opportunity or can be set manually.'
    )

    # Unified deal stage selection (shared with crm.lead)
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
        help='Current stage of the deal for tracking sales pipeline progress'
    )
    
    # Computed field to show when deal stage was last updated
    deal_stage_updated = fields.Datetime(
        string='Deal Stage Last Updated',
        readonly=True,
        help='Timestamp of last deal stage change'
    )

    @api.onchange('opportunity_id')
    def _onchange_opportunity_id(self):
        """
        When an opportunity is linked, automatically populate UTM fields and deal stage
        from the opportunity if they're not already set.
        """
        if self.opportunity_id:
            # Only populate if fields are empty to avoid overwriting manual changes
            if not self.source_id and self.opportunity_id.source_id:
                self.source_id = self.opportunity_id.source_id
            
            if not self.campaign_id and self.opportunity_id.campaign_id:
                self.campaign_id = self.opportunity_id.campaign_id
            
            if not self.medium_id and self.opportunity_id.medium_id:
                self.medium_id = self.opportunity_id.medium_id
            
            # Sync deal stage from opportunity if it has one
            if hasattr(self.opportunity_id, 'deal_stage') and self.opportunity_id.deal_stage:
                self.deal_stage = self.opportunity_id.deal_stage

    def write(self, vals):
        """
        Track when deal_stage is updated and optionally sync back to opportunity
        """
        if 'deal_stage' in vals:
            vals['deal_stage_updated'] = fields.Datetime.now()
            
            # Sync deal stage back to linked opportunity if configured
            if self.env.context.get('sync_deal_stage_to_crm', True):
                for order in self:
                    if order.opportunity_id and hasattr(order.opportunity_id, 'deal_stage'):
                        # Update opportunity's deal stage (without triggering infinite loop)
                        order.opportunity_id.with_context(sync_deal_stage_to_sale=False).write({
                            'deal_stage': vals['deal_stage']
                        })
        
        return super(SaleOrder, self).write(vals)

    @api.model
    def create(self, vals):
        """
        Set deal_stage_updated timestamp on creation if deal_stage is provided
        """
        if 'deal_stage' in vals:
            vals['deal_stage_updated'] = fields.Datetime.now()
        
        return super(SaleOrder, self).create(vals)
