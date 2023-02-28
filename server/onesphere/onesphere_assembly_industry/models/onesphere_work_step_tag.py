# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OnesphereWorkStepTag(models.Model):
    _name = "onesphere.work.step.tag"
    _description = "Work Step Tag"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index", required=True)
    description = fields.Char(string="Description")
