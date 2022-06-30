# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import ustr
import logging

_logger = logging.getLogger(__name__)


class OnesphereTemplateDownload(models.Model):
    _name = "onesphere.template.download"
    _description = "Provide Template to Download"

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
    template_file = fields.Binary(string='Template File', attachment=True, required=True)
    help_info = fields.Html(string='Help Info')

    def template_download(self):
        try:
            record_ids = ','.join([str(id) for id in self.ids])
        except Exception as e:
            _logger.error(ustr(e))
            raise e
        return {
            'type': 'ir.actions.act_url',
            'url': f"/oneshare/template_download?ids={record_ids}",
            'target': 'self',
        }
