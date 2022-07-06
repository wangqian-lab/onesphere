# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError
import logging
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    def _do_download_operations(self, operations):
        self.ensure_one()
        master_pcs = self.get_workcenter_masterpc()
        if not master_pcs:
            info = _(f'Can Not Found MasterPC For Work Center:{self.name}!')
            self.env.user.notify_info(info)
            _logger.error(info)
        for operation in operations:
            masterpc_url = operation._get_masterpc_url(master_pcs)
            operation._push_mrp_routing_workcenter(masterpc_url)

    def download_work_process(self):
        """
            下发生产工艺工序
        """
        operation_obj = self.env['mrp.routing.workcenter']
        for work_center in self:
            need_download_operation_ids = operation_obj.search([('workcenter_id', '=', work_center.id)])
            if not need_download_operation_ids:
                continue
            try:
                work_center._do_download_operations(need_download_operation_ids)
            except Exception as e:
                self.env.user.notify_warning(_(f'Sync Operation Failure:{ustr(e)}'))

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

    def get_workcenter_masterpc(self):
        workcenter_id = self
        master_pcs = self.env['maintenance.equipment'].search(
            [('workcenter_id', '=', workcenter_id.id), ('category_name', '=', 'mpc')])
        return master_pcs
