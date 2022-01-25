# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class RealOperVersion(models.Model):
    _name = "real.oper.version"

    _description = 'Real Oper Version'

    equipment_id = fields.Many2one('maintenance.equipment')
    operation_id = fields.Many2one('mrp.routing.workcenter')
    version = fields.Integer()
    state = fields.Selection([('finish', 'Finish'), ('todo', 'Todo')])