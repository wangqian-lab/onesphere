# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


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
            operation_step_rel.operation_id.oper_version += 1
        return super(OneshareQuality, self).write(vals)
