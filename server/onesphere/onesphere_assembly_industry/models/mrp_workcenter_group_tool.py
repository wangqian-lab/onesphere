# -*- coding: utf-8 -*-
from odoo import api, fields, models

ASSEMBLY_TOOLS_TECH_NAME = ['tightening_nut_runner', 'tightening_wrench', 'tightening_spindle']


class MrpWorkcenterGroup(models.Model):
    _inherit = 'mrp.workcenter.group'

    @api.model
    def create(self, vals):
        ret = super(MrpWorkcenterGroup, self).create(vals)
        if not ret or 'onesphere_workcenter_ids' not in vals:
            return ret
        workgroup_id = ret
        equipment_obj = self.env['maintenance.equipment'].sudo()
        workgroup_tool_obj = self.env['mrp.workcenter.group.tool'].sudo()
        tightening_tool_ids = equipment_obj.search[('workcenter_id', 'in', ret.onesphere_workcenter_ids.ids),
                                                   ('technical_name', 'in', ASSEMBLY_TOOLS_TECH_NAME)]

        vals = []
        for tool in tightening_tool_ids:
            val = {
                "workgroup_id": workgroup_id.id,
                "workcenter_id": tool.workcenter_id.id,
                "tightening_tool_id": tool.id,
            }
            vals.append(val)
        workgroup_tool_obj.create(vals)
        return ret

    def _update_create_workcenter_group_tool(self):
        workgroup_tool_obj = self.env['mrp.workcenter.group.tool'].sudo()
        for wg in self:
            already_workcenter_ids = self.env['mrp.workcenter.group.tool'].search(
                [('workgroup_id', '=', wg.id)]).mapped('workcenter_id')
            workcenter_ids = wg.onesphere_workcenter_ids - already_workcenter_ids
            if not workcenter_ids:
                continue
            tool_ids = self.env['maintenance.equipment'].search(
                [('technical_name', 'in', ASSEMBLY_TOOLS_TECH_NAME), ('workcenter_id', 'in', workcenter_ids.ids)])

            vals = []
            for tool in tool_ids:
                val = {
                    "workgroup_id": wg.id,
                    "workcenter_id": tool.workcenter_id.id,
                    "tightening_tool_id": tool.id,
                }
                vals.append(val)
            workgroup_tool_obj.create(vals)

    def _update_unlink_workcenter_group_tool(self):
        need_unlink_recs = self.env['mrp.workcenter.group.tool']
        for wg in self:
            recs = self.env['mrp.workcenter.group.tool'].search([('workgroup_id', '=', wg.id),
                                                                 ('workcenter_id', 'not in',
                                                                  wg.onesphere_workcenter_ids.ids)])
            need_unlink_recs |= recs
        need_unlink_recs.sudo().unlink()

    def write(self, vals):
        ret = super(MrpWorkcenterGroup, self).write(vals)
        if 'onesphere_workcenter_ids' not in vals:
            return ret
        self._update_create_workcenter_group_tool()
        self._update_unlink_workcenter_group_tool()
        return ret


class MrpWorkcenterGroupTool(models.Model):
    _log_access = False
    _name = 'mrp.workcenter.group.tightening.tool'
    _description = 'Work Center Group Tightening Tool'
    _order = "id"

    workgroup_id = fields.Many2one('mrp.workcenter.group', string='Work Group', copy=False,
                                   ondelete='cascade', required=True)

    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Centre', copy=False,
                                    ondelete='cascade', required=True)

    tightening_tool_id = fields.Many2one('maintenance.equipment', string='Tightening Tool', copy=False,
                                         domain=[('technical_name', 'in', ASSEMBLY_TOOLS_TECH_NAME)],
                                         ondelete='cascade', required=True)

    _sql_constraints = [
        ('each_uniq', 'unique(workgroup_id,workcenter_id,tightening_tool_id)', 'Every Record Is Unique')]

    @api.model_create_multi
    def create(self, vals):
        context = self.env.context
        if context.get('force_nocreate_group_tool', False):
            return self
        return super(MrpWorkcenterGroupTool, self).create(vals)

    def name_get(self):
        res = []
        for tool_group_id in self:
            res.append((tool_group_id.id, '[%s]@%s@%s' % (
                tool_group_id.tightening_tool_id.serial_no, tool_group_id.workcenter_id.name,
                tool_group_id.workgroup_id.name)))
        return res
