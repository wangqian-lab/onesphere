from odoo import fields, models, _
from odoo.exceptions import ValidationError
import werkzeug.local
from typing import Union

_request_stack = werkzeug.local.LocalStack()
request = _request_stack()


def calculate_percent(numerator: Union[float, int], denominator: Union[float, int], float_num: int):
    return f'{round(numerator * 100 / denominator, float_num)}%'


class WizardTighteningResultReport(models.TransientModel):
    _name = 'wizard.tightening.result.report'
    _description = 'Wizard Tightening Result Report'

    track_no = fields.Char(string='Track No', required=True)

    def get_tightening_point(self):
        sql = f''' SELECT distinct(tightening_point_name) from onesphere_tightening_result WHERE track_no='{self.track_no}' '''
        self._cr.execute(sql)
        results = self._cr.fetchall()
        return results

    def get_count(self, filter='1=1'):
        sql = f'''SELECT count(*) FROM onesphere_tightening_result WHERE track_no='{self.track_no}' AND {filter}'''
        self._cr.execute(sql)
        result = self._cr.fetchone()
        return result[0]

    def get_results(self, bolt_id):
        sql = f'''SELECT tightening_result, tightening_process_no, measurement_final_torque, measurement_final_angle, 
                control_time, workcenter_code, attribute_equipment_no, error_code FROM onesphere_tightening_result 
                WHERE track_no='{self.track_no}' AND tightening_point_name={bolt_id} ORDER BY control_time'''
        self._cr.execute(sql)
        results = self._cr.fetchall()
        return results

    def get_bolt_name(self, bolt_id):
        sql = f'''SELECT name from onesphere_tightening_bolt WHERE id={bolt_id} '''
        self._cr.execute(sql)
        result = self._cr.fetchone()
        return result[0]

    def get_results_group_by_bolt(self, tightening_point_list):
        tightening_results = []
        first_ok_count, final_ok_count = 0, 0
        for bolt in tightening_point_list:
            bolt_id = bolt[0]
            bolt_name = self.get_bolt_name(bolt_id)
            results_of_bolt = self.get_results(bolt_id)
            tightening_results.append({
                'bolt_id': bolt_id,
                'bolt_name': bolt_name,
                'results': results_of_bolt,
                'count': len(results_of_bolt),
                'final_result': results_of_bolt[-1][0],
            })
            if results_of_bolt[0][0] == 'ok':
                first_ok_count += 1
            if results_of_bolt[-1][0] == 'ok':
                final_ok_count += 1
        return tightening_results, first_ok_count, final_ok_count

    def get_report_data(self):
        result_count = self.get_count()
        if result_count < 1:
            raise ValidationError(_('No result record!'))
        ok_count = self.get_count("tightening_result='ok'")
        nok_count = self.get_count("tightening_result='nok'")
        ok_percent = calculate_percent(ok_count, result_count, 2)
        nok_percent = calculate_percent(nok_count, result_count, 2)
        tightening_point_list = self.get_tightening_point()
        bolt_count = len(tightening_point_list)
        results_group_by_bolt, first_ok_count, final_ok_count = \
            self.get_results_group_by_bolt(tightening_point_list)
        first_ok_percent = calculate_percent(first_ok_count, bolt_count, 2)
        final_ok_percent = calculate_percent(final_ok_count, bolt_count, 2)
        data = {
            'track_no': self.track_no,
            'count': result_count,
            'ok_count': ok_count,
            'nok_count': nok_count,
            'ok_percent': ok_percent,
            'nok_percent': nok_percent,
            'bolt_count': bolt_count,
            'first_ok_count': first_ok_count,
            'final_ok_count': final_ok_count,
            'first_ok_percent': first_ok_percent,
            'final_ok_percent': final_ok_percent,
            'results': results_group_by_bolt,
        }
        return data

    def print_report(self):
        self.ensure_one()
        data = self.get_report_data()
        report = self.env.ref('onesphere_assembly_industry.print_tightening_result_report')
        return report.report_action([], data=data)
