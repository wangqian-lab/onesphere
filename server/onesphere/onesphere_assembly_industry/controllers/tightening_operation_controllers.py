# -*- coding: utf-8 -*-
from odoo import http, api, SUPERUSER_ID
from odoo.http import request
from odoo.addons.oneshare_utils.http import oneshare_json_success_resp, oneshare_json_fail_response
import logging
import pprint
import uuid

_logger = logging.getLogger(__name__)

api_edit_tightening_opr_points_item = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "sequence": {
                "type": "integer"  # 序列
            },
            "x_offset": {
                "type": "number"  # x轴的位置
            },
            "y_offset": {
                "type": "number"  # y轴的位置
            }
        },
        "required": [
            "sequence",
            "x_offset",
            "y_offset"
        ]
    }
}


class OnesphereAssemablyIndustry(http.Controller):
    @http.api_route('/api/v1/tightening_work_step/<int:tightening_work_step_id>/opr_points_edit', type='apijson',
                    methods=['PUT', 'OPTIONS'], auth='user', cors='*', csrf=False,
                    schema=api_edit_tightening_opr_points_item)
    def _edit_tightening_opr_points(self, tightening_work_step_id=None):
        cr = request.cr
        env = api.Environment(request.cr, SUPERUSER_ID, request.context)
        tightening_opr_point_obj = env['onesphere.tightening.opr.point']
        tightening_work_step = env['oneshare.quality.point'].browse(tightening_work_step_id)

        body_tightening_points = request.ApiJsonRequest or []
        if not tightening_work_step:
            return oneshare_json_fail_response(msg="Tightening Work Step： %d not existed" % tightening_work_step_id, )

        current_points = tightening_opr_point_obj.search(
            [('parent_quality_point_id', '=', tightening_work_step_id)])
        points_map = {i.id: i for i in current_points}

        for val in body_tightening_points:
            sequence = val.get('sequence')
            point_id = tightening_opr_point_obj.search([('parent_quality_point_id', '=', tightening_work_step_id),
                                                        ('sequence', '=', sequence)])

            if tightening_work_step.test_type == 'promiscuous_tightening' and getattr(tightening_work_step,
                                                                                      'tightening_tool_ids',
                                                                                      None):
                # 混杂默认默认取得原来的工步上定义的拧紧工具
                val.update({'tightening_tool_ids': [(6, 0, tightening_work_step.tightening_tool_ids.ids)]})
            val.update({
                'x_offset': val['x_offset'],
                'y_offset': val['y_offset'],
            })
            if not point_id:
                # 新增
                val.update({
                    'name': str(uuid.uuid4()),
                    'parent_quality_point_id': tightening_work_step_id,
                    'sequence': sequence,
                    'product_id': env.ref('onesphere_assembly_industry.product_product_screw_default').id  # 获取默认螺栓
                })

                ret = tightening_opr_point_obj.create(val)
                tightening_work_step.update_points_group_sequence()
                if not ret:
                    _logger.error(
                        "Create Tightening Operation Point Fail, Vals: {0}".format(pprint.pformat(val, indent=4)))
            else:
                # 更新
                ret = point_id.write(val)
                if not ret:
                    _logger.error(
                        u'Update Tightening Operation Point Fail, vals: {0}'.format(pprint.pformat(val, indent=4)))
                if point_id.id in points_map:
                    del points_map[point_id.id]

        need_delete_points = env['onesphere.tightening.opr.point']
        for p in points_map.values():
            need_delete_points += p

        ret = need_delete_points.unlink()
        if not ret and need_delete_points:
            _logger.error(
                "Delete Tightening Operation Point Fail, Points: {0}".format(
                    pprint.pformat(need_delete_points, indent=4)))
        cr.commit()  # 强制提交
        return oneshare_json_success_resp(msg="Edit point success")
