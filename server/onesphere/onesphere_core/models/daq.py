# -*- coding: utf-8 -*-
from __future__ import division
from odoo import fields, models, api, SUPERUSER_ID
from odoo.addons.onesphere_core.constants import oneshare_daq_with_track_code_rel_enable

try:
    from odoo.models import OneshareHyperModel as HModel
except ImportError:
    from odoo.models import Model as HModel


class OperationResult(models.AbstractModel):
    """
    采集数据表，直接插入到数据库中，平铺的数据，字段尽量没有关联关系
    """

    _name = "onesphere.daq.item"
    _description = "Daq Operation Result Abstract Model"

    _rec_name = "track_no"

    _hyper_interval = "3 month"

    _hyper_field = "control_time"

    _dimensions = ["attribute_equipment_no"]

    control_time = fields.Datetime(
        string="数据生成时间", default=fields.Datetime.now, required=True
    )

    if oneshare_daq_with_track_code_rel_enable():
        track_no = fields.Many2one("oneshare.track.code", string="追溯码")
    else:
        track_no = fields.Char(default="", string="追溯码")

    # quality_point_id = fields.Many2one('oneshare.quality.point', string=u'相关联质量控制点')
    #
    # attribute_type = fields.Char(u'数据类型')
    #
    # attribute_val = fields.Char(u'数值')
    #
    # attribute_uom = fields.Char(u'单位')

    attribute_equipment_no = fields.Char("设备序列号")
