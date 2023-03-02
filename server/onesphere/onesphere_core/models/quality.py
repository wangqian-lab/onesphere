# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models, _


class OneshareOperationStepRel(models.Model):
    _name = 'onesphere.mrp.operation.step.rel'
    _description = '工步作业关联表'

    _log_access = False

    _order = "sequence asc, id desc"

    sequence = fields.Integer('Sequence', default=0)

    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation')

    work_step_id = fields.Many2one('oneshare.quality.point', string='Work step', required=True,
                                   domain=[('is_workorder_step', '=', True)])

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def name_get(self):
        res = []
        for point in self:
            res.append((point.id, f'#{point.sequence}[{point.operation_id.name}]'))
        return res


class OneshareTestType(models.Model):
    _name = "oneshare.quality.point.test_type"
    _description = "Quality Control Test Type"

    # Used instead of selection field in order to hide a choice depending on the view.
    name = fields.Char('Name', required=True, translate=True)
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
        return self.env['oneshare.quality.point.test_type'].search(domain, limit=1).id

    name = fields.Char(
        'Reference', required=True)
    sequence = fields.Integer('Sequence')

    code = fields.Char('Code', help='Reference(External)', required=True, default=lambda self: _('New'), copy=False)

    # product_ids = fields.Many2many(
    #     'product.product', string='Products',
    #     domain="[('type', 'in', ['product', 'consu']),'|', ('company_id', '=', False), ('company_id', '=', company_id.id)]")

    operation_type_ids = fields.Many2many(
        'oneshare.operation.type', string='Operation Types', required=True)

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.company)

    active = fields.Boolean(default=True)
    # check_count = fields.Integer(compute=_compute_check_count)
    # quality_check_ids = fields.One2many('oneshare.quality.check', 'quality_point_id')
    test_type_id = fields.Many2one('oneshare.quality.point.test_type', 'Test Type',
                                   help="Defines the type of the quality control point.",
                                   required=True, default=_get_default_test_type_id)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    note = fields.Html('Note')
    reason = fields.Html('Cause')

    norm = fields.Float('Norm', digits='Quality Tests')
    tolerance_min = fields.Float('Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float('Max Tolerance', digits='Quality Tests')
    norm_unit = fields.Char('Unit of Measure', default=lambda self: 'mm')

    # 工步相关
    is_workorder_step = fields.Boolean('Is MRP Working Step?')

    can_do_skip = fields.Boolean(string='Allow Do Skip', default=False, help='Whether This Step Can Be Skipped')
    can_do_rework = fields.Boolean(string='Allow Do Redo', default=True, help='Whether This Step Can Be Rework')
    onesphere_operation_ids = fields.One2many('onesphere.mrp.operation.step.rel', 'work_step_id',
                                              string='Operations', check_company=True)

    multi_measurement_ids = fields.One2many('oneshare.measurement.item', 'parent_quality_point_id',
                                            string='Measurement Items')

    multi_measurement_calc_ids = fields.One2many('oneshare.measurement.calc.item', 'parent_quality_point_id',
                                                 string='Measurement Calculate Items')

    component_id = fields.Many2one('product.product', 'Product To Register', check_company=True)

    # _sql_constraints = [('code_uniq', 'unique(code)', 'Only one code per working step is allowed')]

    def name_get(self):
        res = []
        for step in self:
            if not step.code:
                res.append((step.id, step.name))
            else:
                res.append((step.id, f'[{step.code}] {step.name}'))
        return res

    @api.model
    def default_get(self, fields_list):
        context = self.env.context
        res = super(OneshareQuality, self).default_get(fields_list)
        if 'operation_type_ids' not in fields_list:
            return res
        operation_type = None
        if context.get('default_operation_type'):
            operation_type = self.env['oneshare.operation.type'].search(
                [('code', '=', context.get('default_operation_type'))])
        if operation_type:
            res.update({
                'operation_type_ids': [(4, operation_type.id)]
            })
        return res

    @api.model
    def create(self, vals):
        if 'code' not in vals or vals['code'] == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('oneshare.quality.point') or _('New')
        return super(OneshareQuality, self).create(vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """ copy(default=None)

        Duplicate record ``self`` updating it with default values

        :param dict default: dictionary of field values to override in the
               original values of the copied record, e.g: ``{'field_name': overridden_value, ...}``
        :returns: new record

        """

        new = super(OneshareQuality, self).copy(default=default)

        for point in self.tightening_opr_point_ids:
            vals = point.copy_data()[0]
            vals.update({
                'name': str(uuid.uuid4()),
                'parent_quality_point_id': new.id,
            })
            self.env['onesphere.tightening.opr.point'].create(vals)
        return new
