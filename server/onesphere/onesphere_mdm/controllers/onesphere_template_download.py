# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import send_file, Controller, request
import tempfile
import logging
import binascii
import zipfile
import mimetypes

_logger = logging.getLogger(__name__)


class OneshareTemplateDownloadController(Controller):

    def _get_attachment_type(self, template_record):
        attachment_record = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'onesphere.template.download'),
             ('res_field', '=', 'template_file'),  # 必须带res_field字段
             ('res_id', 'in', template_record.ids)])
        if not attachment_record:
            raise ValidationError(_(f'Can not find attachment! record id is {template_record.id}'))
        mimetype = attachment_record.mimetype
        file_extension = mimetypes.guess_extension(mimetype)
        return mimetype, file_extension

    def multi_template_download(self, temp_file, template_records):
        with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED) as zfp:
            for template_record in template_records:
                template_obj = template_record.template_file
                mimetype, file_extension = self._get_attachment_type(template_record)
                file_name = f'{template_record.name}{file_extension}'
                zfp.writestr(file_name, binascii.a2b_base64(template_obj))
        res = send_file(temp_file, mimetype="application/zip", filename='templates.zip', as_attachment=True)
        return res

    def single_template_download(self, temp_file, template_record):
        template_obj = template_record.template_file
        temp_file.write(binascii.a2b_base64(template_obj))
        mimetype, file_extension = self._get_attachment_type(template_record)
        file_name = f'{template_record.name}{file_extension}'.encode('utf-8')
        res = send_file(temp_file, mimetype=mimetype, filename=file_name, as_attachment=True)
        return res

    @http.route('/oneshare/template_download', type='http', auth='user', cors='*',
                csrf=False,
                save_session=False)
    def template_download(self):
        """
        Downloads the template excel
        """
        record_ids_list = request.params.get('ids', '').split(',')
        record_ids = [int(id) for id in record_ids_list]
        template_records = request.env['onesphere.template.download'].search([('id', 'in', record_ids)])
        if not template_records:
            raise ValidationError(_('No template record!'))
        temp_file = tempfile.TemporaryFile()
        if len(template_records) > 1:
            res = self.multi_template_download(temp_file, template_records)
        else:
            res = self.single_template_download(temp_file, template_records)
        res.headers['Cache-Control'] = 'no-cache'
        return res
