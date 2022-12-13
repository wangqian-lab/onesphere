# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class OneshareMeasurementCalcItem(models.Model):
    _name = 'oneshare.measurement.calc.item'
    _description = '测量计算类型项'
    _log_access = False

    def _get_measurement_item_domain(self):
        parent_quality_point_id = self.env.context.get('default_parent_quality_point_id', False)
        if parent_quality_point_id:
            return [('measurement_item_id.parent_quality_point_id', '=', parent_quality_point_id)]
        return [(1, '=', 1)]

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'), required=True)

    measurement_calc_type_id = fields.Many2one('oneshare.measurement.calc.type', required=True)

    parent_quality_point_id = fields.Many2one('oneshare.quality.point', ondelete='cascade', index=True,
                                              string='Working Step')

    note = fields.Char(string="Description")

    measurement_item_ids = fields.Many2many('oneshare.measurement.item', 'measurement_item_calc_type_rel',
                                            'calc_item_id', 'measurement_item_id',
                                            domain=lambda self: self._get_measurement_item_domain())


class OneshareMeasurementCalculateType(models.Model):
    _name = 'oneshare.measurement.calc.type'
    _description = '测量计算类型'
    _log_access = False
    _rec_name = 'code'

    code = fields.Char(string="Reference", required=True)
    formula = fields.Char(string="Formula", required=True)
    desc = fields.Char(string="Description")
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', "Field code must be unique per measurement calculate type."),
    ]

    def name_get(self):
        return [(calc_type.id,
                 u"[{0}]{1}".format(calc_type.code, calc_type.desc)) for calc_type in self]


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

    test_equipment_id = fields.Many2one('maintenance.equipment', 'Test Equipment',
                                        domain=[('category_id.technical_name', '=', 'general_measure_equipment')])

    # @api.onchange('test_type')
    # def onchange_test_type(self):
    #     if self.test_type == 'passfail':
    #         self.measure = None
    #
    # @api.depends('measure')
    # def _compute_measure_success(self):
    #     self.ensure_one()
    #     if self.test_type == 'passfail':
    #         self.measure_success = 'none'
    #     else:
    #         if self.measure < self.tolerance_min or self.measure > self.tolerance_max:
    #             self.measure_success = 'fail'
    #         else:
    #             self.measure_success = 'pass'

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('oneshare.measurement.item') or _('New')
        if 'note' not in vals or not vals.get('note', ''):
            vals['note'] = vals['name']
        return super(OneshareMeasurementItem, self).create(vals)
