# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.onesphere_assembly_industry.constants import TIGHTENING_TEST_TYPE
from odoo.exceptions import ValidationError


class MultiUpdateWizard(models.TransientModel):
    _name = 'multi.update.wizard'

    tightening_units = fields.Many2many('onesphere.tightening.unit', 'multi_update_unit_rel', 'multi_update_id',
                                        'tightening_unit_id', string='Tightening Units')
    product_id = fields.Many2one('product.product', 'Consume Product(Tightening Bolt/Screw)',
                                 domain="[('categ_id.name', '=', 'Bolt')]")
    tightening_pet = fields.Integer(string='Program Number(Pset/Job)')

    def multi_update(self):
        if not self.env.context.get('step_id'):
            return
        step = self.env['oneshare.quality.point'].search(
            [('id', '=', self.env.context.get('step_id'))])
        if step.test_type_id.technical_name == TIGHTENING_TEST_TYPE and len(self.tightening_units) > 1:
            raise ValidationError(_('If The Type Of Step Is Tightening，Can Only Chose One Unit!'))
        points = step.tightening_opr_point_ids
        for point in points:
            point.tightening_units = [
                (6, 0, self.tightening_units.ids)] if self.tightening_units else point.tightening_units
            point.product_id = self.product_id.id if self.product_id else point.product_id
            point.tightening_pet = self.tightening_pet if self.tightening_pet else point.tightening_pet
