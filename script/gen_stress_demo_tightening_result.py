# -*- coding: utf-8 -*-
import csv
import os
import random
import uuid

from script.constants import attribute_equipments, station_names

DIST_DIR_PATH = '../server/oneshare_enterprise/tests/stress'
DIST_FILE = 'cap2.0拧紧结果数据包.csv'

DIST_PATH = '{}/{}'.format(DIST_DIR_PATH, DIST_FILE)

if __name__ == '__main__':
    if os.path.exists(DIST_PATH):
        os.remove(DIST_PATH)
    rec_str = []
    # track_codes = random_track_codes()
    with open(DIST_PATH, 'w', newline='') as f:
        headers = ['entity_id', 'station_name', 'tool_sn', 'tightening_id']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for i in range(100000):
            entity_id = uuid.uuid4().hex
            station_name = random.choice(station_names)
            tool_sn = random.choice(attribute_equipments)
            tightening_id = i + 1
            writer.writerow({'entity_id': entity_id, 'station_name': station_name, 'tool_sn': tool_sn,
                             'tightening_id': tightening_id})
