# models/res_partner.py
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    payment_count = fields.Integer(
        string="Payment Count",
        compute='_compute_payment_count',
        help="Total number of payments with this partner"
    )
    
    @api.depends('name')
    def _compute_payment_count(self):
        for partner in self:
            partner.payment_count = self.env['account.payment'].search_count([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['posted', 'sent', 'reconciled'])
            ])
    
    def action_view_partner_payments(self):
        """View payments for this partner"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments for %s') % self.display_name,
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
    
    def name_get(self):
        """
        Override name_get to display clean partner names consistently.
        Remove [Archived] prefix to ensure form and list views show the same name.
        This fixes the confusion where archived partners show different names in different views.
        """
        result = []
        for partner in self:
            # Use partner.name directly to get the actual name without any prefix
            # Build the display name similar to standard Odoo but without archive indicator
            name = partner.name or ''
            
            # If partner is a company, just use the name
            # If it's a contact with a parent company, show "Contact Name (Company Name)"
            if partner.parent_id and not partner.is_company:
                name = f"{name} ({partner.parent_id.name})"
            
            result.append((partner.id, name))
        return result