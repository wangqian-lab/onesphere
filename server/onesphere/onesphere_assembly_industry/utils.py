# -*- coding: utf-8 -*-
from typing import List

from odoo.addons.onesphere_spc.utils.lexen_spc.chart import xbar_rbar, covert2dArray

from odoo import _


def get_general_grid_option():
    return {
        'left': '10%',
        'right': 130,
        'top': '20%',
        'bottom': 30,
    }


def _compute_dist_XR_js(data_list: List[float], step=10):
    # x_bar = np.arange(int(min), int(max), 1)
    array_2d_data = covert2dArray(data_list, step)
    XR_data = xbar_rbar(array_2d_data, step)
    # C = rbar(A, 10)
    return XR_data


def get_xr_spc_echarts_options(data={}, query_type='torque', description='', step=10):
    """生成X_R控制图需要的序列
    Args:
        data ([type]): [description]
    Returns:
        [Dict]: [echarts series Option]
    """
    y1 = data.get('data', [])
    y1 = [0] if len(y1) == 0 else y1
    x1 = [f'{i}({(i - 1) * step}~{i * step})' for i in range(1, len(y1) + 1)]
    titleOptions = {
                       'text': f'X-Bar控制图\n{description}'
                   },
    gridOptions = get_general_grid_option()

    xAxisOptions = [{
        'name': '分组(个数)',
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
            'symbol': 'roundRect',
            'symbolSize': 10,
            'yAxisIndex': 0,
            'label': {'show': True},
            'data': y1,
            'markLine': {
                "animation": False,
                "silent": True,
                "label": {
                    "show": True
                },
                "symbol": 'none',
                'data': [
                    {
                        'type': 'average',
                        'name': '中心线-CL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'lineStyle': {
                            'type': 'dashed',  # 目标值虚线，其他值实线
                            'width': 2,
                            'color': '#CC8925'
                        },
                    },
                    {
                        'name': '控制上限-UCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('upper', 'dataMax'),
                        'lineStyle': {
                            'type': 'solid',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
                    },
                    {
                        'name': '2/3控制上限-UCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('upper', 'dataMax') * 2 / 3 + data.get('center') / 3,
                        'lineStyle': {
                            'type': 'dashed',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
                    },

                    {
                        'name': '1/3控制上限-UCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('upper', 'dataMax') / 3 + data.get('center') * 2 / 3,
                        'lineStyle': {
                            'type': 'dashed',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
                    },
                    {
                        'name': '1/3控制下限-LCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('lower', 0) / 3 + data.get('center') * 2 / 3,
                        'lineStyle': {
                            'type': 'dashed',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
                    },
                    {
                        'name': '2/3控制下限-LCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('lower', 0) * 2 / 3 + data.get('center') / 3,
                        'lineStyle': {
                            'type': 'dashed',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
                    },
                    {
                        'name': '控制下限-LCL',
                        'label': {
                            'show': True,
                            'position': 'insideEndTop',
                            'fontSize': 12,
                            'formatter': '{b}\n{c}'
                        },
                        'yAxis': data.get('lower', 0),
                        'lineStyle': {
                            'type': 'solid',  # 目标值虚线，其他值实线
                            'width': 1,
                            'color': '#CC8925'
                        },
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


def get_dist_echarts_options(data={}, query_type='torque', description='', type='norm'):
    """生成正态分布需要的序列
    Args:
        data ([type]): [description]
    Returns:
        [Dict]: [echarts series Option]
    """
    titleOptions = {
        'textAlign': 'auto',
    }
    if type == 'norm':
        titleOptions.update({
            'text': f'正态分布\n{description}'
        })
    if type == 'weill':
        titleOptions.update({
            'text': f'失效韦伯分布\n{description}'
        })
    gridOptions = get_general_grid_option()

    xAxisOptions = [{
        'name': _('Torque(NM)') if query_type == 'torque' else _('Angle(Deg)'),
        'nameLocation': 'end',
        'nameTextStyle': {
            'fontStyle': 'bolder',
            'fontSize': 16
        },
        'data': data.get('x1', []),

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
            'data': data.get('y1', [])
        },
        {
            'name': '标准正态分布',
            'type': 'line',
            'yAxisIndex': 0,
            'label': {'show': False},
            'data': data.get('y2', []),
            'areaStyle': {'shadowColor': 'rgba(58,132,255, 0.5)', 'shadowBlur': 10, 'opacity': 0.2},
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
