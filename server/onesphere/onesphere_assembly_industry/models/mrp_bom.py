from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_oper_rel = fields.Many2many('mrp.routing.workcenter', relation='bom_operation_rel')

