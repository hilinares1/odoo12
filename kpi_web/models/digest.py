import logging
import pytz

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError

from odoo import models

_logger = logging.getLogger(__name__)


class Digest(models.Model):
    _inherit = 'digest.digest'

    def compute_kpis(self, company, user):
        self.ensure_one()
        res = {}
        for tf_name, tf in self._compute_timeframes(company).items():
            digest = self.with_context(start_date=tf[0][0], end_date=tf[0][1], company=company).sudo(user.id)
            previous_digest = self.with_context(start_date=tf[1][0], end_date=tf[1][1], company=company).sudo(user.id)
            kpis = {}
            for field_name, field in self._fields.items():
                if field.type == 'boolean' and field_name.startswith(('kpi_', 'x_kpi_', 'x_studio_kpi_')) and self[field_name]:

                    try:
                        compute_value = digest[field_name + '_value']
                        previous_value = previous_digest[field_name + '_value']
                    except AccessError:  # no access rights -> just skip that digest details from that user's digest email
                        continue
                    if "delta" in field_name:
                        kpis.update({field_name: {field_name: str(timedelta(seconds=compute_value)), 'margin': 0.}})
                    else:
                        margin = self._get_margin_value(compute_value, previous_value)
                        if self._fields[field_name+'_value'].type == 'monetary':
                            converted_amount = self._format_human_readable_amount(compute_value)
                            kpis.update({field_name: {field_name: self._format_currency_amount(converted_amount, company.currency_id), 'margin': margin}})
                        else:
                            kpis.update({field_name: {field_name: compute_value, 'margin': margin}})

                res.update({tf_name: kpis})
        return res

    def _compute_timeframes(self, company):
        now = datetime.utcnow()
        # TODO remove hasattr in >=saas-12.1
        tz_name = hasattr(company, "resource_calendar_id") and company.resource_calendar_id.tz
        if tz_name:
            now = pytz.timezone(tz_name).localize(now)
        start_date = now.date()
        return {
            'today': (
                (start_date + relativedelta(days=0), start_date + relativedelta(days=1)),
                (start_date + relativedelta(days=-1), start_date + relativedelta(days=0))),
            'yesterday': (
                (start_date + relativedelta(days=-1), start_date),
                (start_date + relativedelta(days=-2), start_date + relativedelta(days=-1))),
            'lastweek': (
                (start_date + relativedelta(weeks=-1), start_date),
                (start_date + relativedelta(weeks=-2), start_date + relativedelta(weeks=-1))),
            'lastmonth': (
                (start_date + relativedelta(months=-1), start_date),
                (start_date + relativedelta(months=-2), start_date + relativedelta(months=-1))),
        }
