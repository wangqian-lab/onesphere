# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    workorder_operation_merge = fields.Boolean(default=False,
                                               string='单工位工序合并工单', help='一个工位上的同一工单不同工序如果需要合并成一个工单的话，进行勾选',
                                               config_parameter='oneshare.operation.merge')
