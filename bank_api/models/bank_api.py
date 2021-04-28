from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import hmac
import datetime
import json
import hashlib
import base64
import ast
import requests
import logging

_logger = logging.getLogger(__name__)


class AccountBankApi(models.Model):
    _name = 'account.bank.api'
    _description = 'Bank BCA API'

    name = fields.Char(string="API Name", required=True)    

    # bank_account_id = fields.Many2one("res.partner.bank", string="Bank Account", required=True)
    corporate_id = fields.Char(string="Corporate ID", required=True)
    # account_number = fields.Char(related="bank_account_id.acc_number", string="Account Number")
    api_key = fields.Char(string="API Key", required=True, help="API key from provider e.g: BCA")
    api_secret_key = fields.Char(string="API Secret Key", required=True)
    client_key = fields.Char(string="Client Key", required=True)
    client_secret_key = fields.Char(string="Client Secret Key", required=True)
    url = 'https://sandbox.bca.co.id'
    # url = fields.Char(string="Server Url", required=True)
    # journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Bank Api Status', readonly=True, copy=False, store=True, default='draft')

    @api.multi
    def button_confirm(self):
        if self.confirm_api():
            return self.write({'state': 'confirm'})

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    def confirm_api(self):
        # Get bca token
        bca_token = self.get_token_bca()

        # # Set range of date and timestamp for signature and bank statement
        # range_date = self.get_start_and_end_date()
        # start_date = range_date['start_date']
        # end_date =  range_date['end_date']
        # time_stamp = self.get_time_stamp()

        # # Get bca signature
        # bca_signature = self.get_signature_bca(bca_token,time_stamp,start_date,end_date)

        # # Get bca bank statement
        # data = self.get_bank_statement_bca(bca_signature,bca_token,time_stamp,start_date,end_date)

        if not bca_token:
            return False
        else:
            return True

    @api.model
    def bank_api_import_statement(self):

        # confirmed_bank_api = self.env['account.bank.api'].search([['state', '=', 'confirm']])
        _logger.info('Tes')
        # Check bank account and get statement (Loop)
            # for bank_api in confirmed_bank_api :
            #     bic = bank_api.bank_account_id.bank_id.bic or False
            #     if not bic:
            #         raise UserError(_('Please configure bank BIC'))
            #     elif bic == 'CENAIDJA' :
            #         bank_api.bca_procedure_get_bank_statement()
            #     else:
            #         raise UserError(_('Does not implemented yet'))

    @api.multi
    def bca_procedure_get_bank_statement(self,journal_id,account_number,start_date=False,end_date=False):
        # Get bca token
        bca_token = self.get_token_bca()
            
        # Set range of date and timestamp for signature and bank statement
        if not (start_date and end_date):
            range_date = self.get_start_and_end_date()
            start_date = range_date['start_date']
            end_date =  range_date['end_date']
        time_stamp = self.get_time_stamp()

        # _logger.info('==================================')
        # _logger.info(bca_token)
        # _logger.info(time_stamp)
        # _logger.info(account_number)
        # _logger.info(start_date)
        # _logger.info(end_date)

        # _logger.info(type(bca_token))
        # _logger.info(type(time_stamp))
        # _logger.info(type(account_number))
        # _logger.info(type(start_date))
        # _logger.info(type(end_date))

        # _logger.info('==================================')

        # Get bca signature
        bca_signature = self.create_bca_signature(bca_token,time_stamp,account_number,start_date,end_date)
        # bca_signature = self.get_signature_bca(bca_token,time_stamp,account_number,start_date,end_date)

        # Get bca bank statement
        data = self.get_bank_statement_bca(bca_signature,bca_token,time_stamp,account_number,start_date,end_date)

        # Save Record
        self.save_bank_statement(data,journal_id,start_date,end_date)

    def get_token_bca(self):
        parameter_token_bca = {'bca_url':self.url,
                           'client_key':self.client_key,
                           'client_secret_key':self.client_secret_key}

        URL = ''.join([parameter_token_bca['bca_url'],'/api/oauth/token'])
        
        encoded_key = ''.join([parameter_token_bca['client_key'],':',parameter_token_bca['client_secret_key']])
        encoded_key = encoded_key.encode()
        encoded_key = base64.b64encode(encoded_key).decode("utf-8")
   
        HEADERS ={'Authorization':''.join(['Basic ',encoded_key]),
                  'Content-Type':'application/x-www-form-urlencoded'}
        PARAMS = {'grant_type':'client_credentials'}
        try:
            r = requests.post(url = URL, headers = HEADERS, data=PARAMS)
        except:
            raise UserError(_('Check URL'))

        data = json.loads(r.text)
        if 'ErrorMessage' in data.keys():
            raise UserError(_(data['ErrorMessage']['English']))
        else:
            return data['access_token']

    def get_signature_bca(self,bca_token,time_stamp,account_number,start_date,end_date):
        parameter_signature = {'bca_url':self.url,
                               'corporate_id':self.corporate_id,
                               'account_number':account_number,
                               'start_date':start_date,
                               'end_date':end_date,
                               'bca_token':bca_token,
                               'time_stamp':time_stamp,
                               'api_secret_key':self.api_secret_key}

        URL = ''.join([parameter_signature['bca_url'],'/utilities/signature'])
        HEADERS ={'Timestamp':parameter_signature['time_stamp'],
                  'URI':''.join(['/banking/v3/corporates/',parameter_signature['corporate_id'],
                        '/accounts/',parameter_signature['account_number'],'/statements?StartDate=',
                        parameter_signature['start_date'],'&EndDate=',parameter_signature['end_date']]),
                  'AccessToken':parameter_signature['bca_token'],
                  'APISecret':parameter_signature['api_secret_key'],
                  'HTTPMethod':'GET'}
        r = requests.post(url = URL, headers = HEADERS)

        return self.parse_bca_signature(r.text)

    def get_bank_statement_bca(self,bca_signature,bca_token,time_stamp,account_number,start_date,end_date):
        parameter_statement_bca = {'bca_url':self.url,
                                   'corporate_id':self.corporate_id,
                                   'account_number':account_number,
                                   'start_date':start_date,
                                   'end_date':end_date,
                                   'bca_token':bca_token,
                                   'time_stamp':time_stamp, 
                                   'bca_signature':bca_signature, 
                                   'api_key':self.api_key}

        URL = ''.join([parameter_statement_bca['bca_url'],'/banking/v3/corporates/',parameter_statement_bca['corporate_id'],
              '/accounts/',parameter_statement_bca['account_number'],'/statements?StartDate=',
              parameter_statement_bca['start_date'],'&EndDate=',parameter_statement_bca['end_date']])

        # URL = parameter_statement_bca['bca_url']+'/banking/v3/corporates/'+parameter_statement_bca['corporate_id']+ \
        #       '/accounts/'+parameter_statement_bca['account_number']+'/statements?StartDate='+parameter_statement_bca['start_date']+ \
        #       '&EndDate='+parameter_statement_bca['end_date']
        
        HEADERS ={'X-BCA-Key':parameter_statement_bca['api_key'],
                  'X-BCA-Timestamp':parameter_statement_bca['time_stamp'],
                  'Authorization':''.join(['Bearer ',parameter_statement_bca['bca_token']]),
                  'X-BCA-Signature':parameter_statement_bca['bca_signature']}

        # HEADERS ={'X-BCA-Key':parameter_statement_bca['api_key'],
        #           'X-BCA-Timestamp':parameter_statement_bca['time_stamp'],
        #           'Authorization':'Bearer '+parameter_statement_bca['bca_token'],
        #           'X-BCA-Signature':parameter_statement_bca['bca_signature']}

        r = requests.get(url = URL, headers = HEADERS)

        data = json.loads(r.text)
        if 'ErrorMessage' in data.keys():
            raise UserError(_(data['ErrorMessage']['English']))
        else:
            return data

    def get_start_and_end_date(self):
        # today = datetime.date.today()
        # previous_date = today - relativedelta(months=1)

        today = datetime.date.today()
        previous_date_1 = today - relativedelta(years=2)
        previous_date_2 = today - relativedelta(years=2) + relativedelta(months=1)

        # start_date = datetime.date(previous_date.year, previous_date.month, 1)
        # end_date = datetime.date(today.year, today.month, 1) - relativedelta(days=1)

        start_date = datetime.date(previous_date_1.year, previous_date_1.month, 29)
        end_date = datetime.date(previous_date_2.year, previous_date_2.month, 1)

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        range_date = {'start_date':start_date,
                      'end_date':end_date}
        return range_date

    def get_time_stamp(self):
        time_stamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        time_stamp = ''.join([time_stamp,'.000']) 
        time_stamp = ''.join([time_stamp,'+00:00']) 
        return time_stamp

    def parse_bca_signature(self,texttoparse):
        parsed_text = texttoparse.split(',')
        parsed_text = parsed_text[8].split(':')
        parsed_text = parsed_text[1].strip()
        return parsed_text

    def parse_bca_statement_data(self,datatoparse):
        #Data for odoo model
        format_date = '%d/%m/%Y'
        data_year = datatoparse['StartDate'].split('-')       
        data_year = data_year[0]
        parsed_data = datatoparse['Data']
        for i in parsed_data :
            #do something if date = pending
            if i['TransactionDate'] != 'PEND':
                bca_date = ''.join([i['TransactionDate'],'/',data_year])
                # bca_date = i['TransactionDate']+'/'+data_year
                bca_date = datetime.datetime.strptime(bca_date, format_date)
                i['TransactionDate'] = bca_date.strftime('%Y-%m-%d')

            #do something if Debet
            if i['TransactionType'] == 'D':
                i['TransactionAmount'] = float(i['TransactionAmount']) * -1

        return parsed_data

    def save_bank_statement(self,data,journal_id,start_date,end_date):
        data_detail = self.parse_bca_statement_data(data)
        AccountBankStatement = self.env['account.bank.statement']
        AccountBankStatement.create({'name': ''.join(['BCA Import ',start_date.replace('-','/'),' - ',end_date.replace('-','/')]),
            'state':'open',
            'journal_id':journal_id,
            'date':data['StartDate'],
            'currency_id':data['Currency'],
            'balance_start':data['StartBalance']})
        
        last_stmnt_id = AccountBankStatement.search([],limit=1,order='id desc')

        for i in data_detail :
            if i['TransactionDate'] == 'PEND':
                account_bank_statement_line_vals = {
                    'statement_id' : last_stmnt_id.id,
                    'name': i['TransactionName'],
                    'ref':i['Trailer'],
                    'amount': i['TransactionAmount'],}
            else:
                account_bank_statement_line_vals = {
                    'statement_id' : last_stmnt_id.id,
                    'name': i['TransactionName'],
                    'date': i['TransactionDate'],                
                    'ref':i['Trailer'],
                    'amount': i['TransactionAmount'],}

            account_bank_statement_line = self.env['account.bank.statement.line'].create(account_bank_statement_line_vals)

        last_stmnt_id.write({'balance_end_real':last_stmnt_id.balance_end})

    def create_bca_signature(self,bca_token,time_stamp,account_number,start_date,end_date):
        StringToSign = ''.join(['GET:/banking/v3/corporates/',self.corporate_id,
              '/accounts/',account_number,'/statements?EndDate=',end_date,'&StartDate=',
              start_date,':',bca_token,':e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855:',time_stamp])
        bca_signature = hmac.new(self.api_secret_key.encode(),StringToSign.encode(),hashlib.sha256).hexdigest()
        return bca_signature
