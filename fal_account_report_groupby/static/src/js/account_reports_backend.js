odoo.define('fal_account_report_groupby.fal_account_report_groupby', function(require) {
    "use strict";

var Account_report_generic = require('account_reports.account_report');
var rpc = require('web.rpc');

Account_report_generic.include({
    render_searchview_buttons: function () {
        var self = this;
        this._super();
        this.$searchview_buttons.find('.js_account_groupby_auto_complete').select2();
        if (this.report_options.groupby) {
            this.$searchview_buttons.find('[data-filter="move_line_fields"]').select2("val", this.report_options.groupby_ids);
        }
        this.$searchview_buttons.find('.js_account_groupby_auto_complete').on('change', function(){
            self.report_options.groupby_ids = self.$searchview_buttons.find('[data-filter="move_line_fields"]').val();
            rpc.query({
                    model: 'account.financial.html.report',
                    method: 'fal_set_groupby',
                    args: [self.financial_id, self.report_options.groupby_ids],
                })
                .then(function (result) {
                    return self.reload().then(function(){
                        self.$searchview_buttons.find('.account_groupby').click();
                    })
                });
        });
        return this.$searchview_buttons;
    },
});
});
