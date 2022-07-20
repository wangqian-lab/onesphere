# -*- coding: utf-8 -*-
import os

from odoo import fields, models, api, _
from odoo.tools import ustr
import json
import itertools
from boltons.cacheutils import LRU
import logging

_wave_cache = LRU(max_size=128)

logger = logging.getLogger(__name__)

ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT = int(os.getenv('ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT', '1000'))


def _create_wave_result_dict(x, data):
    _data = json.loads(data)
    _data['name'] = x.split('.')[0]
    _wave_cache[x] = _data  # 将其加入缓存

    return _data


try:
    from odoo.models import OneshareHyperModel as HModel
except ImportError:
    from odoo.models import Model as HModel


class OperationResult(HModel):
    _inherit = "onesphere.tightening.result"

    def download_tightening_results(self):
        records = self
        ICP = self.env['ir.config_parameter'].sudo()
        download_tightening_results_limit = int(ICP.get_param("onesphere_wave.download_tightening_results_limit",
                                                              default=ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT))
        if len(self) > download_tightening_results_limit:
            self.env.user.notify_warning(
                f'曲线导出功能限制前{download_tightening_results_limit}条数据，将自动截取.或通过设置放大onesphere_wave.download_tightening_results_limit参数')
            records = self[:download_tightening_results_limit]
        _ids = ','.join([str(_id) for _id in records.ids])
        return {
            'type': 'ir.actions.act_url',
            'url': f'/oneshare/assembly/tightening/download?ids={_ids}',
            'target': 'self',
        }

    def _get_curve_data(self):
        bucket_name = self.env['ir.config_parameter'].get_param('oss.bucket')
        oss_interface = self.env['onesphere.oss.interface']
        client = oss_interface.ensure_oss_client()
        if not client or not bucket_name:
            return [], None, []  ### 返回无结果数值
        cur_objects = self.mapped('curve_file')
        _objects = [x for x in cur_objects if x]
        objects = []
        cur_objects = map(json.loads, _objects)
        objs = list(itertools.chain.from_iterable(cur_objects))
        for cur in objs:
            objects.append(cur['file'])

        need_fetch_objects = []
        _datas = []
        for _cur_file in objects:
            try:
                # 尝试从LRU cache中获取数据
                _datas.append(_wave_cache[_cur_file])
            except KeyError as e:
                need_fetch_objects.append(_cur_file)
        try:
            _datas.extend(
                map(lambda x: _create_wave_result_dict(x, oss_interface.get_oss_object(bucket_name, x).decode('utf-8')),
                    need_fetch_objects))  # 合并结果
        except Exception as e:
            logger.error(f'Error: {ustr(e)}')
            return [], None, []
        return _datas

    def show_curves(self):
        if not len(self):
            self.env.user.notify_warning(u'查询获取结果:0,请重新定义查询参数或等待新结果数据')
            return None, None
        wave_form = self.env.ref('onesphere_wave.spc_compose_wave_wizard_form')
        if not wave_form:
            self.env.user.notify_warning(u'曲线视图:onesphere_wave.spc_compose_wave_wizard_form 未找到')
            return None, None
        curve_datas = self._get_curve_data()
        if not len(curve_datas):
            self.env.user.notify_warning(
                _('Query Result Data:0,Please Redefine Parameter Of Query or Wait For New Result'))
            return None, None
        curves = json.dumps(curve_datas)
        wave_wizard_id = self.env['wave.compose.wave'].sudo().create({'wave': curves})
        if not wave_wizard_id:
            self.env.user.notify_warning(u'曲线Wizard视图:wave.compose.wave未找到')
            return None, None
        return wave_form.id, wave_wizard_id.id
