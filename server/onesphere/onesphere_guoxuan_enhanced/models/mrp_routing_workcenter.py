# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    def _pack_operation_val(self, bom_id, operation_id):
        operation_val = super(MrpRoutingWorkcenter, self)._pack_operation_val(bom_id, operation_id)
        operation_val.update({
            "operation_name": operation_id.name or "",
            "operation_code": operation_id.code or "",
            "workcenter_name": operation_id.workcenter_id.name if operation_id.workcenter_id else "",
            "company_name": self.env.company.name,
            "tenantid": self.env.company.tenantid,
        })
        return operation_val
