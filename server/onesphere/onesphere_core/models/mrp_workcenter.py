# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError
import logging
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

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
