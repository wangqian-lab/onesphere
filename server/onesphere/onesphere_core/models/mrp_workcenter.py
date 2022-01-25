# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError
import logging
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    def download_work_process(self):
        """
            下发生产工艺工序
        """
        operation_obj = self.env['mrp.routing.workcenter']
        for work_center in self:
            need_download_operation_ids = operation_obj.search([('workcenter_id', '=', work_center.id)])
            if not need_download_operation_ids:
                continue
            # 执行下载工艺



    @api.model
    def default_get(self, fields):
        vals = super(MrpWorkcenter, self).default_get(fields)
        if 'resource_calendar_id' in fields:
            try:
                vals.update({
                    'resource_calendar_id': self.env.ref('onesphere_core.resource_calendar_std_140h',
                                                         raise_if_not_found=True).id
                })
            except Exception as e:
                _logger.error(ustr(e))
        return vals


    def get_workcenter_masterpc_http_connect(self):
        workcenter_id = self
        master_pcs = self.env['maintenance.equipment'].search(
            [('workcenter_id', '=', workcenter_id.id), ('category_name', '=', 'mpc')])
        return master_pcs