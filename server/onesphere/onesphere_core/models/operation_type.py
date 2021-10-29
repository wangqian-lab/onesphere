# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class OneshareOperationType(models.Model):
    _name = "oneshare.operation.type"
    _description = "作业类型"
    _log_access = False
    _rec_name = 'code'
    _order = 'sequence, id'

    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer'),
                             ('mrp_operation', 'Manufacturing')],
                            'Type of Operation', required=True)

    color = fields.Integer('Color', default=1)

    active = fields.Boolean('Active', default=True)

    sequence = fields.Integer('Sequence', help="Used to order the 'All Operations' kanban view", default=1)
