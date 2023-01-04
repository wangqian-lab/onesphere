# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.onesphere_assembly_industry.constants import TIGHTENING_TEST_TYPE
from odoo.exceptions import ValidationError


class OnesphereTighteningUnit(models.Model):
    _name = 'onesphere.tightening.unit'
    # _inherits = {'maintenance.equipment': 'tightening_controller_id'}
    _description = 'Assembly Tightening Unit'
    _log_access = False
    _check_company_auto = True

    ref = fields.Char('Tightening Unit Ref', required=True)
    name = fields.Char('Tightening Unit', related='tightening_controller_id.name', required=True, readonly=False)
    tightening_controller_id = fields.Many2one('maintenance.equipment', 'Controller', ondelete='cascade',
                                         check_company=True,
                                         required=True,
                                         domain=[('technical_name', 'in',
                                                  ['tightening_controller'])])
    category_id = fields.Many2one('maintenance.equipment.category', related='tightening_controller_id.category_id')
    serial_no = fields.Char('Tightening Controller Serial Number', related='tightening_controller_id.serial_no')

    company_id = fields.Many2one('res.company', string='Company', related='tightening_controller_id.company_id')
    partner_id = fields.Many2one('res.partner', string='Vendor', related='tightening_controller_id.partner_id',
                                 check_company=True)
    model = fields.Char('Model', related='tightening_controller_id.model')
    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Work Center', related='tightening_controller_id.workcenter_id', check_company=True,store=True)

    note = fields.Text('Note', related='tightening_controller_id.note')

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

