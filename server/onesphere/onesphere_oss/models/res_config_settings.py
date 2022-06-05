# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.oneshare_utils.constants import ENV_OSS_BUCKET, ENV_OSS_ENDPOINT, ENV_OSS_ACCESS_KEY, \
    ENV_OSS_SECRET_KEY, ENV_OSS_SECURITY_TRANSPORT


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    oss_bucket_name = fields.Char(default=ENV_OSS_BUCKET,
                                  string='OSS Bucket Name',
                                  config_parameter='oss.bucket')

    oss_endpoint = fields.Char(default=ENV_OSS_ENDPOINT,
                               string='OSS Endpoint',
                               config_parameter='oss.endpoint')

    oss_access_key = fields.Char(default=ENV_OSS_ACCESS_KEY,
                                 string='OSS Access Key',
                                 config_parameter='oss.access_key')

    oss_secret_key = fields.Char(default=ENV_OSS_SECRET_KEY,
                                 string='OSS Secret Key',
                                 config_parameter='oss.secret_key')

    oss_security = fields.Char(default=ENV_OSS_SECURITY_TRANSPORT,
                               string='OSS Security Transport(SSL)',
                               config_parameter='oss.security')
