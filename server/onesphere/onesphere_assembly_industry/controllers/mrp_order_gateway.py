# -*- coding: utf-8 -*-
from collections import namedtuple


def package_multi_measure_4_measure_step(step):
    item = step
    val = {
        "name": item.name,
        "code": item.code,
        # "note": item.title or '',
        "note": '',
        "sequence": 1,
        "test_type": item.test_type,  # passfail or measure
        "tolerance_min": item.tolerance_min,
        "tolerance_max": item.tolerance_max,
        "norm_unit": item.norm_unit,
        "norm": item.norm,
        # "equipment_id": item.test_equipment_id
        "equipment_id": ""
    }
    v = namedtuple('Struct', val.keys())(*val.values())
    return v


def package_multi_measurement_items(measu_items):
    ret = []
    for idx, item in enumerate(measu_items):
        val = {
            "title": item.name,
            "code": getattr(item, 'name', ''),  # 多重测量的检测项的参照
            "desc": item.note or '',
            "sequence": idx + 1,
            "test_type": item.test_type,  # passfail or measure
            "tolerance_min": item.tolerance_min,
            "tolerance_max": item.tolerance_max,
            "uom": item.norm_unit,
            "target": item.norm,
            # "sn": item.equipment_id.serial_no if item.equipment_id else ""
            "sn": ""
        }
        ret.append(val)
    return ret