# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import uuid
import zipfile
import json
import pandas as pd

from odoo import http, _
# import csv
from odoo.exceptions import ValidationError
from odoo.http import request, send_file
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.onesphere_assembly_industry.constants import WORK_MODE_DIC

_logger = logging.getLogger(__name__)
ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE = os.getenv('ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE', 'utf-8')


def get_temp_file_from_result(env, result_ids, platform=''):
    if platform and platform.upper() == 'WINDOWS':
        download_tightening_results_encode = 'gbk'  # GBK
    result_list = []
    for result in result_ids:
        control_time = (result.control_time + (timedelta(hours=8))).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT) if result.control_time else ''
        work_mode = WORK_MODE_DIC.get(result.work_mode, '')
        ret = {'追溯码': result.track_no or '',
               '工位': result.workcenter_code or '',
               '工作模式': work_mode,
               '工具序列号': result.attribute_equipment_no or '',
               '螺栓名称': result.tightening_point_name.name if result.tightening_point_name else '',
               '拧紧策略': result.tightening_strategy or '',
               '拧紧结果': result.tightening_result or '',
               '拧紧最终扭矩': result.measurement_final_torque or '',
               '拧紧最终角度': result.measurement_final_angle or '',
               '拧紧时间': control_time,
               '拧紧人员': result.user_list or ''}
        result_list.append(ret)
    df = pd.DataFrame.from_records(result_list)
    temp_file = tempfile.TemporaryFile()
    ICP = env['ir.config_parameter']
    download_tightening_results_encode = ICP.get_param(
        "onesphere_wave.download_tightening_results_encode",
        default=ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE)
    with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zfp:
        with zfp.open('tightening_results.xlsx', mode="w") as xlsx_f:
            df.to_excel(xlsx_f, sheet_name=u'拧紧结果', freeze_panes=(1, 0),
                        encoding=download_tightening_results_encode)
        curve_datas = result_ids._get_curve_data()
        for curve_dict in curve_datas:
            if curve_dict.get('name'):
                fn = curve_dict.pop('name')
            else:
                fn = ''
            if not fn:
                fn = uuid.uuid4().hex
                _logger.error(f'获取曲线名称失败, 重命名为{fn}.csv')
            with zfp.open(f'{fn}.csv', mode="w") as f:
                df = pd.DataFrame.from_dict(curve_dict)
                ret = df.to_csv(path_or_buf=None, index=False, columns=['cur_m', 'cur_w', 'cur_t'],
                                header=['扭矩', '角度', '时间'])
                f.write(ret.encode(download_tightening_results_encode))
    temp_file.seek(0)
    return temp_file


class OnesphereTighteningResultController(http.Controller):
    @http.route('/oneshare/assembly/tightening/download', type='http',
                methods=['GET'], auth='user', cors='*', csrf=False)
    def download_tightening_results(self, *args, **kwargs):
        platform = request.httprequest.user_agent.platform
        record_ids_list = request.params.get('ids', '').split(',')
        record_ids = [int(id) for id in record_ids_list]
        result_ids = request.env['onesphere.tightening.result'].search([('id', 'in', record_ids)])
        if not result_ids:
            raise ValidationError(_('No Tightening Result Found!'))
        temp_file = get_temp_file_from_result(request.env, result_ids, platform)
        res = send_file(temp_file, mimetype="application/zip", filename='tightening_results.zip',
                        as_attachment=True)
        res.headers['Cache-Control'] = 'no-cache'
        return res
