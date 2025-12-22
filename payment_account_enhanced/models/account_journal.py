# models/account_journal.py
from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    enable_payment_verification = fields.Boolean(
        string="Enable Payment Verification",
        default=True,
        help="Enable QR verification for payments in this journal"
    )
    
    payment_approval_required = fields.Boolean(
        string='Require Payment Approval',
        default=True,
        help="Require approval workflow for payments in this journal"
    )

    def name_get(self):
        """
        Override name_get to properly display journal name
        consistent across all views, avoiding archive indicators.
        """
        result = []
        for record in self:
            # Display journal name directly without archive prefix
            name = record.name or ''
            result.append((record.id, name))
        
        return result
