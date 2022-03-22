# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RealOperVersion(models.Model):
    _name = "real.oper.version"

    _description = 'Real Oper Version'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation', required=True)
    version = fields.Integer(string='Version')
    state = fields.Selection([('finish', 'Finish'), ('todo', 'Todo')], string='State')
