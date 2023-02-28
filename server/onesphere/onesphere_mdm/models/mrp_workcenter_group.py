# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class MrpWorkcenterGroup(models.Model):
    _log_access = False
    _name = "mrp.workcenter.group"
    _description = "Work Center Group"
    _order = "code"

    code = fields.Char("Reference", copy=False, required=True)
    name = fields.Char("Work Center Group")
    onesphere_workcenter_ids = fields.Many2many(
        "mrp.workcenter",
        "mrp_workcenter_group_rel",
        "group_id",
        "workcenter_id",
        string="Work Centers",
        copy=False,
        check_company=True,
    )

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    active = fields.Boolean(
        "Active",
        default=True,
        help="If the active field is set to False, it will allow you to hide the bills of material without removing it.",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Only one code per Work Center Group is allowed")
    ]

    def name_get(self):
        res = []
        for center_group in self:
            res.append((center_group.id, f"[{center_group.code}] {center_group.name}"))
        return res
