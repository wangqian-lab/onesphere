# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OnesphereTighteningUnit(models.Model):
    _name = 'onesphere.tightening.unit'
    _inherits = {'maintenance.equipment': 'tightening_tool_id'}
    _description = 'Assembly Tightening Unit'
    _log_access = False
    _check_company_auto = True

    name = fields.Char('Tightening Unit', related='tightening_tool_id.name', required=True, readonly=False)
    active = fields.Boolean(default=True, related='tightening_tool_id.active', readonly=False)
    tightening_tool_id = fields.Many2one('maintenance.equipment', 'Tightening Tool', ondelete='cascade',
                                         check_company=True,
                                         required=True,
                                         domain=[('technical_name', 'in',
                                                  ['tightening_controller', 'tightening_nut_runner',
                                                   'tightening_wrench'])])
    category_id = fields.Many2one('maintenance.equipment.category', related='tightening_tool_id.category_id',
                                  readonly=False, domain=[('technical_name', 'in',
                                                           ['tightening_controller', 'tightening_nut_runner',
                                                            'tightening_wrench'])])
    serial_no = fields.Char('Tightening Tool Serial Number', related='tightening_tool_id.serial_no',
                            readonly=False)

    company_id = fields.Many2one('res.company', string='Company', related='tightening_tool_id.company_id',
                                 default=lambda self: self.env.company, readonly=False)
    partner_id = fields.Many2one('res.partner', string='Vendor', related='tightening_tool_id.partner_id',
                                 check_company=True, readonly=False)
    model = fields.Char('Model', related='tightening_tool_id.model', readonly=False)
    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Work Center', related='tightening_tool_id.workcenter_id', check_company=True,
        readonly=False)

    note = fields.Text('Note', related='tightening_tool_id.note', readonly=False)
