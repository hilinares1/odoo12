odoo.define('fal_financial_report.fal_financial_report', function(require) {
    "use strict";

var Account_report_generic = require('account_reports.account_report');

Account_report_generic.include({
    render_searchview_buttons: function () {
        var self = this;
        this._super();
        this.$searchview_buttons.find('.js_account_user_auto_complete').select2();
        if (this.report_options.user) {
            this.$searchview_buttons.find('[data-filter="res_users"]').select2("val", this.report_options.user_ids);
        }
        this.$searchview_buttons.find('.js_account_user_auto_complete').on('change', function(){
            self.report_options.user_ids = self.$searchview_buttons.find('[data-filter="res_users"]').val();
            return self.reload().then(function(){
                self.$searchview_buttons.find('.account_user_filter').click();
            })
        });
        return this.$searchview_buttons;
    },
});
});
