# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.onesphere_assembly_industry.constants import ASSEMBLY_TOOLS_TECH_NAME, TIGHTENING_TEST_TYPE


class OneshareQuality(models.Model):
    _inherit = "oneshare.quality.point"

    worksheet_img = fields.Binary('Image')

    tightening_opr_point_ids = fields.One2many('onesphere.tightening.opr.point', 'parent_quality_point_id')

    step_version = fields.Integer(default=1, string='Step Version')

    def get_tightening_operation_points(self, *args, **kwargs):
        ret = []
        self.ensure_one()
        if not self or not self.tightening_opr_point_ids:
            return ret
        for point in self.tightening_opr_point_ids:
            ret.append({'y_offset': point.y_offset, 'x_offset': point.x_offset})
        return ret

    def write(self, vals):
        ver = self.step_version
        vals.update({"step_version": ver + 1})
        # 修改使用了该工步的作业的版本号
        for operation_step_rel in self.onesphere_operation_ids:
            if not operation_step_rel.operation_id:
                continue
            operation_step_rel.operation_id.oper_version += 1
        return super(OneshareQuality, self).write(vals)

    def select_tightening_units(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': '选择拧紧单元',
            'res_model': 'onesphere.tightening.unit',
            'target': 'new',
            'view_id': self.env.ref('onesphere_assembly_industry.onesphere_tightening_unit_view_tree').id,
            'view_mode': 'tree',
            'context': {
                'step_id': self.id
            }
        }

    @api.constrains('tightening_opr_point_ids', 'test_type_id')
    def tool_num_cons(self):
        if self.test_type_id.technical_name != TIGHTENING_TEST_TYPE:
            return
        for point in self.tightening_opr_point_ids:
            if len(point.tightening_units) > 1:
                raise ValidationError('拧紧工步类型，每个拧紧点不能选择多个拧紧单元')

    def change_points_sequence(self):
        sequence = 1
        for point in self.tightening_opr_point_ids:
            point.group_sequence = sequence
            sequence += 1
