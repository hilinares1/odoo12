from odoo import models, api
from odoo.exceptions import UserError, ValidationError
import time
from odoo.tools.misc import formatLang
from odoo.addons.mail.models import mail_template


class ReportL10n_vnCommon(models.AbstractModel):
    _name = 'report.l10n_vn.common'
    _description = "Vietnam Common Report"

    @api.model
    def _get_lines(self, data):
        raise ValidationError(_("The method '_get_lines' has NOT been implemented."))

    @api.model
    def formatLang(self, value, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False):
        return formatLang(self.env, value, digits=digits, grouping=grouping, monetary=monetary, dp=dp, currency_obj=currency_obj)

    @api.model
    def format_date(self, date, pattern=False):
        return mail_template.format_date(self.env, date=date, pattern=pattern)

    @api.model
    def format_tz(self, dt, tz=False, format=False):
        return mail_template.format_tz(self.env, dt=dt, tz=tz, format=format)

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        doc = self.env[model].browse(self.env.context.get('active_id'))
        lines = self._get_lines(data)

        res = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'doc': doc,
            'time': time,
            'lines': lines,
            'legal_name':'',
            'formatLang': self.formatLang,
            'format_date': self.format_date,
            'format_tz': self.format_tz
        }
        if 'legal_name' in data:
            res['legal_name'] = data['legal_name']
        return res
