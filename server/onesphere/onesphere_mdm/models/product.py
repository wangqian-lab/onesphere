# -*- coding: utf-8 -*-

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _check_company_auto = True

    @api.model
    def default_get(self, fields_list):
        context = self.env.context
        res = super(ProductTemplate, self).default_get(fields_list)
        if "route_ids" not in fields_list:
            return res
        if context.get("context_route_ids"):
            item = self.env.ref(
                "mrp.route_warehouse0_manufacture", raise_if_not_found=False
            )
            res.update({"route_ids": [[6, 0, item.ids]]})
        return res
