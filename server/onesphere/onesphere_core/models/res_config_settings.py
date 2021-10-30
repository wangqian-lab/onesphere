# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    workorder_operation_merge = fields.Boolean(default=False,
                                               string='单工位工序合并工单',
                                               config_parameter='oneshare.operation.merge')
