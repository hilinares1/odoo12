# All the Datetime field value as str(datetime)
from . import sortedcontainers
from . import models
from . import wizard
from . import report
from contextlib import closing
import psycopg2
import logging

_logger = logging.getLogger(__name__)
from odoo import api, SUPERUSER_ID

def post_init_load_extension(cr, registry):
    try:
        with closing(registry.cursor()) as cr1:
            cr1.execute("SELECT * FROM pg_extension where extname = 'tablefunc'")
            ex_dict = cr1.dictfetchall()
            if not ex_dict or not ex_dict[0].get('extname'):
                cr1.execute("CREATE EXTENSION tablefunc")
                
            cr1.commit()
            env = api.Environment(cr, SUPERUSER_ID, {})
            env['product.average.daily.sale'].create_stored_procedures()
    except psycopg2.DatabaseError as e:
            if e.pgcode == '58P01':
                _logger.warning("Please install Postgresql - Contrib in Postgresql")
            pass
    
