# -*- coding: utf-8 -*-
from . import wizard
from . import models

from odoo import api, SUPERUSER_ID

def init_settings(env):
	# Install discount on line
    res_config_id = env['res.config.settings'].create({
        'group_discount_per_so_line': True
    })
    # We need to call execute, otherwise the "implied_group" in fields are not processed.
    res_config_id.execute()


def post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    init_settings(env)
