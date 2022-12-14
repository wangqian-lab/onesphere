# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    # # 目前只能想到这种方法，action中env ref，obj等字段不支持
    # @api.model
    # def default_select_ids(self):
    #     item = self.env['ir.model.data'].xmlid_to_res_id('mrp.route_warehouse0_manufacture')
    #     return [[6, 0, [item]]]
    #
    # route_ids = fields.Many2many(default=default_select_ids)

    @api.model
    def default_get(self, fields_list):
        context = self.env.context
        res = super(ProductTemplate, self).default_get(fields_list)
        if 'route_ids' not in fields_list:
            return res
        if context.get('context_route_ids'):
            item = self.env['ir.model.data'].xmlid_to_res_id('mrp.route_warehouse0_manufacture')
            res.update({
                'route_ids': [[6, 0, [item]]]
            })
        return res
