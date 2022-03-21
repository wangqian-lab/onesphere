from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    @api.model
    def create(self, vals):
        # 创建工作中心会自动创建一个工作中心组，来确保工具可以选到
        ret = super(MrpWorkcenter, self).create(vals)
        group_data = {
            'code': vals.get('code'),
            'name': vals.get('name'),
            'onesphere_workcenter_ids': [(4, ret.id)],
            'company_id': vals.get('company_id'),
            'active': True
        }
        self.env['mrp.workcenter.group'].sudo().create(group_data)
        return ret
