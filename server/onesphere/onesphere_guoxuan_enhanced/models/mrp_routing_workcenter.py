# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.onesphere_assembly_industry.constants import ALL_TIGHTENING_TEST_TYPE_LIST


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    def _pack_operation_val(self, bom_id, operation_id):
        # 生成作业对应数据
        operation_val = {
            "workcenter_id": operation_id.workcenter_id.id,
            "max_op_time": operation_id.max_op_time,
            "name": f"[{operation_id.name}]@{operation_id.workcenter_id.name}",
            "product_id": bom_id.product_tmpl_id.id if bom_id else 0,
            "product_type": bom_id.product_tmpl_id.default_code if bom_id else "",
            "workcenter_code": operation_id.workcenter_id.code if operation_id.workcenter_id else "",
            'product_type_image': u'data:{0};base64,{1}'.format('image/png',
                                                                bom_id.product_tmpl_id.image_1920.decode()) if bom_id.product_tmpl_id.image_1920 else "",
            "steps": [],
            "operation_name": operation_id.name or "",
            "operation_code": operation_id.code or "",
            "workcenter_name": operation_id.workcenter_id.name if operation_id.workcenter_id else "",
            "company_name": self.env.company.name,
            "tenantid": self.env.company.tenantid,
        }
        # 查看配置中是否下发所有工步数据，是则遍历所有工步，否则只遍历拧紧工步
        config = self.env['ir.config_parameter']
        all_step_flag = config.get_param('oneshare.send.all.steps')
        all_need_steps = operation_id.work_step_ids.mapped('work_step_id')
        if not all_step_flag:
            all_need_steps = all_need_steps.filtered(
                lambda step: step and (step.test_type in ALL_TIGHTENING_TEST_TYPE_LIST))
        # 生成工步数据
        steps_data = []
        for step_id in all_need_steps:
            step_val = self._pack_step_val(step_id)
            steps_data.append(step_val)

        operation_val.update({
            "steps": steps_data
        })
        return operation_val
