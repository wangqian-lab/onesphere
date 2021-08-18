# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HMIUserRole(models.Model):
    _name = 'hmi.user.role'

    _description = 'MOM HMI User Role'

    name = fields.Char('HMI User Role Name')
    code = fields.Char('HMI User Role Code')


class ResUsers(models.Model):
    _inherit = 'res.users'

    uuid = fields.Char(string='UUID')

    hmi_role_id = fields.Many2one(
        'hmi.user.role',
        'HMI角色')

    _sql_constraints = [
        ('unique_uuid', 'unique(uuid)', 'Every User unique UUID'),
    ]
