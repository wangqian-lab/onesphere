from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    onesphere_bom_operation_ids = fields.Many2many('mrp.routing.workcenter', 'bom_operation_rel', 'onesphere_bom_id',
                                                   'onesphere_operation_id', string='MRP Bom Operation Relationship')
