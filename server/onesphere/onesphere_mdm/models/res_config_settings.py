# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_operation_all_step = fields.Boolean(default=False, string='下发工艺所有工步',
                                             help='Send All Steps of Operation To Make Sure Work Center Can Make Orders By Scan', config_parameter='oneshare.send.all.steps')
