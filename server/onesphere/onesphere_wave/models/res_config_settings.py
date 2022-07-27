# -*- coding: utf-8 -*-

import os
import logging
from odoo.tools import ustr
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT = int(os.getenv('ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT', '1000'))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    download_tightening_results_limit = fields.Integer(string='Download Tightening Result Records Limit',
                                                       config_parameter='onesphere_wave.download_tightening_results_limit',
                                                       default=ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT)
