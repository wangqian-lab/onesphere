from odoo import fields, models


class OneshareBomOperationRel(models.Model):
    _name = "onesphere.mrp.bom.operation.rel"
    _description = "物料清单作业关联表"
    _log_access = False

    onesphere_operation_id = fields.Many2one(
        "mrp.routing.workcenter", string="Operation", required=True
    )

    onesphere_operation_revision = fields.Integer(
        "Revision", related="onesphere_operation_id.revision", readonly=True
    )

    onesphere_bom_id = fields.Many2one(
        "mrp.bom", string="Bill Of Material", required=True
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    def name_get(self):
        res = []
        for rec in self:
            res.append(
                (
                    rec.id,
                    f"REV{rec.onesphere_operation_id.revision}-{rec.onesphere_operation_id.name}@{rec.onesphere_bom_id.display_name}",
                )
            )
        return res


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    onesphere_bom_operation_ids = fields.One2many(
        "onesphere.mrp.bom.operation.rel",
        "onesphere_bom_id",
        check_company=True,
        string="MRP Bom Operation Relationship",
    )
