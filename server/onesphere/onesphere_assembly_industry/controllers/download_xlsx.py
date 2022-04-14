# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import send_file, Controller, request
import tempfile
import logging
import binascii

_logger = logging.getLogger(__name__)


class OneshareTemplateDownloadController(Controller):

    @http.route('/oneshare/template_download/<int:record_id>', type='http', auth='user', cors='*',
                csrf=False,
                save_session=False)
    def template_download(self, record_id):
        """
        Downloads the template excel
        """
        template_record = request.env['template.download'].search([('id', '=', record_id)])
        if not template_record:
            raise ValidationError(_('No template record!'))
        template_obj = template_record.template_file
        if not template_obj:
            raise ValidationError(_('No template file!'))
        temp_file = tempfile.TemporaryFile()
        temp_file.write(binascii.a2b_base64(template_obj))
        file_name = f'{template_record.name}.xlsx'.encode('utf-8')
        res = send_file(temp_file, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=file_name, as_attachment=True)
        res.headers['Cache-Control'] = 'no-cache'
        return res
