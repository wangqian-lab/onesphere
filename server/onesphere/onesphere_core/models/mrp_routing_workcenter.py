# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    @api.depends('work_step_ids')
    def _compute_work_step_count(self):
        for record in self:
            if not record.work_step_ids:
                record.work_step_count = 0
            record.work_step_count = len(record.work_step_ids)

    work_step_ids = fields.One2many('onesphere.mrp.operation.step.rel', 'operation_id', string='Work Step',
                                    check_company=True)

    onesphere_bom_ids = fields.Many2many('mrp.bom', 'bom_operation_rel', 'onesphere_operation_id',
                                         'onesphere_bom_id',
                                         string='MRP Bom Operation Relationship')

    work_step_count = fields.Integer('Working Steps', compute=_compute_work_step_count)

    def button_open_mrp_workorder_step_action(self):
        self.ensure_one()
        step_ids = self.work_step_ids.mapped('work_step_id').ids
        action = self.env.ref('onesphere_core.onesphere_action_open_work_step').read()[0]
        ctx = dict(self._context, default_operation_type='mrp_operation', default_company_id=self.env.company.id,
                   default_is_workorder_step=True)
        action.update({'context': ctx})
        action['domain'] = [('id', 'in', step_ids)]
        action['name'] = _("Working Steps")

        return action

    # 重写删除，会将该作业与工步的关联也删掉
    def unlink(self):
        self.env['onesphere.mrp.operation.step.rel'].search([('operation_id', 'in', self.ids)]).unlink()
        result = super(MrpRoutingWorkcenter, self).unlink()
        return result
