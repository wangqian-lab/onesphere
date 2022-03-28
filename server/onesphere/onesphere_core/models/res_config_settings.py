# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    workorder_operation_merge = fields.Boolean(default=False,
                                               string='单工位工序合并工单',
                                               help='Chose it If Need Merge Different Operations Of One Workorder',
                                               config_parameter='oneshare.operation.merge')
