# -*- encoding: utf-8 -*-

import os
from distutils.util import strtobool
from odoo.addons.oneshare_utils.constants import ENV_ONESHARE_EXPERIMENTAL_ENABLE

ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL = strtobool(os.getenv('ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL', 'false'))

DEFAULT_LIMIT = 80


def oneshare_daq_with_track_code_rel_enable():
    return ENV_ONESHARE_EXPERIMENTAL_ENABLE & ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL
