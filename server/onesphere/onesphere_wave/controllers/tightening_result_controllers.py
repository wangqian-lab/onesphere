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
from odoo.addons.onesphere_wave.constants import OK_BG_COLOR, OK_COLOR, NOK_BG_COLOR, NOK_COLOR, OTHER_BG_COLOR

_logger = logging.getLogger(__name__)
ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE = os.getenv('ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE', 'utf-8')


def style_apply(v):
    if v.upper() == 'OK':
        bg_color, color = OK_BG_COLOR, OK_COLOR
    elif v.upper() == 'NOK':
        bg_color, color = NOK_BG_COLOR, NOK_COLOR
    else:
        return f'background-color: {OTHER_BG_COLOR}'
    return f'background-color: {bg_color}; color: {color}'


def get_temp_file_from_result(env, result_ids, platform=''):
    ICP = env['ir.config_parameter']
    download_tightening_results_encode = ICP.get_param(
        "onesphere_wave.download_tightening_results_encode",
        default=ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE)
    if platform and platform.upper() == 'WINDOWS':
        download_tightening_results_encode = 'gbk'  # GBK
    result_list, curve_file_list, entity_id_list = [], [], []
    for result in result_ids:
        control_time = (result.control_time + (timedelta(hours=8))).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT) if result.control_time else ''
        work_mode = WORK_MODE_DIC.get(result.work_mode, '')
        ret = {'追溯码': result.track_no or '',
               '工位': result.workcenter_code or '',
               '工作模式': work_mode,
               '工具序列号': result.attribute_equipment_no or '',
               '程序号': result.tightening_process_no or '',
               '螺栓名称': result.tightening_point_name.name if result.tightening_point_name else '',
               '曲线ID': result.entity_id or '',
               '拧紧策略': result.tightening_strategy or '',
               '拧紧结果': result.tightening_result or '',
               '拧紧最终扭矩': result.measurement_final_torque or '',
               '拧紧最终角度': result.measurement_final_angle or '',
               '拧紧时间': control_time,
               '拧紧人员': result.user_list or ''}
        result_list.append(ret)
        curve_file_list.append(json.loads(result.curve_file)[0].get('file') if result.curve_file else '')
        entity_id_list.append(result.entity_id or '')
    df = pd.DataFrame.from_records(result_list)
    df_style = df.style.applymap(style_apply, subset="拧紧结果")
    temp_file = tempfile.TemporaryFile()
    bucket_name = ICP.get_param('oss.bucket')
    oss_interface = env['onesphere.oss.interface']
    with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zfp:
        with zfp.open('tightening_results.xlsx', mode="w") as xlsx_f:
            writer = pd.ExcelWriter(xlsx_f)
            df_style.to_excel(writer, sheet_name=u'拧紧结果', freeze_panes=(1, 0),
                              encoding=download_tightening_results_encode)
            writer.save()
        curve_datas = oss_interface.get_oss_objects(bucket_name, curve_file_list, entity_id_list)
        for entity_id, curve in curve_datas.items():
            if not curve:
                continue
            with zfp.open(f'{entity_id}.csv', mode="w") as f:
                df = pd.DataFrame.from_dict(json.loads(curve))
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
