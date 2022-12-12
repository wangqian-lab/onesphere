from typing import Union

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie
from snapshot_phantomjs import snapshot

from odoo import fields, models, _
from odoo.exceptions import ValidationError


def generate_base64_image_content_str(chart):
    img_data = snapshot.make_snapshot(
        html_path=chart.render(),
        file_type='png',
        delay=1,
        pixel_ratio=2,
    )  # base64 string

    content = img_data.replace('TypeError: Attempting to change the setter of an unconfigurable property.', '')
    return content


def generate_pie_chart(title, subtitle, labels, values):
    c = (
        Pie(init_opts=opts.InitOpts(width="800px", height="500px"),
            ).add(
            title,
            [list(z) for z in zip(labels, values)],
            radius=["40%", "55%"],
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                font_size=24,
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999",
                          "lineHeight": 24,
                          "fontSize": 16,
                          "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",
                        "width": "100%",
                        "align": "right",
                        "height": 24,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},
                    "per": {
                        "color": "#eee",
                        "fontSize": 16,
                        "backgroundColor": "#334455",
                        "padding": [2, 4],
                        "borderRadius": 2,
                    },
                },
            ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title=subtitle, title_textstyle_opts=opts.TextStyleOpts(font_size=24)),
            legend_opts=opts.LegendOpts(
                pos_right='15%',
                textstyle_opts=opts.TextStyleOpts(font_size=24),
            ),
        )
    )
    return c


def bolt_statistic_pie_chart(final_ok_count=0, bolt_count=0, final_ok_percent='0.0%'):
    labels = ['最终合格数量', '最终不合格数量']
    values = [final_ok_count, bolt_count - final_ok_count]

    c = generate_pie_chart("拧紧螺栓编号统计合格率", f'最终合格率:{final_ok_percent}', labels, values)

    content = generate_base64_image_content_str(c)
    return content


def result_statistic_pie_chart(results_pd):
    labels = list(map(str.upper, results_pd.index.tolist()))
    values = results_pd['count'].tolist()

    c = generate_pie_chart("拧紧合格异常比例", '拧紧合格异常比例', labels, values)

    content = generate_base64_image_content_str(c)

    return content


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

    def get_count_groupby_tightening_result(self, filter='1=1'):
        sql = f'''SELECT tightening_result, count(*) FROM onesphere_tightening_result WHERE track_no='{self.track_no}' AND {filter} GROUP BY tightening_result'''
        self._cr.execute(sql)
        d = self._cr.fetchall()
        result = {dd[0]: dd[1] for dd in d}
        return result

    def get_results_via_blot_id(self, bolt_id):
        sql = f'''SELECT tightening_result, tightening_process_no, measurement_final_torque, measurement_final_angle, 
                control_time, workcenter_code, attribute_equipment_no, error_code FROM onesphere_tightening_result 
                WHERE track_no='{self.track_no}' AND tightening_point_name={bolt_id} ORDER BY control_time'''
        self._cr.execute(sql)
        results = self._cr.fetchall()
        return results

    def get_bolt_number(self, bolt_id):
        sql = f'''SELECT name from onesphere_tightening_bolt WHERE id={bolt_id} '''
        self._cr.execute(sql)
        result = self._cr.fetchone()
        return result[0]

    def get_results_group_by_bolt(self, tightening_point_list):
        tightening_results = []
        first_ok_count, final_ok_count = 0, 0
        for bolt in tightening_point_list:
            bolt_id = bolt[0]
            bolt_name = self.get_bolt_number(bolt_id)
            results_of_bolt = self.get_results_via_blot_id(bolt_id)
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
        results = self.get_count_groupby_tightening_result()
        results_pd = pd.DataFrame.from_dict(results, orient='index',
                                            columns=['count'])
        result_count = results_pd['count'].sum()
        if result_count < 1:
            raise ValidationError(_('No result record!'))
        ok_count = results_pd.loc['ok']['count']
        abnormal_count = result_count - ok_count
        ok_percent = calculate_percent(ok_count, result_count, 2)
        abnormal_percent = calculate_percent(abnormal_count, result_count, 2)
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
            'abnormal_count': abnormal_count,
            'ok_percent': ok_percent,
            'abnormal_percent': abnormal_percent,
            'bolt_count': bolt_count,
            'first_ok_count': first_ok_count,
            'final_ok_count': final_ok_count,
            'first_ok_percent': first_ok_percent,
            'final_ok_percent': final_ok_percent,
            'results': results_group_by_bolt,
            'bolt_statistic_pie_chart': bolt_statistic_pie_chart(final_ok_count, bolt_count, final_ok_percent),
            'result_statistic_pie_chart': result_statistic_pie_chart(results_pd),
        }
        return data

    def print_report(self):
        self.ensure_one()
        data = self.get_report_data()
        report = self.env.ref('onesphere_assembly_industry.print_tightening_result_report')
        return report.report_action([], data=data)
