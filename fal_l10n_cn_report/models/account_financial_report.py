
from odoo import fields, models, api, _


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    fal_is_page2 = fields.Boolean('Page 2')

    @api.multi
    def get_lines(self, financial_report, context, currency_table, linesDicts):
        res = super(AccountFinancialReportLine, self).get_lines(
            financial_report, context, currency_table, linesDicts)
        for line in self:
            report_lines = filter(lambda x: x['id'] == line.id, res)
            # print report_lines
            for report_line in report_lines:
                report_line['fal_is_page2'] = line.fal_is_page2
        return res

# end of AccountFinancialReportLine()
