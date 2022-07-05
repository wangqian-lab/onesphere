# -*- coding: utf-8 -*-
import os
import uuid

import xmltodict
from jinja2 import Template
import random
from script.constants import track_codes, tightening_bolts, attribute_equipments

from faker import Faker

fake = Faker()

DIST_RESULT_DIR_PATH = '../server/onesphere/onesphere_assembly_industry/demo'
DIST_RESULT_FILE = 'tightening_result_demo.xml'

DIST_RESULT_PATH = '{}/{}'.format(DIST_RESULT_DIR_PATH, DIST_RESULT_FILE)

DIST_DIR_PATH = '../server/oneshare_enterprise/oneshare_cap_assembly/demo'
DIST_FILE = 'cap_analysis_log_demo.xml'

DIST_PATH = '{}/{}'.format(DIST_DIR_PATH, DIST_FILE)

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
        <record id="cap_tightening_log_{{ id }}" model="oneshare.cap.tightening.analysis.log">
            <field name="tightening_result_entity_id">{{ tightening_result_entity_id }}</field>
            <field name="tightening_track_code">{{ tightening_track_code }}</field>
            <field name="tightening_tool_entity_id">{{ tightening_tool_entity_id }}</field>
            <field name="analysis_result_state">{{ analysis_result_state }}</field>
            <field name="tightening_bolt_id" ref="{{ tightening_bolt_id }}"/>
            <field name="cap_error_massage">{{ cap_error_massage }}</field>
            <field name="time" eval="(DateTime.today() - relativedelta(days={{ delta_day }})).strftime('%Y-%m-%d %H:%M')"/>
        </record>
''')


def gen_record_msg(*args, **kwargs):
    r = RECORD_TMPL.render(**kwargs)
    return r


from typing import List, Dict


def convert_fields_to_dict(fields: List) -> Dict:
    field: Dict = {}
    ret = {}
    for field in fields:
        key = field.pop('@name')
        ret[key] = field
    return ret


if __name__ == '__main__':
    if os.path.exists(DIST_PATH):
        os.remove(DIST_PATH)
    rec_str = []
    result_dict = {}
    with open(DIST_RESULT_PATH) as f:
        a = f.read()
        result_dict = xmltodict.parse(a)
    results = result_dict.get('odoo', {}).get('data', {}).get('record', [])
    for i, r in enumerate(results):
        delta_day = random.choice([1, 2])
        d = convert_fields_to_dict(r.get('field'))
        tightening_result_entity_id = d.get('entity_id').get('#text')
        tightening_track_code = d.get('track_no').get('#text')
        tightening_tool_entity_id = d.get('attribute_equipment_no').get('#text')
        tightening_bolt_id = d.get('tightening_point_name').get('@ref')
        analysis_result_state = random.choice(['ok', 'nok'])
        cap_error_massage = random.choice(['', '101', '101,102', '101,102,103'])
        m = gen_record_msg(id=i,
                           tightening_result_entity_id=tightening_result_entity_id,
                           tightening_tool_entity_id=tightening_tool_entity_id,
                           tightening_bolt_id=tightening_bolt_id,
                           analysis_result_state=analysis_result_state,
                           delta_day=delta_day,
                           cap_error_massage=cap_error_massage,
                           tightening_track_code=tightening_track_code)
        rec_str.append(m)
    ss = G_TMPL.render(items=rec_str)
    with open(DIST_PATH, 'w') as f:
        f.write(ss)
