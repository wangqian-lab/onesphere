# -*- coding: utf-8 -*-

import logging
import os

from odoo import fields, models

_logger = logging.getLogger(__name__)

ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT = int(
    os.getenv("ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT", "1000")
)
ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE = os.getenv(
    "ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE", "utf-8"
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    download_tightening_results_limit = fields.Integer(
        string="Download Tightening Result Records Limit",
        config_parameter="onesphere_wave.download_tightening_results_limit",
        default=ENV_DOWNLOAD_TIGHTENING_RESULT_LIMIT,
    )

    download_tightening_results_encode = fields.Char(
        string="Download Tightening Result Records Encode",
        config_parameter="onesphere_wave.download_tightening_results_encode",
        default=ENV_DOWNLOAD_TIGHTENING_RESULT_ENCODE,
    )
