# -*- coding: utf-8 -*-
import logging

from odoo import api, SUPERUSER_ID
from odoo.tools import ustr
from . import models
from . import tests

_logger = logging.getLogger(__name__)


def _ir_attachment_s3_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ICP = env['ir.config_parameter']
    oss_interface = env['onesphere.oss.interface']
    bucket_name = ICP.get_param('s3.bucket', 'oneshare-attachments')
    try:
        oss_interface.create_bucket(bucket_name=bucket_name, public=True)
    except Exception as e:
        _logger.error(ustr(e))
