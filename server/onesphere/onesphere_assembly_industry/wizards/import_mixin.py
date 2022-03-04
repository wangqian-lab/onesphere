# -*- coding: utf-8 -*-

from odoo import models, fields, api

class OnesphereImportMixin(models.AbstractModel):
    _name = 'onesphere.import.mixin'
    _description = 'Onesphere Import Mixin'

    file_type = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File'), ('xlsx', 'XLSX File')], string='File Type', default='xlsx')
    file = fields.Binary(string="Upload File", attachment=False)
    img_url = fields.Char(string='Img Url')

