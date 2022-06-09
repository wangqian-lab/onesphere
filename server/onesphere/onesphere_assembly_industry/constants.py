# -*- encoding: utf-8 -*-

import os

# 拧紧类型
TIGHTENING_TEST_TYPE = "tightening"
PROM_TIGHTENING_TEST_TYPE = "promiscuous_tightening"

ALL_TIGHTENING_TEST_TYPE_LIST = [TIGHTENING_TEST_TYPE, PROM_TIGHTENING_TEST_TYPE]

# 测量类型
MEASURE_TYPE = "measure"
MULTI_MEASURE_TYPE = "multi_measure"
PASS_FAIL_TYPE = "pass_fail"

ALL_MEASURE_TYPE_LIST = [MEASURE_TYPE, MULTI_MEASURE_TYPE, PASS_FAIL_TYPE]

# 拧紧工具类型集合
ASSEMBLY_TOOLS_TECH_NAME = ['tightening_nut_runner', 'tightening_wrench', 'tightening_spindle']

# endpoint
MASTER_ROUTING_API = "/rush/v1/mrp.routing.workcenter"
