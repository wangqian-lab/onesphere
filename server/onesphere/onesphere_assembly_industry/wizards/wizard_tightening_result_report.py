from odoo import fields, models, _
from odoo.exceptions import ValidationError
import werkzeug.local

_request_stack = werkzeug.local.LocalStack()
request = _request_stack()


class WizardTighteningResultReport(models.TransientModel):
    _name = 'wizard.tightening.result.report'
    _description = 'Wizard Tightening Result Report'

    track_no = fields.Char(string='Track No', required=True)

    def print_report(self):
        self.ensure_one()
        doc = self.env['onesphere.tightening.result'].search([('track_no', '=', self.track_no)])
        report = self.env.ref('onesphere_assembly_industry.print_tightening_result_report')
        sql = f'''SELECT tightening_result, tightening_process_no, measurement_final_torque,
             measurement_final_angle, control_time  FROM onesphere_tightening_result 
             WHERE track_no='{self.track_no}' ORDER BY id DESC'''
        self._cr.execute(sql)
        results = self._cr.fetchall()
        data = {
            'track_no': self.track_no,
            'results': results,
        }
        if not doc:
            raise ValidationError(_('No document record!'))
        return report.report_action([], data=data)
