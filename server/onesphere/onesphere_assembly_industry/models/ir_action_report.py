# -*- coding: utf-8 -*-

from odoo import models, api


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        command_args = super(IrActionsReport, self)._build_wkhtmltopdf_args(
            paperformat_id, landscape, specific_paperformat_args, set_viewport_size
        )
        if self.env.context.get("active_model", None) in [
            "wizard.tightening.result.report"
        ]:
            command_args.extend(["--enable-javascript"])
        return command_args
