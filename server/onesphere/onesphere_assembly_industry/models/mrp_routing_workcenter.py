# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
import logging, json
import http, os
import pprint
from odoo.exceptions import UserError, ValidationError
import requests as Requests
from requests import ConnectionError, RequestException
from odoo.addons.onesphere_assembly_industry.constants import ALL_TIGHTENING_TEST_TYPE_LIST, MULTI_MEASURE_TYPE, \
    MEASURE_TYPE, MULTI_MEASURE_TYPE, PASS_FAIL_TYPE, MASTER_ROUTING_API
from distutils.util import strtobool
from odoo.addons.onesphere_assembly_industry.controllers.mrp_order_gateway import package_multi_measurement_items, \
    package_multi_measure_4_measure_step

_logger = logging.getLogger(__name__)



# ENV_MEAS_STEP_DOWNLOAD_ENABLE = strtobool(os.getenv('ENV_MEAS_STEP_DOWNLOAD_ENABLE', 'false'))
# ENV_PROJECT_CODE = os.getenv('ENV_PROJECT_CODE', '')
# if ENV_PROJECT_CODE == 'ts031':
#     ENV_MEAS_STEP_DOWNLOAD_ENABLE = True


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    oper_version = fields.Integer('Oper Version', default=1)
    workcenter_group_id = fields.Many2one('mrp.workcenter.group', string='Workcenter Group')
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        related='workcenter_group_id.onesphere_workcenter_ids',
        string='Work Center Set')
    max_op_time = fields.Integer('Max Operation time(second)',
                                 default=60)

    def write(self, vals):
        ver = self.oper_version
        vals.update({"oper_version": ver + 1})
        return super(MrpRoutingWorkcenter, self).write(vals)

    def _create_update_val_record(self, equipment, success_flag):
        self.ensure_one()
        ver_model = self.env['real.oper.version'].sudo()
        ver_record = ver_model.search([('equipment_id', '=', equipment.id), ('operation_id', '=', self.id)])
        if ver_record and success_flag:
            ver_record.update({
                'version': self.oper_version,
                'state': 'finish'
            })
        elif ver_record and not success_flag:
            if ver_record.version != self.oper_version:
                ver_record.update({
                    'state': 'todo'
                })
        elif not ver_record and success_flag:
            val = {
                'equipment_id': equipment.id,
                'operation_id': self.id,
                'version': self.oper_version,
                'state': 'finish'
            }
            ver_model.create(val)
        else:
            pass

    def _push_operation_to_mpcs(self, master_pcs):
        for master_pc in master_pcs:
            try:
                connections = master_pc.connection_ids.filtered(
                    lambda r: r.protocol == 'http') if master_pc.connection_ids else None
                if not connections:
                    info = "Can Not Found Connect Info For MasterPC:{0}".format(master_pc.name)
                    self.env.user.notify_info(info)
                    _logger.error(info)
                    continue
                for connect in connections:
                    url = f'http://{connect.ip}:{connect.port}{MASTER_ROUTING_API}'
                    self._push_mrp_routing_workcenter(url)
                    self._create_update_val_record(master_pc, success_flag=True)
            except Exception as e:
                self._create_update_val_record(master_pc, success_flag=False)
                raise ValidationError(e)

    def _pack_points_val(self, tightening_step_id):
        # 拧紧点数据打包
        _points = []
        operation_point_ids = tightening_step_id.tightening_opr_point_ids
        for point in operation_point_ids:
            _points.append({
                'sequence': point.sequence,
                'group_sequence': point.group_sequence,
                'offset_x': point.x_offset,
                'offset_y': point.y_offset,
                'max_redo_times': point.max_attempt_times,
                'tool_sn': point.tightening_tool_ids.tightening_tool_id.mapped('serial_no') or [],  # 默认模式下这里传送的枪的序列号是空字符串
                'controller_sn': '',
                'pset': point.tightening_pet,
                'consu_product_id': point.product_id.id if point.product_id.id else 0,
                'nut_no': point.name,  # 螺栓编号为拧紧点上的名称
            })

        return _points

    def _pack_operation_val(self, bom_id, operation_id):
        # 生成作业对应数据
        val = {
            'tightening_step_ref': "",
            'tightening_step_name': "",
            "workcenter_id": operation_id.workcenter_id.id,
            # "job": int(operation_id.op_job_id.code) if operation_id.op_job_id else 0,
            "job": 0,
            "max_op_time": operation_id.max_op_time,
            "name": u"[{0}]@{1}".format(operation_id.name, operation_id.workcenter_id.name),
            # operation_id.routing_id.name),
            "img": "",
            "product_id": bom_id.product_tmpl_id.id if bom_id else 0,
            "product_type": bom_id.product_tmpl_id.default_code if bom_id else "",
            "workcenter_code": operation_id.workcenter_id.code if operation_id.workcenter_id else "",
            'product_type_image': u'data:{0};base64,{1}'.format('image/png',
                                                                bom_id.product_tmpl_id.image_1920) if bom_id.product_tmpl_id.image_1920 else "",
            "points": [],
            "steps": [],
        }

        return val

    def _pack_measure_step_val(self, step_id):
        # 测量工步生成step数据
        # payloads = []
        # for idx, measurement_step_id in enumerate(measurement_step_ids):
            # if not ENV_MEAS_STEP_DOWNLOAD_ENABLE or not measurement_step_id.can_download:
            #     continue
        ts = {
            "title": step_id.name or '',  # 这里只会是QCP代码
            "code": step_id.code or '',  # 通过下发的ref去进行定位查找，这里可能出现上层业务系统的k值，报工需要传递的是这个代码
            "desc": step_id.note or '',  # 工步指令字段
            # "failure_msg": step_id.failure_message or '',
            # "sequence": idx + 1,
            "skippable": step_id.can_do_skip,
            # "skippable": True,
            "undoable": step_id.can_do_rework,
            "test_type": step_id.test_type_id.technical_name or '',
            "consume_product": step_id.component_id.default_code or step_id.component_id.barcode or '',
            "text": step_id.reason or '',  # 备注字段
            "tolerance_min": step_id.tolerance_min,
            "tolerance_max": step_id.tolerance_max,
            "target": step_id.norm,
            "uom": step_id.norm_unit or '',  # 测量工步的标准值
        }
        if step_id.test_type in [MEASURE_TYPE, MULTI_MEASURE_TYPE]:
            p = package_multi_measurement_items(step_id.multi_measurement_ids)
            ts.update({'measurement_items': p})  # 将测量项
            ts.update({'measurement_total': len(step_id.multi_measurement_ids)})
            # if measurement_step_id.test_type == PASS_FAIL_TYPE:
            #     v = package_multi_measure_4_measure_step(measurement_step_id)
            #     p = package_multi_measurement_items([v])
            #     ts.update({'measurement_items': p})  # 将测量项
            #     ts.update({'measurement_total': 1})
            # payloads.append(ts)

        return ts

    def _send_operation_val(self, val, url):
        # 发送包好的数据
        try:
            _logger.debug("Push Operation： {}".format(pprint.pformat(val, indent=4)))
            ret = Requests.put(url, data=json.dumps(val), headers={'Content-Type': 'application/json'},
                               timeout=60)
            if ret.status_code == http.HTTPStatus.OK:
                self.env.user.notify_info('Push Operation Successfully!')
        except ConnectionError as e:
            self.env.user.notify_warning('Push Operation Failure, Error Message:{0}'.format(e))
        except RequestException as e:
            self.env.user.notify_warning('Push Operation Failure, Error Message:{0}'.format(e))

    def button_send_mrp_routing_workcenter(self):
        operation = self
        if not operation.workcenter_ids:
            self.env.user.notify_info('Can Not Found Workcenter!')
            return
        for workcenter_id in operation.workcenter_ids:
            try:
                master_pcs = workcenter_id.get_workcenter_masterpc()
                if not master_pcs:
                    info = 'Can Not Found MasterPC For Work Center:{0}!'.format(workcenter_id.name)
                    self.env.user.notify_info(info)
                    _logger.error(info)
                    continue
                self._push_operation_to_mpcs(master_pcs)
            except Exception as e:
                self.env.user.notify_warning(u'Sync Operation Failure:{0}'.format(str(e)))

    def _push_mrp_routing_workcenter(self, url):
        self.ensure_one()
        config = self.env['ir.config_parameter']
        all_step_flag = config.get_param('oneshare.send.all.steps')
        operation_id = self
        bom_id = self.env.context.get('bom_id')
        if bom_id:
            bom_ids = bom_id
        else:
            bom_ids = self.env['mrp.bom'].search([('bom_oper_rel', '=', operation_id.id)])
        if not bom_ids:
            _logger.debug("_push_mrp_routing_workcenter, BOM:{0}".format(pprint.pformat(bom_ids.ids, indent=4)))
            msg = "Can Not Found MRP BOM Within The Operation:{0}".format(operation_id.name)
            _logger.error(msg)
            raise ValidationError(msg)

        for bom_id in bom_ids:
            # step_id = step_rel.
            for step_id in operation_id.work_step_ids.mapped('work_step_id'):
                val = self._pack_operation_val(bom_id, operation_id)
                if step_id.test_type in ALL_TIGHTENING_TEST_TYPE_LIST:
                    _points = []
                    _points = self._pack_points_val(step_id)
                    val.update({
                        'tightening_step_ref': step_id.code,
                        'tightening_step_name': step_id.name,
                        "points": _points,
                        "img": u'data:{0};base64,{1}'.format('image/png',
                                                             step_id.worksheet_img) if step_id.worksheet_img else "",
                    })

                elif all_step_flag:
                    payloads = self._pack_measure_step_val(step_id)
                    val.update({'steps': payloads})
                else:
                    pass

                self._send_operation_val(val, url)
