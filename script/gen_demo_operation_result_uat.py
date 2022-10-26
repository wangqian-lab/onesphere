import json
import os
import pandas as pd
from jinja2 import Template
import random
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from script.constants import station_names, attribute_equipments, error_codes

DATETIME_LENGTH = len(datetime.today().now().strftime(DEFAULT_SERVER_DATETIME_FORMAT))

DIST_DIR_PATH = '../server/oneshare_enterprise/oneshare_cap_assembly/demo'
DIST_FILE = 'tightening_result_demo.xml'

DIST_PATH = '{}/{}'.format(DIST_DIR_PATH, DIST_FILE)

RESULT_DATA_PATH = '/home/leext/work/resulta.csv'

G_TMPL = Template('''
<odoo>
    <data noupdate="1">
        {% for item in items %}
            {{ item }}
        {% endfor %}
        </data>
</odoo>
''')

RECORD_TMPL = Template('''
        <record id="tightening_result_uat_{{ id }}" model="onesphere.tightening.result">
            <field name="entity_id">{{ entity_id }}</field>
            <field name="track_no">{{ track_no }}</field>
            <field name="tightening_process_no">{{ tightening_process_no }}</field>
            <field name="attribute_equipment_no">{{ attribute_equipment_no }}</field>
            <field name="measurement_final_torque">{{ measurement_final_torque }}</field>
            <field name="measurement_final_angle">{{ measurement_final_angle }}</field>
            <field name="tightening_point_name" ref="{{ tightening_point_name }}"/>
            <field name="step_type">tightening</field>
            <field name="tightening_result">{{ tightening_result }}</field>
            <field name="tightening_strategy">{{ tightening_strategy }}</field>
            <field name="control_time">{{ control_time }}</field>
            <field name="tightening_id">{{ tightening_id }}</field>
            <field name="curve_file">{{ curve_file }}</field>
            <field name="angle_max">{{ angle_max }}</field>
            <field name="angle_min">{{ angle_min }}</field>
            <field name="angle_target">{{ angle_target }}</field>
            <field name="torque_max">{{ torque_max }}</field>
            <field name="error_code">{{ error_code }}</field>
            <field name="torque_min">{{ torque_min }}</field>
            <field name="torque_target">{{ torque_target }}</field>
            <field name="torque_target">2</field>
            <field name="measurement_step_results">{{ step_results }}</field>
            <field name="workcenter_code">{{ workcenter_code }}</field>
        </record>
''')


def gen_record_msg(*args, **kwargs):
    r = RECORD_TMPL.render(**kwargs)
    return r


def get_step_result(step_results):
    step_results = json.loads(step_results)
    step_result_list = []
    for result in step_results:
        step_result_list.append({
            "measure_torque": round(result.get("measure_torque"), 2),
            "measure_angle": round(result.get("measure_angle"), 2)
        })
    return step_result_list


if __name__ == '__main__':
    if os.path.exists(DIST_PATH):
        os.remove(DIST_PATH)
    rec_str = []
    data = pd.read_csv(RESULT_DATA_PATH).to_dict()
    for index in range(len(data.get('pk'))):
        track_no = data['vin'][index][:8]
        tightening_process_no = data['pset'][index]
        measurement_final_torque = data['measure_torque'][index]
        measurement_final_angle = data['measure_angle'][index]
        tightening_point_name = data["nut_no"][index]
        tightening_result = data['measure_result'][index].lower()
        error_code = random.choice(error_codes) if tightening_result == 'nok' else ''
        tightening_strategy = random.choice(['AD', 'AW'])
        control_time = data['update_time'][index][:DATETIME_LENGTH] if data['update_time'][index] else datetime.now().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        control_timestamp = int(datetime.strptime(control_time, DEFAULT_SERVER_DATETIME_FORMAT).timestamp())
        entity_id = f"{track_no}_{data['tool_sn'][index]}_{control_timestamp}_{index}"
        tightening_id = data['tightening_id'][index]
        curve = f"{data['entity_id'][index].split('/')[-1]}.json"
        curve_file = '[{"file":"%s","op":1}]' % curve
        angle_max = data['angle_max'][index]
        angle_min = data['angle_min'][index]
        angle_target = data['angle_target'][index]
        torque_max = data['torque_max'][index]
        torque_min = data['torque_min'][index]
        torque_target = data['torque_target'][index]
        step_results = json.dumps(get_step_result(data['step_results'][index]))
        workcenter_code = random.choice(station_names)
        attribute_equipment_no = random.choice(attribute_equipments)
        m = gen_record_msg(id=index, entity_id=entity_id, track_no=track_no,
                           tightening_process_no=tightening_process_no,
                           measurement_final_torque=measurement_final_torque,
                           measurement_final_angle=measurement_final_angle,
                           tightening_point_name=tightening_point_name, tightening_result=tightening_result,
                           error_code=error_code,
                           tightening_strategy=tightening_strategy, control_time=control_time,
                           tightening_id=tightening_id, curve_file=curve_file, angle_max=angle_max, angle_min=angle_min,
                           angle_target=angle_target, torque_max=torque_max, torque_min=torque_min,
                           torque_target=torque_target, step_results=step_results, workcenter_code=workcenter_code,
                           attribute_equipment_no=attribute_equipment_no)
        rec_str.append(m)
    ss = G_TMPL.render(items=rec_str)
    with open(DIST_PATH, 'w') as f:
        f.write(ss)
