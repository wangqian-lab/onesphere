# -*- coding: utf-8 -*-
from odoo.addons.onesphere_assembly_industry.tests.common import TestOneshareAssyIndustryCommon
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError


@tagged('-standard', 'tightening_result')
class TestTighteningResult(TestOneshareAssyIndustryCommon):

    def test_get_tightening_result_filter_datetime(self):
        result = self.env['onesphere.tightening.result'].get_tightening_result_filter_datetime()
        self.assertTrue(isinstance(result, dict))
