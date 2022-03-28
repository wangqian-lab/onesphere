# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.onesphere_assembly_industry.constants import ASSEMBLY_TOOLS_TECH_NAME


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def create_group_tool(self):
        for worckcenter_group in self.workcenter_id.group_ids:
            val = {
                "workgroup_id": worckcenter_group.id,
                "workcenter_id": self.workcenter_id.id,
                "tightening_tool_id": self.id,
            }
            self.env['mrp.workcenter.group.tightening.tool'].sudo().create(val)

    # 修改拧紧工具类设备时，如果所属工作中心有变化，将更新拧紧工具组表
    def write(self, vals):
        ret = super(MaintenanceEquipment, self).write(vals)
        if 'workcenter_id' not in vals:
            return ret
        for tool_id in self:
            if tool_id.category_id.technical_name not in ASSEMBLY_TOOLS_TECH_NAME:
                continue
            need_unlink_recs = self.env['mrp.workcenter.group.tightening.tool'].search(
                [('tightening_tool_id', '=', tool_id.id)])
            need_unlink_recs.sudo().unlink()
            tool_id.create_group_tool()
        return ret

    # 创建拧紧工具时，生成对应拧紧工具组数据
    @api.model
    def create(self, vals):
        ret = super(MaintenanceEquipment, self).create(vals)
        if 'workcenter_id' not in vals:
            return ret
        for tool_id in ret:
            if tool_id.category_id.technical_name not in ASSEMBLY_TOOLS_TECH_NAME:
                continue
            tool_id.create_group_tool()
        return ret
