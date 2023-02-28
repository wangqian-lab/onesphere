# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests as Requests
from http import HTTPStatus
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from validators import ip_address
from odoo.tools import ustr
from odoo.addons.oneshare_utils.constants import DEFAULT_TIMEOUT
from odoo.addons.onesphere_mdm.constants import (
    HEALTHZ_URL,
    MODBUSTCP_PROTOCOL_TYPE,
    MODBUSRTU_PROTOCOL_TYPE,
    RAWTCP_PROTOCOL_TYPE,
    RAWUDP_PROTOCOL_TYPE,
    HTTP_PROTOCOL_TYPE,
)


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"
    _check_company_auto = True

    technical_name = fields.Char(
        "Technical name", related="category_id.technical_name", store=True
    )
    expected_mtbf = fields.Integer(
        string="Expected MTBF", help="Expected Mean Time Between Failure"
    )
    mtbf = fields.Integer(
        string="MTBF",
        help="Mean Time Between Failure, computed based on done corrective maintenances.",
    )
    mttr = fields.Integer(string="MTTR", help="Mean Time To Repair")
    workcenter_id = fields.Many2one(
        "mrp.workcenter", string="Work Center", check_company=True
    )
    category_name = fields.Char(related="category_id.technical_name")
    connection_ids = fields.One2many(
        "maintenance.equipment.connection",
        "equipment_id",
        string="Connection Information",
    )

    serial_no = fields.Char("Serial Number", copy=False, required=True)

    def button_mrp_workcenter(self):
        self.ensure_one()
        return {
            "name": _("work centers"),
            "view_mode": "form",
            "res_model": "mrp.workcenter",
            "view_id": self.env.ref("mrp.mrp_workcenter_view").id,
            "type": "ir.actions.act_window",
            "res_id": self.workcenter_id.id,
            "context": {"default_company_id": self.company_id.id},
        }


class MaintenanceEquipmentCategory(models.Model):
    _inherit = "maintenance.equipment.category"

    @api.depends("name")
    def _compute_technical_name(self):
        for category in self:
            if category.technical_name:
                continue
            category.technical_name = category.name

    technical_name = fields.Char(
        "Technical name", required=True, compute=_compute_technical_name, store=True
    )

    _sql_constraints = [
        (
            "technical_name_uniq",
            "unique (technical_name)",
            "The technical name of the equipment category must be unique!",
        )
    ]

    @api.model
    def create(self, vals):
        if not vals.get("technical_name", None):
            vals.update({"technical_name": vals.get("name")})
        return super(MaintenanceEquipmentCategory, self).create(vals)


class EquipmentConnection(models.Model):
    _name = "maintenance.equipment.connection"
    _description = "Equipment Connection"
    _log_access = False

    active = fields.Boolean(default=True)
    name = fields.Char(string="Connection", required=True, default="Connection")
    ip = fields.Char(string="IP")
    tty = fields.Char(string="Serial TTY")

    equipment_id = fields.Many2one("maintenance.equipment", string="Equipment")

    port = fields.Integer(string="port", default=0)
    unitid = fields.Integer(
        string="Unit ID", help="Modbus need this ID for identification", default=0
    )
    protocol = fields.Selection(
        [
            (MODBUSTCP_PROTOCOL_TYPE, "ModbusTCP"),
            (MODBUSRTU_PROTOCOL_TYPE, "ModbusRTU"),
            (HTTP_PROTOCOL_TYPE, "HTTP"),
            (RAWTCP_PROTOCOL_TYPE, "TCP"),
            (RAWUDP_PROTOCOL_TYPE, "UDP"),
        ],
        string="Protocol",
    )

    def button_check_healthz(self):
        for connection in self:
            if connection.protocol != "http":
                continue
            try:
                url = f"http://{connection.ip}:{connection.port}/{HEALTHZ_URL}"
                resp = Requests.get(
                    url,
                    headers={"Content-Type": "application/json"},
                    timeout=DEFAULT_TIMEOUT,
                )
                if resp.status_code == HTTPStatus.NO_CONTENT:
                    raise UserError(
                        _(
                            "Connection Test Succeeded! Everything seems properly set up!"
                        )
                    )
                else:
                    raise UserError(
                        _(
                            f"Connection Test Failed! Here is what we got instead: {resp.status_code}!"
                        )
                    )
            except Exception as e:
                raise UserError(
                    _(
                        f"Connection Test Failed! Here is what we got instead:\n {ustr(e)}"
                    )
                )

    @api.constrains("ip", "port")
    def _constraint_ip(self):
        if not self.ip:
            return
        ret = ip_address.ipv4(self.ip)
        if not ret:
            # 返回一个ValidationFailure对象： https://validators.readthedocs.io/en/latest/
            raise ValidationError(_("is NOT valid IP Address!"))
        if self.port <= 0:
            raise ValidationError(_("Port must be greater than ZERO!"))

    def name_get(self):
        def get_names(cat):
            if cat.protocol == MODBUSTCP_PROTOCOL_TYPE:
                return f"modbustcp://{cat.ip}:{cat.port}/{cat.unitid}"
            if cat.protocol == MODBUSRTU_PROTOCOL_TYPE:
                return f"modbusrtu://{cat.tty}/{cat.unitid}"
            if cat.protocol in [
                HTTP_PROTOCOL_TYPE,
                RAWTCP_PROTOCOL_TYPE,
                RAWUDP_PROTOCOL_TYPE,
            ]:
                return f"{cat.protocol}://{cat.ip}:{cat.port}"
            else:
                raise ValueError(f"Protocol Not Support: {cat.protocol}")

        return [(cat.id, get_names(cat)) for cat in self]
