# -*- encoding: utf-8 -*-

import os
from distutils.util import strtobool


ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL = strtobool(os.getenv('ENV_ONESPHERE_DAQ_WITH_TRACK_CODE_REL', 'false'))
