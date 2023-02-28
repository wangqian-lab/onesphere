# -*- coding: utf-8 -*-
from odoo.addons.onesphere_assembly_industry.tests.common import (
    TestOneshareAssyIndustryCommon,
)

from odoo.tests import tagged


@tagged("-standard", "tightening_result")
class TestTighteningResult(TestOneshareAssyIndustryCommon):
    def test_get_tightening_result_filter_datetime(self):
        result = self.env[
            "onesphere.tightening.result"
        ].get_tightening_result_filter_datetime()
        self.assertTrue(isinstance(result, dict))

    def test_get_nok_tightening_result_time_bucket_count(self):
        result = self.env[
            "onesphere.tightening.result"
        ].get_nok_tightening_result_time_bucket_count()
        self.assertTrue(isinstance(result, dict))
