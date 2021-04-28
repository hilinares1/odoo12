# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
# from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class DokuController(http.Controller):
    _notify_url = '/payment/doku/notify/'
    _redirect_url = '/payment/doku/redirect/'
    _identify_url = '/payment/doku/identify/'
    _review_url = '/payment/doku/review/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from doku. """
        return_url = post.pop('return_url', '')
        return return_url

    @http.route('/payment/doku/review', type='http', auth='none', methods=['POST'], csrf=False)
    def doku_review(self, **post):
        """ Doku Review. """
        _logger.info('------ REVIEW : %s', pprint.pformat(post))  # debug

        # return ''

    @http.route('/payment/doku/identify', type='http', auth='none', methods=['POST'], csrf=False)
    def doku_identify(self, **post):
        print ("apa? 4")
        """ Doku Identify. """
        _logger.info('------ IDENTIFY : %s', pprint.pformat(post))  # debug
        paymentcode = post.get('PAYMENTCODE', '')
        if paymentcode != '':
            _logger.info('IDENTIFY - if paymentcode not null%s :' %paymentcode)
            request.env['payment.transaction'].sudo().form_feedback(post, 'doku')
        # try:
        #     self.paypal_validate_data(**post)
        # except ValidationError:
        #     _logger.exception('Unable to validate the Paypal payment')
        # return ''

    @http.route('/payment/doku/notify', type='http', auth='none', methods=['POST'], csrf=False)
    def doku_notify(self, **post):
        """ Doku Notify. """
        _logger.info('------ NOTIFY : %s', pprint.pformat(post))  # debug

        resultmsg = post.get('RESULTMSG', '')
        if resultmsg == 'SUCCESS':
            _logger.info('NOTIFY - if resultmsg == SUCCESS')
            request.env['payment.transaction'].sudo().form_feedback(post, 'doku')
        elif resultmsg == 'FAILED':
            _logger.info('NOTIFY - if resultmsg == FAILED')
            # request.env['payment.transaction'].sudo().form_feedback(post, 'doku')
        # return_url = post.pop('return_url', '')
        # if not return_url:
        #     # custom = json.loads(post.pop('merchantReturnData', '{}'))
        #     return_url = '/'
        # return werkzeug.utils.redirect(return_url)

    @http.route('/payment/doku/redirect', type='http', auth="none", methods=['POST'], csrf=False)
    def doku_redirect(self, **post):
        """ Doku Redirec. """
        _logger.info('------ REDIRECT : %s', pprint.pformat(post))

        return_url = self._get_return_url(**post)
        statuscode = post.pop('STATUSCODE', '')
        _logger.info('statuscode ->>: %s', statuscode)
        if statuscode == "0000":
            _logger.info('TRANSAKSI BERHASIL')
            return_url = '/payment/process'
        elif statuscode == "5510": # Cancel by Customer
            _logger.info('IF statuscode 5510->>: %s', statuscode)
            return_url = '/'
        elif statuscode == "5511": # Not an error, payment code has not been paid by Customer
            _logger.info('IF statuscode 5511->>: %s', statuscode)
            return_url = '/shop/payment/validate'
        else:
            _logger.info('ELSE ->>: %s', statuscode)
            return_url = '/'

        return werkzeug.utils.redirect(return_url)
