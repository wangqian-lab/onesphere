# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

try:
    from odoo.models import OneshareHyperModel as HModel
except ImportError:
    from odoo.models import Model as HModel


class OperationResult(HModel):
    """
    采集拧紧数据结果表
    """
    _name = "onesphere.tightening.result"

    _rec_name = 'track_no'

    _hyper_interval = '1 month'

    _hyper_field = 'control_time'

    control_time = fields.Date(string=u'数据生成时间', default=fields.Date.today, required=True)

    track_no = fields.Char(default='', string=u'追溯码')

    attribute_equipment_no = fields.Char(u'设备序列号')

    tightening_process_no = fields.Char(string='Tightening Process(Pset/Job)')

    measurement_final_torque = fields.Float(string='Tightening Final Torque',
                                            digits='decimal_tightening_result_measurement')

    measurement_final_angle = fields.Float(string='Tightening Final Angle',
                                           digits='decimal_tightening_result_measurement')

    measurement_step_results = fields.Char(string='Tightening Step Results', help=u'分段拧紧结果')

    curve_data_url = fields.Char('Tightening Curve Data Url', help=u'拧紧曲线数据URL')




