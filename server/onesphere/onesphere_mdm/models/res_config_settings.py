# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_operation_all_step = fields.Boolean(default=False, string='下发工艺所有工步',
                                             help='下发工艺所有工步，使工位可以扫码生成工单', config_parameter='oneshare.send.all.steps')
