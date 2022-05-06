# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import send_file, Controller, request
import tempfile
import logging
import binascii
import zipfile

_logger = logging.getLogger(__name__)


class OneshareTemplateDownloadController(Controller):

    def template_download_zip(self, temp_file, template_records):
        with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zfp:
            for template_record in template_records:
                template_obj = template_record.template_file
                file_name = f'{template_record.name}.xlsx'
                zfp.writestr(file_name, binascii.a2b_base64(template_obj))
        res = send_file(temp_file, mimetype="application/zip", filename='test.zip', as_attachment=True)
        return res

    def template_download_xlsx(self, temp_file, template_record):
        template_obj = template_record.template_file
        temp_file.write(binascii.a2b_base64(template_obj))
        file_name = f'{template_record.name}.xlsx'.encode('utf-8')
        res = send_file(temp_file, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=file_name, as_attachment=True)
        return res

    @http.route('/oneshare/template_download/<string:record_ids>', type='http', auth='user', cors='*',
                csrf=False,
                save_session=False)
    def template_download(self, record_ids):
        """
        Downloads the template excel
        """
        record_ids_list = record_ids[1:-1].split(',')
        template_records = request.env['onesphere.template.download'].search([('id', 'in', record_ids_list)])
        if not template_records:
            raise ValidationError(_('No template record!'))
        temp_file = tempfile.TemporaryFile()
        if len(template_records) > 1:
            res = self.template_download_zip(temp_file, template_records)
        else:
            res = self.template_download_xlsx(temp_file, template_records)
        res.headers['Cache-Control'] = 'no-cache'
        return res
