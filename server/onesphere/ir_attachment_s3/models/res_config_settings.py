# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019-2020 Eugene Molotov <https://it-projects.info/team/em230418>
import os

import boto3
from odoo.addons.oneshare_utils.constants import ENV_OSS_ENDPOINT, ENV_OSS_ACCESS_KEY, ENV_OSS_SECRET_KEY

from odoo import _, fields, models


class NotAllCredentialsGiven(Exception):
    pass


class S3Settings(models.TransientModel):
    _inherit = "res.config.settings"

    s3_bucket = fields.Char(string="S3 bucket name", help="i.e. 'attachmentbucket'", config_parameter="s3.bucket",
                            default='oneshare_attachments')
    s3_condition = fields.Char(
        string="S3 condition",
        config_paramter="s3.condition",
        help="""Specify valid odoo search domain here,
                               e.g. [('res_model', 'in', ['product.image'])] -- store data of product.image only.
                               Empty condition means all models""",
    )

    def _get_s3_settings(self, param_name, os_var_name):
        config_obj = self.env["ir.config_parameter"]
        res = config_obj.sudo().get_param(param_name)
        if not res:
            res = os.environ.get(os_var_name)
        return res

    def get_s3_obj_url(self, bucket, file_id):
        config_obj = self.env["ir.config_parameter"].sudo()
        s3_endpoint_url = config_obj.get_param("oss.endpoint", ENV_OSS_ENDPOINT)
        s3_bucket = config_obj.get_param("s3.bucket", 'oneshare_attachments')
        base_url = f'http://{s3_endpoint_url}/{s3_bucket}'
        if base_url:
            return base_url + file_id
        return "https://{}.s3.amazonaws.com/{}".format(bucket.name, file_id)

    def get_s3_bucket(self):
        config_obj = self.env["ir.config_parameter"].sudo()
        access_key_id = config_obj.get_param("oss.access_key", ENV_OSS_ACCESS_KEY)
        secret_key = config_obj.get_param("oss.secret_key", ENV_OSS_SECRET_KEY)
        endpoint_url = config_obj.get_param("oss.endpoint", ENV_OSS_ENDPOINT)
        bucket_name = config_obj.get_param("s3.bucket", 'oneshare_attachments')

        if not access_key_id or not secret_key or not bucket_name:
            raise NotAllCredentialsGiven(
                _("Amazon S3 credentials are not defined properly")
            )

        s3 = boto3.resource(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
            endpoint_url=f'http://{endpoint_url}',
        )
        bucket = s3.Bucket(bucket_name)

        return bucket

    def s3_upload_existing(self):
        self.env["ir.attachment"].force_storage_s3()
