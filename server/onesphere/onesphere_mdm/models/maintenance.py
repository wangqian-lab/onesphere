# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _check_company_auto = True

    technical_name = fields.Char('Technical name', related='category_id.technical_name', store=True)
    expected_mtbf = fields.Integer(string='Expected MTBF', help='Expected Mean Time Between Failure')
    mtbf = fields.Integer(string='MTBF',
                          help='Mean Time Between Failure, computed based on done corrective maintenances.')
    mttr = fields.Integer(string='MTTR', help='Mean Time To Repair')
    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Work Center', check_company=True)

    def button_mrp_workcenter(self):
        self.ensure_one()
        return {
            'name': _('work centers'),
            'view_mode': 'form',
            'res_model': 'mrp.workcenter',
            'view_id': self.env.ref('mrp.mrp_workcenter_view').id,
            'type': 'ir.actions.act_window',
            'res_id': self.workcenter_id.id,
            'context': {
                'default_company_id': self.company_id.id
            }
        }


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    @api.depends('name')
    def _compute_technical_name(self):
        for category in self:
            if category.technical_name:
                continue
            category.technical_name = category.name

    technical_name = fields.Char('Technical name', required=True, compute=_compute_technical_name, store=True)

    _sql_constraints = [
        ('technical_name_uniq', 'unique (technical_name)',
         'The technical name of the equipment category must be unique!')
    ]

    @api.model
    def create(self, vals):
        if not vals.get('technical_name', None):
            vals.update({'technical_name': vals.get('name')})
        return super(MaintenanceEquipmentCategory, self).create(vals)
