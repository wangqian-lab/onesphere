# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    active = fields.Boolean("Active", default=True)

    workcenter_id = fields.Many2one(
        "mrp.workcenter",
        string="Work Center",
        required=False,
        check_company=True,
        ondelete="set null",
    )
