# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MaintenanceEquipment(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True
    type = fields.Selection(default='product')
    tracking = fields.Selection(default='serial')

    @api.model
    def get_all_select_ids(self):
        select_ids = self.env['stock.location.route'].search([('product_selectable', '=', True)])
        vals = []
        for item in select_ids.ids:
            vals.append([6, 0, [item]])
        return vals

    route_ids = fields.Many2many(default=get_all_select_ids)
