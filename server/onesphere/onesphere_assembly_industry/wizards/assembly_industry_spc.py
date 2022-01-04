# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
import logging
from odoo.exceptions import ValidationError
from odoo.addons.oneshare_utils.constants import ONESHARE_DEFAULT_SPC_MIN_LIMIT, ONESHARE_DEFAULT_SPC_MAX_LIMIT

_logger = logging.getLogger(__name__)

measurement_type_field_map = {
    'torque': 'measurement_final_torque',
    'angle': 'measurement_final_angle'
}


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
        field_name = measurement_type_field_map[measurement_type]
        self.model_object_field = self.env['ir.model.fields']._get('onesphere.tightening.result', field_name)

    @api.model
    def query_spc(self, query_from=None, query_to=None, query_type='torque', usl=10.0, lsl=1.0,
                  limit=ONESHARE_DEFAULT_SPC_MAX_LIMIT, others={}, *args,
                  **kwargs):
        _logger.debug(f"query spc, params: {args}, {kwargs}")
        query_date_from = fields.Datetime.from_string(query_from)  # UTC 时间
        query_date_to = fields.Datetime.from_string(query_to)
        model_object_param = others.get('model_object', None)
        if not model_object_param:
            raise ValidationError('model_object_param is required')
        model_object = self.env['onesphere.tightening.result']
        query_type_field = query_type
        if not query_type_field:
            raise ValidationError(f'query_type: {query_type} is not valid. query_type_field is required')
        data = model_object.get_tightening_result_filter_datetime(query_date_from, query_date_to, query_type_field,
                                                                  limit=limit)
        _logger.debug(f"获取到的SPC查询原始结果数据: {data}")
