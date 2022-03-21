# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools import ustr
import json, itertools
from boltons.cacheutils import LRU
import logging

_wave_cache = LRU(max_size=128)

logger = logging.getLogger(__name__)


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

    def _get_curve_data(self, data):
        bucket_name = self.env['ir.config_parameter'].get_param('oss.bucket')
        client = self.env['onesphere.oss.interface'].ensure_oss_client()
        if not client or not bucket_name:
            return [], None, []  ### 返回无结果数值
        cur_objects = data.mapped('curve_file')
        _objects = [x for x in cur_objects if x]
        objects = []
        cur_objects = map(json.loads, _objects)
        objs = list(itertools.chain.from_iterable(cur_objects))
        for cur in objs:
            objects.append(cur['file'])

        need_fetch_objects = []
        _datas = []
        for _t in objects:
            try:
                # try to get the cache
                _datas.append(_wave_cache[_t])
            except KeyError as e:
                need_fetch_objects.append(_t)
        try:
            _datas.extend(
                map(lambda x: _create_wave_result_dict(x, client.get_object(bucket_name, x).data.decode('utf-8')),
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
            return None, None
        datas = self._get_curve_data(self)
        if not len(datas):
            self.env.user.notify_warning(u'查询获取结果:0,请重新定义查询参数或等待新结果数据')
            return None, None
        curves = json.dumps(datas)
        wave_wizard_id = self.env['wave.compose.wave'].sudo().create({'wave': curves})
        if not wave_wizard_id:
            return None, None

        return wave_form.id, wave_wizard_id.id
