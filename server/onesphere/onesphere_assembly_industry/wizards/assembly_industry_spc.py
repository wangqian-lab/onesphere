# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class OnesphereAssyIndustrySPC(models.TransientModel):
    _name = 'onesphere.assy.industry.spc'
    _description = '装配行业拧紧SPC分析'
    _inherit = ['onesphere.spc.mixin']

    measurement_type = fields.Selection([('torque', 'Torque'),
                                         ('angle', 'Angle')],
                                        default='torque',
                                        string='Assembly Industry SPC Measurement Type')

    @api.model
    def default_get(self, fields_list):
        res = super(OnesphereAssyIndustrySPC, self).default_get(fields_list)
        if 'model_object' in fields_list:
            res.update({
                'model_object': self.env['ir.model'].search(
                    [('model', '=', 'onesphere.tightening.result')]).id
            })
        if 'model_object_field' in fields_list:
            res.update({
                'model_object_field': self.env['ir.model.fields']._get_ids(
                    'onesphere.tightening.result').get('measurement_final_torque')
            })
        return res

    @api.onchange('measurement_type')
    def _onchange_measurement_type(self):
        self.ensure_one()
        measurement_type = self.measurement_type
        field_name = 'measurement_final_torque'
        if measurement_type == 'angle':
            field_name = 'measurement_final_angle'
        self.model_object_field = self.env['ir.model.fields']._get('onesphere.tightening.result', field_name)
