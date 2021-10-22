# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
import uuid


class TighteningOprPoint(models.Model):
    _name = 'onesphere.tightening.opr.point'
    _log_access = False

    _inherits = {'oneshare.quality.point': 'quality_point_id'}

    _description = '螺栓拧紧点'

    _order = "group_sequence, sequence"

    is_key = fields.Boolean(string='Is Key Tightening Point', default=False)
    active = fields.Boolean(
        'Active', default=True,
        help="If the active field is set to False, it will allow you to hide the bills of material without removing it.")

    sequence = fields.Integer('sequence', default=1)

    name = fields.Char('Tightening Point Name(Bolt Number)', related='quality_point_id.name', inherited=True,
                       default=lambda self: str(uuid.uuid4()))  # 如果未定义拧紧点编号，即自动生成uuid号作为唯一标示,螺栓编号

    group_id = fields.Many2one('onesphere.tightening.opr.point.group', string='Tightening Point Group',
                               help='拧紧组定义，当多轴或者多人同时作业时使用')

    group_sequence = fields.Integer(string='Group Sequence for Multi Spindle', help='拧紧组定义，当多轴或者多人同时作业时使用,定义其顺序')

    product_ids = fields.Many2many('product.product', 'Consume Product(Tightening Bolt/Screw)',
                                   related='quality_point_id.product_id',
                                   inherited=True,
                                   domain="[('onesphere_product_type', 'in', ['screw', 'bolt'])]")

    product_qty = fields.Float('Product Quantity', default=1.0, digits='Product Unit of Measure')

    x_offset = fields.Float('x axis offset from left(%)', default=0.0, digits='Unit of Tightening Opr Point Offset')

    y_offset = fields.Float('y axis offset from top(%)', default=0.0, digits='Unit of Tightening Opr Point Offset')

    tightening_pet = fields.Integer(string='程序号(Pset/Job)')

    control_mode = fields.Selection([('pset', 'Parameter Set'),
                                     ('job', 'Assembly Process')],
                                    default='pset',
                                    string='Control Mode For Tightening')

    parent_quality_point_id = fields.Many2one('oneshare.quality.point', ondelete='cascade', index=True,
                                              string='Quality Control Point(Tightening Operation Step)')

    quality_point_id = fields.Many2one('oneshare.quality.point', required=True,
                                       string='Quality Control Point(Tightening Work Step)',
                                       ondelete='cascade', auto_join=True)

    test_type_id = fields.Many2one('oneshare.quality.point.test_type', related='quality_point_id.test_type_id',
                                   default=lambda self: self.env.ref(
                                       'onesphere_assembly_industry.test_type_tightening_point'))

    max_attempt_times = fields.Integer(string='Tightening Operation Max Attempt Times', default=3)

    # 测量相关
    # norm = fields.Float('Norm', related='quality_point_id.norm', digits='Quality Tests', inherited=True)
    # tolerance_min = fields.Float('Min Tolerance', related='quality_point_id.tolerance_min',
    #                              digits='Quality Tests', inherited=True)
    # tolerance_max = fields.Float('Max Tolerance', related='quality_point_id.tolerance_max',
    #                              digits='Quality Tests', inherited=True)
    #
    # norm_degree = fields.Float('Norm Degree', related='quality_point_id.norm_degree', inherited=True,
    #                            digits='Quality Tests')  # TDE RENAME ?
    # tolerance_min_degree = fields.Float('Degree Min Tolerance', related='quality_point_id.tolerance_min_degree', inherited=True,
    #                                     digits='Quality Tests', default=0.0)
    # tolerance_max_degree = fields.Float('Degree Max Tolerance', related='quality_point_id.tolerance_max_degree', inherited=True,
    #                                     digits='Quality Tests', default=0.0)

    # 拧紧工具相关
    tightening_tool_ids = fields.Many2many('mrp.workcenter.group.tightening.tool', 'tightening_point_tool_rel',
                                           'point_id',
                                           'tightening_tool_id',
                                           string='Tightening Tools', copy=False)

    tightening_tool_id = fields.Many2one('maintenance.equipment', string='Prefer Tightening Tool',
                                         domain="[('category_name', 'in', ['tightening_wrench', 'tightening_nut_runner', 'tightening_spindle'])]",
                                         copy=False)
