# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    @api.model
    def default_select_ids(self):
        item = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        if item:
            return item.ids
        return []
    route_ids = fields.Many2many(default=lambda self: self.default_select_ids())
