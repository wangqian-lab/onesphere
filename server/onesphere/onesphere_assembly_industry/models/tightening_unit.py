# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.onesphere_assembly_industry.constants import TIGHTENING_TEST_TYPE
from odoo.exceptions import ValidationError


class OnesphereTighteningUnit(models.Model):
    _name = 'onesphere.tightening.unit'
    _inherits = {'maintenance.equipment': 'tightening_tool_id'}
    _description = 'Assembly Tightening Unit'
    _log_access = False
    _check_company_auto = True

    ref = fields.Char('Tightening Unit Ref', required=True)
    name = fields.Char('Tightening Unit', related='tightening_tool_id.name', required=True, readonly=False)
    tightening_tool_id = fields.Many2one('maintenance.equipment', 'Controller', ondelete='cascade',
                                         check_company=True,
                                         required=True,
                                         domain=[('technical_name', 'in',
                                                  ['tightening_controller'])])
    category_id = fields.Many2one('maintenance.equipment.category', related='tightening_tool_id.category_id',
                                  readonly=False, domain=[('technical_name', 'in',
                                                           ['tightening_spindle', 'tightening_nut_runner',
                                                            'tightening_wrench'])])
    serial_no = fields.Char('Tightening Controller Serial Number', related='tightening_tool_id.serial_no',
                            readonly=False)

    company_id = fields.Many2one('res.company', string='Company', related='tightening_tool_id.company_id',
                                 default=lambda self: self.env.company, readonly=False)
    partner_id = fields.Many2one('res.partner', string='Vendor', related='tightening_tool_id.partner_id',
                                 check_company=True, readonly=False)
    model = fields.Char('Model', related='tightening_tool_id.model', readonly=False)
    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Work Center', related='tightening_tool_id.workcenter_id', check_company=True,
        readonly=False, store=True)

    note = fields.Text('Note', related='tightening_tool_id.note', readonly=False)

    _sql_constraints = [
        (
            'unique_tightening_unit_per_work_center',
            'UNIQUE(ref, workcenter_id)',
            'Unique Tightening Unit Ref Per Work Center',
        ),
    ]

    def name_get(self):
        res = []
        for unit in self:
            res.append((unit.id, f'#{unit.ref}@{unit.serial_no}@{unit.workcenter_id.display_name}'))
        return res

    def select_tightening_unit_confirm(self):
        if not self.env.context.get('step_id'):
            return
        step = self.env['oneshare.quality.point'].search(
            [('id', '=', self.env.context.get('step_id'))])
        if step.test_type_id.technical_name == TIGHTENING_TEST_TYPE and len(self) > 1:
            raise ValidationError('拧紧工步类型，每个拧紧点不能选择多个工具')
        points = step.tightening_opr_point_ids
        for point in points:
            point.tightening_units = [(6, 0, self.ids)]
