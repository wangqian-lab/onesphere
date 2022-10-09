# -*- coding: utf-8 -*-
from odoo import _


def get_general_grid_option():
    return {
        'left': '10%',
        'right': 130,
        'top': '20%',
        'bottom': 30,
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
            'name': '曲线图',
            'type': 'line',
            'yAxisIndex': 0,
            'label': {'show': True},
            'data': data.get('y2', []),
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
