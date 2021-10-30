# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OneshareQuality(models.Model):
    _inherit = "oneshare.quality.point"

    worksheet_img = fields.Binary('Image')

    def get_tightening_operation_points(self, *args, **kwargs):
        ret = []
        self.ensure_one()
        if not self:
            return ret
        return ret
