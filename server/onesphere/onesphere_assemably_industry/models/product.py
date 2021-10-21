# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from uuid import uuid4


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    onesphere_product_type = fields.Selection([('screw', 'Screw'), ('bolt', 'Bolt'), ('vehicle', 'Vehicle')],
                                              string='产品类型')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    onesphere_product_type = fields.Selection(related='product_tmpl_id.onesphere_product_type', store=True)
