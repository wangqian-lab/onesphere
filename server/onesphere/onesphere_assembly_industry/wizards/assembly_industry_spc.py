# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
import logging
from odoo.exceptions import ValidationError
from odoo.addons.oneshare_utils.constants import ONESHARE_DEFAULT_SPC_MIN_LIMIT, ONESHARE_DEFAULT_SPC_MAX_LIMIT
import numpy as np
from odoo.addons.onesphere_spc.utils.lexen_spc.plot import normal, histogram
from odoo.addons.onesphere_spc.utils.lexen_spc.chart import cmk, cpk, xbar_rbar, rbar, covert2dArray
from typing import List

_logger = logging.getLogger(__name__)

measurement_type_field_map = {
    'torque': 'measurement_final_torque',
    'angle': 'measurement_final_angle'
}


def get_general_grid_option():
    return {
        'left': '10%',
        'right': 130,
        'top': '20%',
        'bottom': 30,
    }


X_LINE = 0
ARRAY_Y = 1
EFF_LENGTH = 2


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
        spc_step = float(others.get('spc_step', None))
        if not model_object_param:
            raise ValidationError('model_object_param is required')
        model_object = self.env['onesphere.tightening.result']
        query_type_field = query_type
        if not query_type_field:
            raise ValidationError(f'query_type: {query_type} is not valid. query_type_field is required')
        data = model_object.get_tightening_result_filter_datetime(query_date_from, query_date_to, query_type_field,
                                                                  limit=limit)
        _logger.debug(_(f"Spc Data of Query Result: {data}"))

        data_list = data[query_type]

        CMK = cmk(data_list, usl, lsl)
        CPK = cpk(data_list, usl, lsl)

        # 正太分布数据
        x1, y1, y2, eff_length = self._compute_dist_js(data_list, usl, lsl, spc_step)
        dict1 = {
            'x1': x1,
            'y1': y1,
            'y2': y2
        }

        if len(data) > 0:
            description = _(f'Tighetening Points number:{eff_length}/{len(data_list)},Mean:{np.mean(data_list) or 0, np.min(data_list):.2f},'
                            f'Range:[{np.min(data_list) or 0:.2f},{np.max(data_list) or 0:.2f}]')
        else:
            description = _('Tighetening Points number:0')

        dict2 = self._compute_dist_XR_js(data_list)
        ret = {
            'pages': {'o_spc_norm_dist': self.get_norm_dist_echarts_options(dict1, query_type, description),
                      # 'o_spc_weibull_dist': self.get_weill_dist_echarts_options(),
                      # 'o_spc_scatter': self.get_scatter_echarts_options(),
                      'o_spc_xr_chart': self.get_xr_spc_echarts_options(dict2, query_type, description),
                      },
            'cmk': CMK if CMK else 0.0,
            'cpk': CPK if CPK else 0.0,
        }

        return ret

    @staticmethod
    def get_xr_spc_echarts_options(data={}, query_type='torque', description=''):
        """生成X_R控制图需要的序列
        Args:
            data ([type]): [description]
        Returns:
            [Dict]: [echarts series Option]
        """
        y1 = data.get('data', [])
        y1 = [0] if len(y1) == 0 else y1
        x1 = [(x + 1) * 10 for x in range(len(y1))]
        titleOptions = {
                           'text': 'X-R SPC 控制图(%s)' % description
                       },
        gridOptions = get_general_grid_option()

        xAxisOptions = [{
            'name': '分组(个数))',
            'nameLocation': 'end',
            'nameTextStyle': {
                'fontStyle': 'bolder',
                'fontSize': 16
            },
            'data': x1,

        }]
        yAxisOptions = [
            {
                'type': 'value',
                'name': _('Torque(NM)') if query_type == 'torque' else _('Angle(Deg)'),
                # 'min': data.get('lower', 0),
                # 'max': data.get('upper', 'dataMax'),round(val * 100, 2)
                'min': round(min(min(y1), data.get('lower', 0) * 1.1 - data.get('upper', 60) * 0.1), 2),
                'max': round(max(max(y1), data.get('upper', 0) * 1.1 - data.get('lower', 0) * 0.1), 2),
                'interval': 1,
                'axisLabel': {
                    'formatter': '{value}'
                }
            },
        ]
        seriesOptions = [
            {
                'name': '曲线图',
                'type': 'line',
                'yAxisIndex': 0,
                'label': {'show': True},
                'data': y1,
                'markLine': {
                    'data': [{'type': 'average',
                              'name': '中心线-CL',
                              'label': {
                                  'show': True,
                                  'position': 'end',
                                  'formatter': '{b}\n{c}'
                              },
                              # 'lineStyle': {
                              #     'color': 'green'
                              # }
                              },
                             {
                                 'name': '控制上限-UCL',
                                 'label': {
                                     'show': True,
                                     'position': 'end',
                                     'formatter': '{b}\n{c}'
                                 },
                                 'yAxis': data.get('upper', 'dataMax'),
                                 # 'lineStyle': {
                                 #     'color': 'green'
                                 # }
                             },
                             {
                                 'name': '控制下限-LCL',
                                 'label': {
                                     'show': True,
                                     'position': 'end',
                                     'formatter': '{b}\n{c}'
                                 },
                                 'yAxis': data.get('lower', 0),
                                 # 'lineStyle': {
                                 #     'color': 'green'
                                 # }
                             }]
                }
            }
        ]
        return {
            'title': titleOptions,
            'grid': gridOptions,
            'xAxis': xAxisOptions,
            'yAxis': yAxisOptions,
            'series': seriesOptions
        }

    @staticmethod
    def get_norm_dist_echarts_options(data={}, query_type='torque', description=''):
        """生成正态分布需要的序列
        Args:
            data ([type]): [description]
        Returns:
            [Dict]: [echarts series Option]
        """
        x1 = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        y1 = [2.0, 4.9, 7.0, 23.2, 25.6, 76.7]
        y2 = [2.0, 2.2, 3.3, 4.5, 6.3, 10.2, 20.3]
        titleOptions = {
            'text': '正态分布(%s)' % description,
            'textAlign': 'auto',
        }
        gridOptions = get_general_grid_option()

        xAxisOptions = [{
            'name': _('Torque(NM)') if query_type == 'torque' else _('Angle(Deg)'),
            'nameLocation': 'end',
            'nameTextStyle': {
                'fontStyle': 'bolder',
                'fontSize': 16
            },
            'data': data.get('x1', x1),

        }]
        yAxisOptions = [
            {
                'type': 'value',
                'name': '概率(Probability)',
                'min': 0,
                'max': 'dataMax',
                'interval': 5,
                'axisLabel': {
                    'formatter': '{value} %'
                }
            },
        ]

        seriesOptions = [
            {
                'name': '直方图',
                'type': 'bar',
                'label': {'show': True},
                'data': data.get('y1', y1)
            },
            {
                'name': '曲线图',
                'type': 'line',
                'yAxisIndex': 0,
                'label': {'show': True},
                'data': data.get('y2', y2),
                'smooth': True
            }
        ]
        return {
            'title': titleOptions,
            'grid': gridOptions,
            'xAxis': xAxisOptions,
            'yAxis': yAxisOptions,
            'series': seriesOptions
        }

    def _compute_dist_js(self, data_list: List[float], usl: float, lsl: float, spc_step: float):
        histogram_data = histogram(data_list, usl, lsl, spc_step)
        normal_data = normal(data_list, usl, lsl, spc_step)
        x_axis_data, y_histogram_data, y_normal_data = [], [], []
        x_line_len = len(histogram_data[X_LINE])
        for i in range(x_line_len - 1):
            # 取x轴数据生成区间，并生成对应区间的直方图数据和正太分布数据，故循环长度为x轴数据长度减1
            x_axis_data.append(f'{histogram_data[X_LINE][i]:.1f},{histogram_data[X_LINE][i + 1]:.1f}')
            y_histogram_data.append(round(histogram_data[ARRAY_Y][i] * 100, 2))
            y_normal_data.append(round(normal_data[ARRAY_Y][i] * 100, 2))
        return x_axis_data, y_histogram_data, y_normal_data, histogram_data[EFF_LENGTH]

    def _compute_dist_XR_js(self, data_list: List[float]):
        # x_bar = np.arange(int(min), int(max), 1)
        array_2d_data = covert2dArray(data_list, 10)
        XR_data = xbar_rbar(array_2d_data, 10)
        # C = rbar(A, 10)
        return XR_data
