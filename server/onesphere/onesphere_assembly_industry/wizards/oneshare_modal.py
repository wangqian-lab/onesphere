# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import MissingError


class OneshareModal(models.TransientModel):
    _inherit = 'oneshare.modal'

    def get_image_editor_action(self):
        ret = super(OneshareModal, self).get_image_editor_action()
        context = self.env.context
        if context.get('active_model') == 'oneshare.quality.point':
            return self.env.ref('onesphere_assembly_industry.oneshare_tightening_modal_view_form').id
        return ret
