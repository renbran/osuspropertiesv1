from odoo import fields, api, models


class BookingWizard(models.TransientModel):
    _name = 'booking.wizard'
    _description = 'Create Booking While Property on Sale'

    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('user_type','=','customer')]")
    property_id = fields.Many2one('property.details', string='Property')
    price = fields.Monetary(related="property_id.price")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    book_price = fields.Monetary(string="Advance")
    ask_price = fields.Monetary(string="Customer Price")
    sale_price = fields.Monetary(related="property_id.sale_price", string="Sale Price")
    is_any_broker = fields.Boolean(string='Any Broker?')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[('user_type', '=', 'broker')])
    commission_type = fields.Selection([('f', 'Fix'), ('p', 'Percentage')], string="Commission Type")
    broker_commission = fields.Monetary(string='Commission')
    broker_commission_percentage = fields.Float(string='Percentage')
    commission_from = fields.Selection([('customer', 'Customer'),
                                        ('landlord', 'Landlord',)],
                                       default='customer', string="Commission From")
    from_inquiry = fields.Boolean('From Enquiry')
    note = fields.Text(string="Note", translate=True)
    lead_id = fields.Many2one('crm.lead', string="Enquiry", domain="[('property_id','=',property_id)]")

    # Maintenance and utility Service
    is_any_maintenance = fields.Boolean(related="property_id.is_maintenance_service")
    total_maintenance = fields.Monetary(related="property_id.total_maintenance")
    is_utility_service = fields.Boolean(related="property_id.is_extra_service")
    total_service = fields.Monetary(related="property_id.extra_service_cost")

    # Booking Item
    booking_item_id = fields.Many2one('product.product', string="Booking Item")
    broker_item_id = fields.Many2one('product.product', string="Broker Item")

    # Deprecated
    inquiry_id = fields.Many2one('sale.inquiry', string="Enquiry ")

    @api.model
    def default_get(self, fields):
        res = super(BookingWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        property_id = self.env['property.details'].browse(active_id)
        
        # Get default products from config parameters with fallback to XML refs
        default_broker_item = self.env['ir.config_parameter'].sudo().get_param(
            'rental_management.account_broker_item_id')
        default_deposit_item = self.env['ir.config_parameter'].sudo().get_param(
            'rental_management.account_deposit_item_id')
        
        res['property_id'] = property_id.id
        res['ask_price'] = property_id.price
        
        # Set booking item with existence check
        if default_deposit_item:
            try:
                deposit_product = self.env['product.product'].browse(int(default_deposit_item))
                if deposit_product.exists():
                    res['booking_item_id'] = deposit_product.id
                else:
                    # Fallback to XML ref or create if needed
                    res['booking_item_id'] = self._get_or_create_deposit_product().id
            except (ValueError, TypeError):
                res['booking_item_id'] = self._get_or_create_deposit_product().id
        else:
            res['booking_item_id'] = self._get_or_create_deposit_product().id
        
        # Set broker item with existence check
        if default_broker_item:
            try:
                broker_product = self.env['product.product'].browse(int(default_broker_item))
                if broker_product.exists():
                    res['broker_item_id'] = broker_product.id
                else:
                    # Fallback to XML ref or create if needed
                    res['broker_item_id'] = self._get_or_create_broker_product().id
            except (ValueError, TypeError):
                res['broker_item_id'] = self._get_or_create_broker_product().id
        else:
            res['broker_item_id'] = self._get_or_create_broker_product().id
        
        return res

    def _get_or_create_deposit_product(self):
        """Get or create property deposit product"""
        try:
            # Try to get from XML reference
            product = self.env.ref('rental_management.property_product_2', raise_if_not_found=False)
            if product and product.exists():
                return product
        except:
            pass
        
        # Search for existing deposit product
        product = self.env['product.product'].search([
            ('name', '=', 'Property Deposit'),
            ('detailed_type', '=', 'service')
        ], limit=1)
        
        if product:
            return product
        
        # Create new deposit product if not found
        category = self.env.ref('rental_management.product_category_property', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([('name', '=', 'Property')], limit=1)
            if not category:
                category = self.env['product.category'].create({
                    'name': 'Property',
                    'parent_id': self.env.ref('product.product_category_all').id
                })
        
        product = self.env['product.product'].create({
            'name': 'Property Deposit',
            'detailed_type': 'service',
            'categ_id': category.id,
            'list_price': 0.0,
        })
        
        # Update config parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'rental_management.account_deposit_item_id', product.id)
        
        return product

    def _get_or_create_broker_product(self):
        """Get or create broker commission product"""
        try:
            # Try to get from XML reference
            product = self.env.ref('rental_management.property_product_3', raise_if_not_found=False)
            if product and product.exists():
                return product
        except:
            pass
        
        # Search for existing broker commission product
        product = self.env['product.product'].search([
            ('name', '=', 'Broker Commission'),
            ('detailed_type', '=', 'service')
        ], limit=1)
        
        if product:
            return product
        
        # Create new broker commission product if not found
        category = self.env.ref('rental_management.product_category_property', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([('name', '=', 'Property')], limit=1)
            if not category:
                category = self.env['product.category'].create({
                    'name': 'Property',
                    'parent_id': self.env.ref('product.product_category_all').id
                })
        
        product = self.env['product.product'].create({
            'name': 'Broker Commission',
            'detailed_type': 'service',
            'categ_id': category.id,
            'list_price': 0.0,
        })
        
        # Update config parameter
        self.env['ir.config_parameter'].sudo().set_param(
            'rental_management.account_broker_item_id', product.id)
        
        return product

    def create_booking_action(self):
        """Create booking with product validation"""
        invoice_post_type = self.env['ir.config_parameter'].sudo().get_param('rental_management.invoice_post_type')
        self.customer_id.user_type = "customer"
        
        # Ensure booking and broker products exist and are valid
        if not self.booking_item_id or not self.booking_item_id.exists():
            self.booking_item_id = self._get_or_create_deposit_product()
        
        if self.is_any_broker and (not self.broker_item_id or not self.broker_item_id.exists()):
            self.broker_item_id = self._get_or_create_broker_product()
        
        data = {
            'customer_id': self.customer_id.id,
            'property_id': self.property_id.id,
            'book_price': self.book_price * (-1),
            'ask_price': self.ask_price,
            'is_any_broker': self.is_any_broker,
            'broker_id': self.broker_id.id,
            'commission_type': self.commission_type,
            'broker_commission': self.broker_commission,
            'broker_commission_percentage': self.broker_commission_percentage,
            'stage': 'booked',
            'commission_from': self.commission_from,
            'booking_item_id': self.booking_item_id.id,
            'broker_item_id': self.broker_item_id.id,
        }
        booking_id = self.env['property.vendor'].create(data)
        self.property_id.sold_booking_id = booking_id.id
        mail_template = self.env.ref(
            'rental_management.property_book_mail_template', raise_if_not_found=False)
        if mail_template:
            mail_template.send_mail(booking_id.id, force_send=True)
        if not booking_id.book_price == 0:
            record = {
                'product_id': self.booking_item_id.id,
                'name': 'Booked Amount of   ' + booking_id.property_id.name,
                'quantity': 1,
                'price_unit': self.book_price
            }
            invoice_lines = [(0, 0, record)]
            data = {
                'partner_id': booking_id.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.date.today(),
                'invoice_line_ids': invoice_lines
            }
            book_invoice_id = self.env['account.move'].sudo().create(data)
            book_invoice_id.sold_id = booking_id.id
            if invoice_post_type == 'automatically':
                book_invoice_id.action_post()
            booking_id.book_invoice_id = book_invoice_id.id
            booking_id.book_invoice_state = True
        booking_id.property_id.stage = 'booked'
        booking_id.stage = 'booked'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Booking',
            'res_model': 'property.vendor',
            'res_id': booking_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }

    @api.onchange('from_inquiry')
    def _onchange_property_sale_inquiry(self):
        inquiry_ids = self.env['sale.inquiry'].search(
            [('property_id', '=', self.property_id.id)]).mapped('id')
        for rec in self:
            if not rec.from_inquiry:
                return
            return {'domain': {'inquiry_id': [('id', 'in', inquiry_ids)]}}

    @api.onchange('lead_id')
    def _onchange_ask_price(self):
        for rec in self:
            if not rec.from_inquiry and not rec.lead_id:
                return
            rec.ask_price = rec.lead_id.ask_price
            rec.note = rec.lead_id.description
            rec.customer_id = rec.lead_id.partner_id.id
