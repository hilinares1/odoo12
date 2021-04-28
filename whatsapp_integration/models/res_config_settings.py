# -*- coding: utf-8 -*-

import os
import shutil

from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def action_logout(self):
        user = self.env.uid
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.abspath(dir_path + '/../wizard')
        data_dir = '.user_data_uid_' + str(user)
        try:
            shutil.rmtree(dir_path + '/' + data_dir)
        except:
            pass
