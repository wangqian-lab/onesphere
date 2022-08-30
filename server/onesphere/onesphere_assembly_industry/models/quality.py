# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.onesphere_assembly_industry.constants import ASSEMBLY_TOOLS_TECH_NAME, TIGHTENING_TEST_TYPE


class OneshareQuality(models.Model):
    _inherit = "oneshare.quality.point"

    worksheet_img = fields.Binary('Image')

    tightening_opr_point_ids = fields.One2many('onesphere.tightening.opr.point', 'parent_quality_point_id')

    step_version = fields.Integer(default=1, string='Step Version')

    tag_ids = fields.Many2many('onesphere.work.step.tag', 'step_tag_rel', 'onesphere_step_id', 'onesphere_tag_id',
                               string='Step Tag Relationship')

    barcode_rule = fields.Char(string='Barcode Rule')
    time_limit = fields.Integer(string='Time Limit(s)', default=-1)

    @api.onchange('test_type_id')
    def onchange_test_type_id(self):
        if self.test_type_id.technical_name != 'text':
            self.time_limit = -1
        else:
            self.time_limit = 5

    @api.onchange('tightening_opr_point_ids')
    def update_points_group_sequence(self):
        group_sequence_list = self.tightening_opr_point_ids.mapped('group_sequence')
        if not group_sequence_list or min(group_sequence_list) > 0:
            return
        current_group_sequence = 1
        if max(group_sequence_list) > 0:
            current_group_sequence = max(group_sequence_list) + 1
        points = self.tightening_opr_point_ids.filtered(lambda x: x.group_sequence < 1)
        for point in points:
            point.group_sequence = current_group_sequence
            current_group_sequence += 1

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
                raise ValidationError(_('The Points Of Tightening Step Can Only Have One Tightening Unit'))

    def change_points_sequence(self):
        sequence = 1
        for point in self.tightening_opr_point_ids:
            point.sequence = sequence
            sequence += 1
