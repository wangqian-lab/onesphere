# -*- coding: utf-8 -*-

from odoo import models, fields
from random import randint


class OneshareMOMTrackCode(models.Model):
    """ Track Code """
    _name = 'oneshare.track.code'
    _description = '追踪码'
    _log_access = False
    _rec_name = 'track_code'

    track_code = fields.Char(string="Track Code", required=True)

    _sql_constraints = [
        ('track_code_uniq', 'unique(track_code)', 'Track Code MUST BE Unique!')]
