# -*- coding: utf-8 -*-

from . import models
from odoo.models import SUPERUSER_ID, api

vals_key = ['group_mrp_routings', 'group_product_variant']


# 默认激活了工艺路线功能
def _default_group_mrp_routing(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ResConfig = env['res.config.settings']
    default_values = ResConfig.default_get(list(ResConfig.fields_get()))
    for key in vals_key:
        if default_values.get(key, False):
            continue
        default_values.update({key: True})
    ResConfig.create(default_values).execute()


def _modify_all_workcenter_resource_calendar(cr, resource_xml_id):
    env = api.Environment(cr, SUPERUSER_ID, {})
    WorkCenter = env['mrp.workcenter'].search([(1, '=', 1)])
    calendar_id = env.ref(resource_xml_id)
    if calendar_id:
        WorkCenter.write({'resource_calendar_id': calendar_id.id})


def _onesphere_core_post_init(cr, registry):
    _default_group_mrp_routing(cr)
    _modify_all_workcenter_resource_calendar(cr, 'onesphere_core.resource_calendar_std_140h')


def _oneshare_core_uninstall_hook(cr, registry):
    _modify_all_workcenter_resource_calendar(cr, 'resource.resource_calendar_std')
