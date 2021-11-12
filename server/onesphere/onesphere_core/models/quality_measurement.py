# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class OneshareMeasurementItem(models.Model):
    _name = 'oneshare.measurement.item'
    _description = 'Measurement Item'

    _order = "sequence"

    sequence = fields.Integer('sequence', default=1)

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'), required=True)

    note = fields.Char(string="Description")

    parent_quality_point_id = fields.Many2one('oneshare.quality.point', ondelete='cascade', index=True,
                                              string='Working Step')

    test_type = fields.Selection([
        ('passfail', 'Pass - Fail'),
        ('measure', 'Measure')], string="Test Type",
        default='passfail', required=True)

    norm = fields.Float('Norm', digits='Quality Tests')
    tolerance_min = fields.Float('Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float('Max Tolerance', digits='Quality Tests')
    norm_unit = fields.Char('Unit of Measure', default=lambda self: 'mm')

    test_equipment_id = fields.Many2one('maintenance.equipment', 'Test Equipment')

    @api.onchange('test_type')
    def onchange_test_type(self):
        if self.test_type == 'passfail':
            self.measure = None

    @api.depends('measure')
    def _compute_measure_success(self):
        self.ensure_one()
        if self.test_type == 'passfail':
            self.measure_success = 'none'
        else:
            if self.measure < self.tolerance_min or self.measure > self.tolerance_max:
                self.measure_success = 'fail'
            else:
                self.measure_success = 'pass'

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('oneshare.measurement.item') or _('New')
        if 'note' not in vals or not vals.get('note', ''):
            vals['note'] = vals['name']
        return super(OneshareMeasurementItem, self).create(vals)
