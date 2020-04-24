#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import platform
sys.path.append("../")
_sig = '\\' if platform.system().lower() == 'windows' else '/'
VERIFY_PATH = os.path.realpath(__file__).split(os.path.basename(__file__))[0] + _sig + 'test_captcha'
background_path = os.path.realpath(__file__).split(os.path.basename(__file__))[0] + _sig + 'background'
knn_data_path = os.path.realpath(__file__).split(os.path.basename(__file__))[0] + _sig + 'knn_database'



