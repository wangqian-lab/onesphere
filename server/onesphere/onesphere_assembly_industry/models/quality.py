# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OneshareQuality(models.Model):
    _inherit = "oneshare.quality.point"

    worksheet_img = fields.Binary('Image')

    tightening_opr_point_ids = fields.One2many('onesphere.tightening.opr.point', 'parent_quality_point_id')

    def get_tightening_operation_points(self, *args, **kwargs):
        ret = []
        self.ensure_one()
        if not self or not self.tightening_opr_point_ids:
            return ret
        for point in self.tightening_opr_point_ids:
            ret.append({'y_offset': point.y_offset, 'x_offset': point.x_offset})
        return ret
