# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.oneshare_utils.constants import ONESHARE_DEFAULT_SPC_MIN_LIMIT, ONESHARE_DEFAULT_SPC_MAX_LIMIT


class OnesphereSPCMixin(models.AbstractModel):
    _name = 'onesphere.spc.mixin'
    _description = '统计过程控制MIXIN类'

    query_date_from = fields.Datetime(string='Query Date From')
    query_date_to = fields.Datetime(string='Query Date to', default=fields.Datetime.now)

    model_object = fields.Many2one('ir.model', string='Model')

    model_object_field = fields.Many2one('ir.model.fields', string='Field',
                                         domain=lambda self: [('id', 'in', self.model_object.field_id.ids)])

    spc_step = fields.Selection([('0.1', '0.1'), ('0.2', '0.2'), ('0.5', '0.5'), ('1', '1')],
                                string='SPC Analysis Step',
                                default='0.5')

    usl = fields.Float(string='规格上限(USL)', default=10.0)

    lsl = fields.Float(string='规格下限(LSL)', default=1.0)

    cmk = fields.Float(string='Machine Capability Index(CMK)', default=0.0, store=False)

    cpk = fields.Float(string='Process Capability Index(CPK)', default=0.0, store=False)

    limit = fields.Integer(string='SPC Query Record Count Limit', default=ONESHARE_DEFAULT_SPC_MAX_LIMIT)

    @api.model
    def query_spc(self, *args, **kwargs):
        raise UserError(_('Please Implement Via Every SPC Modules, No Mixin Class'))
