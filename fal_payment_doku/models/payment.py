# coding: utf-8

import datetime
import hashlib
import logging

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.fal_payment_doku.controllers.main import DokuController

_logger = logging.getLogger(__name__)


class AcquirerDoku(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('doku', 'Doku')])
    doku_mallid = fields.Char(
        'Doku Mall ID', groups='base.group_user',
        help='The Mall ID is used to ensure communications coming from Doku are valid and secured.')
    doku_transidmerchant = fields.Integer('Trans ID Merchant')
    doku_paymenttype = fields.Char('Doku Payment Type')
    doku_words = fields.Char('Doku WORDS')
    doku_email_account = fields.Char('Doku Email ID', required_if_provider='doku', groups='base.group_user')
    doku_payment_channel = fields.Char('Doku Payment Channel')    
    doku_difference_account_positive = fields.Many2one(
        'account.account', 'Doku Difference Account Positive')
    doku_difference_account_negative = fields.Many2one(
        'account.account', 'Doku Difference Account Negative')

    # def _get_feature_support(self):
    #     """Get advanced feature support by provider.

    #     Each provider should add its technical in the corresponding
    #     key for the following features:
    #         * fees: support payment fees computations
    #         * authorize: support authorizing payment (separates
    #                      authorization and capture)
    #         * tokenize: support saving payment data in a payment.tokenize
    #                     object
    #     """
    #     res = super(AcquirerDoku, self)._get_feature_support()
    #     res['fees'].append('paypal')
    #     return res

    @api.model
    def _get_doku_urls(self, environment):
        """ Paypal URLS """
        if environment == 'prod':
            return {
                'doku_form_url': 'https://pay.doku.com/Suite/Receive',
            }
        else:
            return {
                'doku_form_url': 'https://staging.doku.com/Suite/Receive',
            }

    @api.multi
    def doku_compute_fees(self, amount, currency_id, country_id):
        """ Compute paypal fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        # if not self.fees_active:
        #     return 0.0
        # country = self.env['res.country'].browse(country_id)
        # if country and self.company_id.country_id.id == country.id:
        #     percentage = self.fees_dom_var
        #     fixed = self.fees_dom_fixed
        # else:
        #     percentage = self.fees_int_var
        #     fixed = self.fees_int_fixed
        # fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return 0

    @api.multi
    def doku_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        MALLID = "10255259"
        SHAREKEY = "o2d9h6M6d9o3"
        AMOUNT = str("{:.2f}".format(round(values['amount'])))
        REQUESTDATETIME = (datetime.datetime.now()+datetime.timedelta(hours=7)).strftime("%Y%m%d%H%M%S")
        TRANSIDMERCHANT = values['reference']
        WORDS_GENERATE = AMOUNT+MALLID+SHAREKEY+TRANSIDMERCHANT
        WORDS = hashlib.sha1(str(WORDS_GENERATE).encode('utf-8')).hexdigest()

        doku_tx_values = dict(values)
        doku_tx_values.update({
            'BASKET'            : "Item 1,500.00,1,500.00",
            'MALLID'            : MALLID,
            'CHAINMERCHANT'     : "NA",
            'CURRENCY'          : "360",
            'PURCHASECURRENCY'  : "360",
            'AMOUNT'            : AMOUNT,
            'PURCHASEAMOUNT'    : AMOUNT,
            'TRANSIDMERCHANT'   : TRANSIDMERCHANT,
            'WORDS'             : WORDS,
            'REQUESTDATETIME'   : REQUESTDATETIME,
            'SESSIONID'         : "e67wh4l1hsif00a",
            'EMAIL'             : values.get('partner_email'),
            'NAME'              : values.get('partner_name'),
            'ADDRESS'           : values.get('partner_address'),
            'COUNTRY'           : "360",
            'CITY'              : values.get('partner_city'),
            'ZIPCODE'           : values.get('partner_zip'),
            'MOBILEPHONE'       : values.get('partner_phone') or "",
            'PAYMENTCHANNEL'    : "",
            'redirect_url'      : urls.url_join(base_url, DokuController._redirect_url),
            'notify_url'        : urls.url_join(base_url, DokuController._notify_url),
            'identify_url'      : urls.url_join(base_url, DokuController._identify_url),
            'review_url'        : urls.url_join(base_url, DokuController._review_url),
        })
        _logger.info('doku_tx_values : %s' % doku_tx_values)
        return doku_tx_values

    @api.multi
    def doku_get_form_action_url(self):
        return self._get_doku_urls(self.environment)['doku_form_url']


class TxDoku(models.Model):
    _inherit = 'payment.transaction'

    doku_txn_type = fields.Char('Transaction type')

    # Compute a unique reference for the transaction
    # Just for testing, if production don't use this method.
    @api.model
    def _compute_reference(self, values=None, prefix=None):
        res = super(TxDoku, self)._compute_reference(values, prefix)

        REQUESTDATETIME = (datetime.datetime.now() + datetime.timedelta(hours=7)).strftime("%Y%m%d%H%M%S")
        res = '%s_%s' % (REQUESTDATETIME, res)

        return res

    @api.model
    def _doku_form_get_tx_from_data(self, data):
        _logger.info('------ _doku_form_get_tx_from_data : %s' %data)
        reference = data.get('TRANSIDMERCHANT', '')
        if not reference:
            error_msg = _('Doku: received data with missing reference (%s) or missing pspReference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx
        tx = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('Doku: received data for reference %s') % (reference)
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    @api.multi
    def _doku_form_get_invalid_parameters(self, data):
        _logger.info('------ _doku_form_get_invalid_parameters')
        invalid_parameters = []
        # method for checking if has invalid parameters
        return invalid_parameters

    @api.multi
    def _doku_form_validate(self, data):
        _logger.info('------ _doku_form_validate : %s' % data)
        self.ensure_one()
        resultmsg = data.get('RESULTMSG', '')
        paymentcode = data.get('PAYMENTCODE', '')
        trans_id_merchant = data.get('TRANSIDMERCHANT', '')

        res = {
            'acquirer_reference': trans_id_merchant,
        }
        if resultmsg == 'SUCCESS':
            _logger.info('_if resultmsg SUCCESS, doku_form_validate : %s' % resultmsg)
            self._set_transaction_done()
            return self.write(res)
        elif paymentcode != '':
            _logger.info('doku_form_validate : if paymentcode not null%s :' % paymentcode)
            self._set_transaction_pending()
            return self.write(res)
        else:
            error = _('Doku: feedback error')
            _logger.info(error)
            res.update(state_message=error)
            self._set_transaction_cancel()
            return self.write(res)
