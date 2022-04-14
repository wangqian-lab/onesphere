# -*- coding: utf-8 -*-

from odoo import api, fields, models
import shutil, requests
from odoo.tools import mute_logger
# from odoo import http
import base64
from odoo.http import request

class TemplateDownload(models.Model):
    _name = "template.download"
    _description = "Provide Template to Download"

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    template_file = fields.Binary(string='Template File')

    def template_download(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f"http://localhost:8070/oneshare/template_download/{self.id}",
            'target': 'self',
        }
