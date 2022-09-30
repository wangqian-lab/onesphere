# -*- coding: utf-8 -*-

from odoo.addons.onesphere_assembly_industry.constants import DEFAULT_BOLT_NAME_RULES, ENV_PROCESS_PROPOSAL_DURATION

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bolt_name_rules = fields.Char(default=DEFAULT_BOLT_NAME_RULES,
                                  string='螺栓编号拼接规则',
                                  help='the rules of bolt name',
                                  config_parameter='oneshare.bolt_name.rules')

    tightening_process_proposal_duration = fields.Integer(default=ENV_PROCESS_PROPOSAL_DURATION,
                                                          string='拧紧工艺建议计算间隔时间(天)',
                                                          help='拧紧工艺建议计算间隔时间, 默认为三十天',
                                                          config_parameter='oneshare.tightening.process.proposal.duration')
