# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class MrpWorkcenterGroup(models.Model):
    _log_access = False
    _name = 'mrp.workcenter.group'
    _description = 'Work Center Group'
    _order = "code"

    code = fields.Char('Reference', copy=False, required=True)
    name = fields.Char('Work Center Group')
    onesphere_workcenter_ids = fields.Many2many('mrp.workcenter', 'mrp_workcenter_group_rel', 'group_id',
                                                'workcenter_id',
                                                string="Work Centers", copy=False, check_company=True)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    active = fields.Boolean(
        'Active', default=True,
        help="If the active field is set to False, it will allow you to hide the bills of material without removing it.")

    _sql_constraints = [('code_uniq', 'unique(code)', 'Only one code per Work Center Group is allowed')]

    def name_get(self):
        res = []
        for center_group in self:
            res.append((center_group.id, '[%s] %s' % (center_group.code, center_group.name)))
        return res

class MrpWorkcenterGroupTool(models.Model):
    _name = 'mrp.workcenter.group.tool'
    _description = 'Work Center Group Tool'
    _order = "id"

    workgroup_id = fields.Many2one('mrp.workcenter.group', string='Work Group', copy=False,
                                   ondelete='cascade', required=True)

    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Centre', copy=False,
                                    ondelete='cascade', required=True)

    tool_id = fields.Many2one('maintenance.equipment', string='Tightening Tool(Tightening Gun/Wrench)', copy=False,
                              ondelete='cascade', required=True)

    _sql_constraints = [
        ('each_uniq', 'unique(workgroup_id,workcenter_id,tool_id)', 'Every Record Is Unique')]

    @api.model
    def create(self, vals):
        context = self.env.context
        if context.get('force_uncreate_group_tool', False):
            return self
        return super(MrpWorkcenterGroupTool, self).create(vals)

    def name_get(self):
        res = []
        for tool_group_id in self:
            res.append((tool_group_id.id, _('[%s]@%s@%s') % (
                tool_group_id.tool_id.serial_no, tool_group_id.workcenter_id.name, tool_group_id.workgroup_id.name)))
        return res