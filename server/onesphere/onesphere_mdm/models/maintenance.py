# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    @api.depends('name')
    def _compute_technical_name(self):
        for equipment in self:
            if equipment.technical_name:
                continue
            equipment.technical_name = equipment.name

    technical_name = fields.Char('Technical name', required=True, compute=_compute_technical_name, store=True)

    @api.model
    def create(self, vals):
        if not vals.get('technical_name', None):
            vals.update({'technical_name': vals.get('name')})
        return super(MaintenanceEquipmentCategory, self).create(vals)
