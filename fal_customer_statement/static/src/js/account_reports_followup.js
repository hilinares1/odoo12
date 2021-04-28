odoo.define('fal_customer_statement.account_reports_followup', function (require) {
'use strict';

var account_reports_followup = require('accountReports.FollowupFormController');

	account_reports_followup.include({
		//directly override this method to show mail.compose.message
		_onSendMail: function(e) {
	        var self = this;
		        var partnerID = this.model.get(this.handle, {raw: true}).res_id;
		        this.options = {};
		        this.options.partner_id = partnerID;

	        var body = this._rpc({
		            model: 'account.followup.report',
		            method: 'get_body_html',
		            args: [partnerID, this.options],
		        })
	        	.then(function (result) {
	        	self.mail_compose_wizard(result);
	        	});
    	},

    	mail_compose_wizard: function(result){
	        this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'mail.compose.message',
                src_model: 'account.followup.report',
                multi: "True",
                target: 'new',
                key2: 'client_action_multi',
                context: result,
                views: [[false, 'form']],
            });

    	},

	});
});