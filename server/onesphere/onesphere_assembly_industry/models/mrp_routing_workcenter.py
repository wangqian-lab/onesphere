# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging, json
import http, os
import pprint
from odoo.exceptions import UserError, ValidationError
import requests as Requests
from requests import ConnectionError, RequestException
from odoo.addons.oneshare_utils.constants import ENV_MAX_WORKERS
from odoo.addons.onesphere_assembly_industry.constants import ALL_TIGHTENING_TEST_TYPE_LIST, MULTI_MEASURE_TYPE, \
    MEASURE_TYPE, MULTI_MEASURE_TYPE, PASS_FAIL_TYPE, MASTER_ROUTING_API
from distutils.util import strtobool
from odoo.addons.onesphere_assembly_industry.controllers.mrp_order_gateway import package_multi_measurement_items
from concurrent import futures
from odoo.tools import ustr
from lxml.html.soupparser import fromstring
from xml.etree import ElementTree

_logger = logging.getLogger(__name__)


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    code = fields.Char('Code', copy=False)
    oper_version = fields.Integer('Operation Version', default=1)
    workcenter_group_id = fields.Many2one('mrp.workcenter.group', string='Workcenter Group')
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        related='workcenter_group_id.onesphere_workcenter_ids',
        string='Work Center Set')
    max_op_time = fields.Integer('Max Operation time(second)',
                                 default=60)

    onesphere_bom_ids = fields.Many2many('mrp.bom', 'bom_operation_rel', 'onesphere_operation_id',
                                         'onesphere_bom_id',
                                         string='MRP Bom Operation Relationship')

    _sql_constraints = [('operation_code_unique', 'unique(code)', 'Code must be unique!')]

    def write(self, vals):
        ver = self.oper_version
        vals.update({"oper_version": ver + 1})
        return super(MrpRoutingWorkcenter, self).write(vals)

    def _create_update_val_record(self, equipment, success_flag):
        self.ensure_one()
        ver_model = self.env['real.oper.version'].sudo()
        ver_record = ver_model.search([('equipment_id', '=', equipment.id), ('operation_id', '=', self.id)])
        if not ver_record:
            # 未找到记录，需要新建
            if not success_flag:
                return
            val = {
                'equipment_id': equipment.id,
                'operation_id': self.id,
                'version': self.oper_version,
                'state': 'finish'
            }
            ver_model.create(val)
            return
        if success_flag:
            ver_record.update({
                'version': self.oper_version,
                'state': 'finish'
            })
        if not success_flag:
            if ver_record.version != self.oper_version:
                ver_record.update({
                    'state': 'todo'
                })

    def _get_masterpc_url(self, master_pcs):
        connect_list = []
        for master_pc in master_pcs:
            connections = master_pc.connection_ids.filtered(
                lambda r: r.protocol == 'http') if master_pc.connection_ids else None
            if not connections:
                info = _(f"Can Not Found Connect Info For MasterPC:{master_pc.name}")
                self.env.user.notify_info(info)
                _logger.error(info)
                continue
            else:
                connect_list += connections
        masterpc_url = [f'http://{connect.ip}:{connect.port}{MASTER_ROUTING_API}' for connect in connect_list]
        return masterpc_url

    @staticmethod
    def _pack_points_val(tightening_step_id):
        # 拧紧点数据打包
        _points = []
        operation_point_ids = tightening_step_id.tightening_opr_point_ids
        for point in operation_point_ids:
            _points.append({
                'sequence': point.sequence,
                'is_key': point.is_key,
                'key_num': point.group_id.key_num if point.group_id else 1,
                'group_sequence': point.group_sequence,
                'x': point.x_offset,
                'y': point.y_offset,
                'max_redo_times': point.max_attempt_times,
                'controller_sn': point.tightening_units.mapped('serial_no') if point.tightening_units else [],
                'tightening_unit': point.tightening_units.mapped('ref') if point.tightening_units else [],
                # 'tool_sn': point.tightening_tool_ids.tightening_tool_id.mapped('serial_no') or [],
                'pset': point.tightening_pet,
                'nut_no': point.product_id.name if point.product_id else '',  # 螺栓编号为拧紧点上的名称
                'tightening_point_name': point.name,
            })

        return _points

    def replace_text_img(self, val):
        text = val.get('text')
        if not text:
            return
        tree = fromstring(text)
        ts = tree.xpath('//img')
        for t in ts:
            src = t.get('src')
            if not src or src == 'undefined':
                continue
            src_content = src.split('/')
            xml_id = src_content[-2].split('-')[0]
            fn = src_content[-1].split('?')[0]
            status, headers, content = self.env["ir.http"].binary_content(id=int(xml_id), filename=fn,
                                                                          default_mimetype='image/png')
            if not content:
                continue
            t.set('src', u'data:{0};base64,{1}'.format('image/png', content.decode()))
        tt = ElementTree.tostring(tree, encoding='utf-8').decode()
        val.update({'text': tt})

    def _pack_step_val(self, step_id):
        step_val = {
            "title": step_id.name or '',  # 名称或者QCP
            "code": step_id.code or '',  # 通过下发的ref去进行定位查找，这里可能出现上层业务系统的k值，报工需要传递的是这个代码
            "desc": step_id.note or '',  # 工步指令字段
            "tag": step_id.tag_ids.mapped('name') if step_id.tag_ids else [],
            "skippable": step_id.can_do_skip,
            "undoable": step_id.can_do_rework,
            "test_type": step_id.test_type_id.technical_name or '',
            "consume_product": step_id.component_id.default_code or step_id.component_id.barcode or '',
            "text": step_id.reason or '',  # 备注字段
            "time_limit": step_id.time_limit * 1000,
            "barcode_rule": step_id.barcode_rule or '',
        }
        # 测量工步增加测量项内容，拧紧工步增加拧紧点内容
        self.replace_text_img(step_val)
        if step_id.test_type in [MEASURE_TYPE, MULTI_MEASURE_TYPE]:
            measure_items_data = package_multi_measurement_items(step_id.multi_measurement_ids)
            step_val.update({'measurement_items': measure_items_data})  # 将测量项
            step_val.update({'measurement_total': len(step_id.multi_measurement_ids)})
        elif step_id.test_type in ALL_TIGHTENING_TEST_TYPE_LIST:
            points_data = self._pack_points_val(step_id)
            step_val.update({
                'points': points_data,
                "img": u'data:{0};base64,{1}'.format('image/png',
                                                     step_id.worksheet_img.decode()) if step_id.worksheet_img else ""
            })
        else:
            pass

        return step_val

    def _pack_operation_val(self, bom_id, operation_id):
        # 生成作业对应数据
        operation_val = {
            "workcenter_id": operation_id.workcenter_id.id,
            "max_op_time": operation_id.max_op_time,
            "name": f"[{operation_id.name}]@{operation_id.workcenter_id.name}",
            "product_id": bom_id.product_tmpl_id.id if bom_id else 0,
            "product_type": bom_id.product_tmpl_id.default_code if bom_id else "",
            "workcenter_code": operation_id.workcenter_id.code if operation_id.workcenter_id else "",
            'product_type_image': u'data:{0};base64,{1}'.format('image/png',
                                                                bom_id.product_tmpl_id.image_1920.decode()) if bom_id.product_tmpl_id.image_1920 else "",
            "steps": [],
        }
        # 查看配置中是否下发所有工步数据，是则遍历所有工步，否则只遍历拧紧工步
        config = self.env['ir.config_parameter']
        all_step_flag = config.get_param('oneshare.send.all.steps')
        all_need_steps = operation_id.work_step_ids.mapped('work_step_id')
        if not all_step_flag:
            all_need_steps = all_need_steps.filtered(
                lambda step: step and (step.test_type in ALL_TIGHTENING_TEST_TYPE_LIST))
        # 生成工步数据
        steps_data = []
        for step_id in all_need_steps:
            step_val = self._pack_step_val(step_id)
            steps_data.append(step_val)

        operation_val.update({
            "steps": steps_data
        })
        return operation_val

    def _send_operation_val(self, operation_val_list, url_list):
        # 发送数据
        with futures.ThreadPoolExecutor(max_workers=ENV_MAX_WORKERS) as executor:
            task_list = [executor.submit(self._send_val_by_thread, *args) for args in zip(operation_val_list, url_list)]
        for task in task_list:
            task_exception = task.exception()
            if task_exception:
                self.env.user.notify_warning(_(f'Push Operation Failure, Error Message:{ustr(task_exception)}'))
                continue
            ret = task.result()
            if ret.status_code == http.HTTPStatus.OK:
                self.env.user.notify_info(_('Push Operation Successfully!'))
            else:
                self.env.user.notify_warning(_(f'Push Operation Failure, Error Message:{ret.text}'))

    def _send_val_by_thread(self, val, url):
        # 异步发送包好的数据
        _logger.debug("Push Operation： {}".format(pprint.pformat(val, indent=4)))
        ret = Requests.put(url, data=json.dumps(val), headers={'Content-Type': 'application/json'},
                           timeout=60)
        return ret

    def _push_mrp_routing_workcenter(self, url_list):
        # 推送作业数据
        self.ensure_one()
        operation_id = self
        bom_id = self.env.context.get('bom_id')
        if bom_id:
            bom_ids = bom_id
        else:
            bom_ids = self.env['mrp.bom'].search([('onesphere_bom_operation_ids', '=', operation_id.id)])
        if not bom_ids:
            msg = _(f"Can Not Found MRP BOM Within The Operation:{operation_id.name}")
            _logger.error(msg)
            raise ValidationError(msg)

        rel_operation_val_list = []
        rel_url_list = []
        for bom_id in bom_ids:
            operation_val_list = []
            operation_val = self._pack_operation_val(bom_id, operation_id)
            operation_val_list.append(operation_val)
            rel_operation_val_list += operation_val_list * len(url_list)  # 有几个url就发几次
            rel_url_list += url_list

        self._send_operation_val(rel_operation_val_list, rel_url_list)

    def button_send_mrp_routing_workcenter(self):
        operation = self
        if not operation.workcenter_id:
            self.env.user.notify_info(_('Can Not Found Workcenter!'))
            return
        try:
            url_list = []
            for workcenter_id in operation.workcenter_ids or operation.workcenter_id:
                master_pcs = workcenter_id.get_workcenter_masterpc()
                if not master_pcs:
                    info = _(f'Can Not Found MasterPC For Work Center:{workcenter_id.name}!')
                    self.env.user.notify_info(info)
                    _logger.error(info)
                    continue
                masterpc_url = self._get_masterpc_url(master_pcs)
                url_list += masterpc_url
            self._push_mrp_routing_workcenter(url_list)
        except Exception as e:
            self.env.user.notify_warning(_(f'Sync Operation Failure:{ustr(e)}'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """ copy(default=None)

        Duplicate record ``self`` updating it with default values

        :param dict default: dictionary of field values to override in the
               original values of the copied record, e.g: ``{'field_name': overridden_value, ...}``
        :returns: new record

        """
        new = super(MrpRoutingWorkcenter, self).copy(default=default)
        for work_step in self.work_step_ids:
            operation_step_rel_dic = {
                'operation_id': new.id,
                'work_step_id': work_step.work_step_id.id,
                'sequence': work_step.sequence,
            }
            self.env['onesphere.mrp.operation.step.rel'].create(operation_step_rel_dic)
        return new
