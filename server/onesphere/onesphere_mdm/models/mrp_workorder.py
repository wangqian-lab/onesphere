# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    workcenter_id = fields.Many2one(
        "mrp.workcenter", required=False, ondelete="set null"
    )
