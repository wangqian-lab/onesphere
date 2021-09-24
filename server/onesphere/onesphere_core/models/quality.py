# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.oneshare_utils.constants import ONESHARE_DEFAULT_LIMIT


class OneshareTestType(models.Model):
    _name = "oneshare.quality.point.test_type"
    _description = "Quality Control Test Type"

    # Used instead of selection field in order to hide a choice depending on the view.
    name = fields.Char('Name', required=True)
    technical_name = fields.Char('Technical name', required=True)
    active = fields.Boolean('active', default=True)


class OneshareQuality(models.Model):
    _name = "oneshare.quality.point"
    _description = "Quality Control Point"
    _inherit = ['mail.thread']
    _order = "sequence, id"
    _check_company_auto = True

    def _compute_check_count(self):
        check_data = self.env['quality.check'].read_group([('point_id', 'in', self.ids)], ['point_id'], ['point_id'])
        result = dict((data['point_id'][0], data['point_id_count']) for data in check_data)
        for point in self:
            point.check_count = result.get(point.id, 0)

    def _get_type_default_domain(self):
        domain = [('technical_name', '=', 'passfail')]
        return domain

    def _get_default_test_type_id(self):
        domain = self._get_type_default_domain()
        return self.env['quality.point.test_type'].search(domain, limit=1).id

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'),
        required=True)
    sequence = fields.Integer('Sequence')

    product_ids = fields.Many2many(
        'product.product', string='Products',
        domain="[('type', 'in', ['product', 'consu']),'|', ('company_id', '=', False), ('company_id', '=', company_id.id)]")
    picking_type_ids = fields.Many2many(
        'stock.picking.type', string='Operation Types', required=True, check_company=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.company)

    active = fields.Boolean(default=True)
    check_count = fields.Integer(compute=_compute_check_count)
    quality_check_ids = fields.One2many('oneshare.quality.check', 'quality_point_id')
    test_type_id = fields.Many2one('oneshare.quality.point.test_type', 'Test Type',
                                   help="Defines the type of the quality control point.",
                                   required=True, default=_get_default_test_type_id)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    note = fields.Html('Note')
    reason = fields.Html('Cause')
