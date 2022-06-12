# -*- coding: utf-8 -*-
import os
from jinja2 import Template
import random

DIST_DIR_PATH = '../server/onesphere/onesphere_assembly_industry/demo'
DIST_FILE = 'tightening_result_demo.xml'

DIST_PATH = '{}/{}'.format(DIST_DIR_PATH, DIST_FILE)

G_TMPL = Template('''
<odoo>
    <data noupdate="0">
        {% for item in items %}
            {{ item }}
        {% endfor %}
        </data>
</odoo>
''')

RECORD_TMPL = Template('''
        <record id="tightening_result_{{ id }}" model="onesphere.tightening.result">
            <field name="track_no">{{ track_no }}</field>
            <field name="attribute_equipment_no">{{ attribute_equipment_no }}</field>
            <field name="measurement_final_torque">{{ torque }}</field>
            <field name="measurement_final_angle">{{ degree }}</field>
            <field name="step_type">tightening</field>
            <field name="tightening_point_name" ref="{{ tightening_bolt_id }}"/>
            <field name="tightening_result">{{ result }}</field>
            <field name="tightening_strategy">{{ tightening_strategy }}</field>
            <field name="control_time" eval="(DateTime.today() - relativedelta(days={{ delta_day }})).strftime('%Y-%m-%d %H:%M')"/>
            <field name="tightening_id">{{ tightening_id }}</field>
        </record>
''')


def gen_record_msg(*args, **kwargs):
    r = RECORD_TMPL.render(**kwargs)
    return r


if __name__ == '__main__':
    if os.path.exists(DIST_PATH):
        os.remove(DIST_PATH)
    rec_str = []
    for i in range(1000):
        torque = round(random.uniform(3.5, 5.4), 2)
        degree = round(random.uniform(165.5, 187.5), 2)
        result = random.choice(['ok', 'nok', 'ak2'])
        tightening_strategy = random.choice(['AD', 'AW'])
        delta_day = random.choice([1, 2])
        track_no = random.choice(['0781213', '0781214', '0781215'])
        tightening_bolt_id = random.choice(
            ['tightening_bolt_0', 'tightening_bolt_1', 'tightening_bolt_2', 'tightening_bolt_3'])
        attribute_equipment_no = random.choice(['tightening_unit_1', 'tightening_unit_2', 'tightening_unit_3'])
        m = gen_record_msg(id=i, attribute_equipment_no=attribute_equipment_no, track_no=track_no, torque=torque,
                           degree=degree, result=result, tightening_bolt_id=tightening_bolt_id,
                           tightening_strategy=tightening_strategy,
                           delta_day=delta_day, tightening_id=i + 1)
        rec_str.append(m)
    ss = G_TMPL.render(items=rec_str)
    with open(DIST_PATH, 'w') as f:
        f.write(ss)
