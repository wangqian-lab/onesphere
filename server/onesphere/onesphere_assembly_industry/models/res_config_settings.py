# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.onesphere_assembly_industry.constants import DEFAULT_BOLT_NAME_RULES


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bolt_name_rules = fields.Char(default=DEFAULT_BOLT_NAME_RULES,
                                  string='螺栓编号拼接规则',
                                  help='the rules of bolt name',
                                  config_parameter='oneshare.bolt_name.rules')
