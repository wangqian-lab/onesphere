# -*- coding: utf-8 -*-

from . import models
from odoo.models import SUPERUSER_ID, api


def _default_group_mrp_routing(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ResConfig = env['res.config.settings']
    default_values = ResConfig.default_get(list(ResConfig.fields_get()))
    if default_values.get('group_mrp_routings', False):
        return
    default_values.update({'group_mrp_routings': True})
    ResConfig.create(default_values).execute()
    cr.commit()  # force commit


def _onesphere_core_post_init(cr, registry):
    _default_group_mrp_routing(cr)
