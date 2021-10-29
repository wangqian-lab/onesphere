# -*- coding: utf-8 -*-

import os, io
from odoo.tests import common
import json


class TestOssObject(common.TransactionCase):

    def setUp(self):
        """set up"""
        super(TestOssObject, self).setUp()

    def test_get_oss_object(self):
        oss_interface = self.env['onesphere.oss.interface']
        obj = oss_interface.get_oss_object("test", "test1.json")
        oss_interface.put_oss_object("test", "test2.json", io.BytesIO(obj), 50540)
