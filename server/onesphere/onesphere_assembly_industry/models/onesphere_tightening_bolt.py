# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OnesphereTighteningBolt(models.Model):
    _name = "onesphere.tightening.bolt"
    _description = 'Tightening Bolt Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')
    type = fields.Selection([('missing', 'Missing'), ('verified', 'Verified')], string='Type', default='verified',
                            required=True)
    bolt_result_rel = fields.One2many('onesphere.tightening.result', 'tightening_point_name', string='Bolt Result Rel')

    _sql_constraints = [('name_uniq', 'unique (name)', "bolt name already exists !")]
