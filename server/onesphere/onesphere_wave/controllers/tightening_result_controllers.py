# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import uuid
import zipfile

import pandas as pd

from odoo import http, _
# import csv
from odoo.exceptions import ValidationError
from odoo.http import request, send_file
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE = os.getenv('ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE', 'utf-8')


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
        result_list = []
        for result in result_ids:
            control_time = (result.control_time + (timedelta(hours=8))).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if result.control_time else ''
            ret = {'追溯码': result.track_no,
                   '工位': result.workcenter_code,
                   '工具序列号': result.attribute_equipment_no,
                   '螺栓名称': result.tightening_point_name.name if result.tightening_point_name else '',
                   '拧紧策略': result.tightening_strategy,
                   '拧紧结果': result.tightening_result,
                   '拧紧最终扭矩': result.measurement_final_torque,
                   '拧紧最终角度': result.measurement_final_angle,
                   '拧紧时间': control_time,
                   '拧紧人员': result.user_list}
            result_list.append(ret)
        df = pd.DataFrame.from_records(result_list)
        temp_file = tempfile.TemporaryFile()
        ICP = request.env['ir.config_parameter'].sudo()
        download_tightening_results_encode = ICP.get_param(
            "onesphere_wave.download_tightening_results_encode",
            default=ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE)
        if platform.upper() == 'WINDOWS':
            download_tightening_results_encode = 'gbk'  # GBK
        with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zfp:
            with zfp.open('tightening_results.xlsx', mode="w") as xlsx_f:
                df.to_excel(xlsx_f, sheet_name=u'拧紧结果', freeze_panes=(1, 0),
                            encoding=download_tightening_results_encode)
            curve_datas = result_ids._get_curve_data()
            for curve_dict in curve_datas:
                fn = curve_dict.pop('name') or ''
                if not fn:
                    fn = uuid.uuid4().hex
                    _logger.error(f'获取曲线名称失败, 重命名为{fn}.csv')
                with zfp.open(f'{fn}.csv', mode="w") as f:
                    df = pd.DataFrame.from_dict(curve_dict)
                    ret = df.to_csv(path_or_buf=None, index=False, columns=['cur_m', 'cur_w', 'cur_t'],
                                    header=['扭矩', '角度', '时间'])
                    f.write(ret.encode(download_tightening_results_encode))
        temp_file.seek(0)
        res = send_file(temp_file, mimetype="application/zip", filename='tightening_results.zip',
                        as_attachment=True)
        res.headers['Cache-Control'] = 'no-cache'
        return res
