openerp.account_dynamic_gl = function (instance) {
'use strict';

// var ActionManager = instance('web.ActionManager');
// var data = instance('web.data');
// var Dialog = instance('web.Dialog');
// var FavoriteMenu = instance('web.FavoriteMenu');
// var form_common = instance('web.form_common');
// var pyeval = instance('web.pyeval');
// var ViewManager = instance('web.ViewManager');


// var ajax = instance('web.ajax');


// var base = instance('web_editor.base');
// instance.web.Model = instance.web.Model;
// instance.web.Session = instance.web.Session;

// instance.web.round_decimals = instance.web.round_decimals;

var _t = instance.web._t;
var QWeb = instance.web.qweb;

// var exports = {};

    instance.web.DynamicMain = instance.web.Widget.extend({
    template:'DynamicMain',

    init : function(view, code){
        this._super(view, code);
    },

	start : function(){
        new instance.web.ControlButtons(this).appendTo(this.$('.ControlSection'));
        new instance.web.UserFilters(this).appendTo(this.$('.FiltersSection'));
	    }, //start

    }); //DynamicMain

instance.web.UserFilters = instance.web.Widget.extend({
    template:'UserFilters',
    events: {
        // events binding
        'click input.showCurrency': 'show_options',
        'click input.notshowCurrency': 'hide_options',
        'click input#trans_date': 'show_trans_date_options',
        'click input#set_date': 'show_set_date_options',
        'click input#set_curr_date': 'show_set_curr_date_options',
        },

    alerta: function(){
        alert('s')
    },

    init : function(view, code){
		this._super(view, code);
		},

	start : function(){
	    var self = this;

	    // Calling common template. for both company and Date filter
	    self.$el.append(QWeb.render('CompanyDatefilterLine'));

	    // Getting date filters
	    // Add filter type section
	    self.$el.find('.date-filters').append(QWeb.render('DatefilterSelectionLine'));
	    self.$el.find('.dynamic-datefilter-multiple').select2({
	        placeholder:'Select filter type...',
	        maximumSelectionSize: 1,
	        }).val('this_month').trigger('change');

        // Getting companies from company master
        var company_ids = [];
        var current_company = self.session.company_id
        var allowed_companies = []
        var company_filter = []
        if(!(self.session.is_admin)){
            allowed_companies.push(parseInt(self.session.company_id));
            company_filter = [['id','in',allowed_companies]];
        }
        var a = new instance.web.Model('res.company')
            .query(['name','id'])
            .filter(company_filter)
            .all()
            .then(function(results){
            _(results).each(function (item) {
                company_ids.push({'name':item.name,'code':item.id})
                }) //each
            self.$el.find('.multi-companies').append(QWeb.render('MultiCompanies', {'companies': company_ids}));
            self.$el.find('.dynamic-company-multiple').select2({
                placeholder:'Select companies...',
                }).val(current_company).trigger('change');
            }); //query

        // Date from and To
	    self.$el.append(QWeb.render('DateLine'));

        // No need to fetch from DB. Just templates
	    self.$el.append(QWeb.render('TargetAccountsLine'));
	    self.$el.append(QWeb.render('SortByInitialBalanceLine'));
	    self.$el.append(QWeb.render('ShowSecondaryCurrency'));
        // self.$el.find('.notshowCurrency').click(function(e){
	     //   self.$el.find('.secondary_exchange').addClass('hide')
        // });
        // self.$el.find('.showCurrency').click(function(e){
	     //   self.$el.find('.secondary_exchange').removeClass('hide')
        // });

        // Getting partners from partner master
	    var partners = [];
        var a = new instance.web.Model('res.partner').query(['name','id']).all().then(function(results){
            _(results).each(function (item) {
                partners.push({'name':item.name,'id':item.id})
                }) //each
            self.$el.append(QWeb.render('PartnersLine', {'partners': partners}));
            self.$el.find('.dynamic-partner-multiple').select2({
                placeholder:'Select partners...',
                minimumResultsForSearch: 5
                });

            }); //query

	    // Getting journals from journal master
	    var journals = [];
	    var journal_ids = []
        var a = new instance.web.Model('account.journal').query(['name','id','code']).all().then(function(results){
            _(results).each(function (item) {
                journals.push({'name':item.name,'code':item.id,'short_code':item.code})
                journal_ids.push(parseInt(item.id))
                }) //each
            self.$el.append(QWeb.render('JournalsLine', {'journals': journals}));
            self.$el.find('.dynamic-journal-multiple').select2({
                placeholder:'Select journals...',
                minimumResultsForSearch: 5
                }).val(journal_ids).trigger('change');

            }); //query

        self.$el.append(QWeb.render('OperatingUnits'));
        var units = [];
        var u = new instance.web.Model('operating.unit').query(['name','id','code']).all().then(function(results){
            _(results).each(function (item) {
                units.push({'name':item.name,'code':item.id,'short_code':item.code})

                }) //each
            self.$el.find('.normal_unit').append(QWeb.render('OperatingUnitsLine', {'units': units}));
            self.$el.find('.dynamic-unit-multiple').select2({
                placeholder:'Select Operating Unit...',
                minimumResultsForSearch: 5
                });

            }); //query

        self.$el.append(QWeb.render('Account'));

        var accounts = [];
        var a = new instance.web.Model('account.account').query(['name','id','code']).all().then(function(results){
            _(results).each(function (item) {
                accounts.push({'name':item.name,'code':item.id,'short_code':item.code})

                }) //each
            if(accounts.length == 0) {
                self.getParent().$el.find('button').hide();
                self.do_notify(_("Insufficient data"), "No chart of account defined for this company");
            }
            self.$el.find('.normal_acc').append(QWeb.render('AccountsLine', {'accounts': accounts}));
            self.$el.find('.dynamic-account-multiple').select2({
                placeholder:'Select accounts...',
                minimumResultsForSearch: 5
                });

            }); //query

        // Getting account tags from tags master
	    var account_tags = [];
        var a = new instance.web.Model('account.account.tag').query(['name','id']).all().then(function(results){
            _(results).each(function (item) {
                account_tags.push({'name':item.name,'code':item.id})

                }) //each
            self.$el.find('.normal_acc_tags').append(QWeb.render('AccountTagsLine', {'acc_tags': account_tags}));
            self.$el.find('.dynamic-acc-tags-multiple').select2({
                placeholder:'Select account tags...',
                });
            }); //query

        self.$el.append(QWeb.render('Analytic'));

        // Getting analytic account from master
	    var analytic_accounts = [];
        var a = new instance.web.Model('account.analytic.account').query(['name','id']).all().then(function(results){
            _(results).each(function (item) {
                analytic_accounts.push({'name':item.name,'code':item.id})

                }) //each
            self.$el.find('.analytic_acc').append(QWeb.render('AnalyticAccountLine', {'analytic_accs': analytic_accounts}));
            self.$el.find('.dynamic-analytic-acc-multiple').select2({
                placeholder:'Select analytic accounts...',
                });
            }); //query

//        //Getting analytic account analytic tags from tags master
//	    var analytic_account_tags = [];
//        var a = new Model('account.analytic.tag').query(['name','id']).all().then(function(results){
//            _(results).each(function (item) {
//                analytic_account_tags.push({'name':item.name,'code':item.id})
//
//                }) //each
//            self.$el.find('.analytic_acc_tags').append(QWeb.render('AnalyticTagsLine', {'analytic_acc_tags': analytic_account_tags}));
//            self.$el.find('.dynamic-analytic-acc-tags-multiple').select2({
//                placeholder:'Select analytic tags...',
//                });
//            }); //query

        var date = new Date();
        var y = date.getFullYear();
        var m = date.getMonth();
        var d = date.getDay();


        self.$el.find('#from_date').datepicker({
                icons: {
                    time: "fa fa-clock-o",
                    date: "fa fa-calendar",
                    up: "fa fa-arrow-up",
                    down: "fa fa-arrow-down"
                },
                viewMode: 'days',
                format: 'DD/MM/YYYY',
                defaultDate: new Date(y, m, 1)
                });
        self.$el.find('#to_date').datepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: 'DD/MM/YYYY',
                    defaultDate: new Date(y, m+1, 0)
                });
        self.$el.find('#curr_rate_date').datepicker({
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-arrow-up",
                        down: "fa fa-arrow-down"
                    },
                    viewMode: 'days',
                    format: 'DD/MM/YYYY',
                    defaultDate: new Date(y, m, d)
                });
        //
	    }, //start

    /* Used to show options */
	show_options: function(event){
        var self = this;
        self.$el.find('.secondary_exchange').removeClass("hide");
    },

    /* Used to hide options */
	hide_options: function(event){
        var self = this;
        self.$el.find('.secondary_exchange').addClass("hide");
    },

    /* Used to hide the curr_rate_date and curr_rate*/
    show_trans_date_options: function(event){
        var self = this;
        self.$el.find('.fourth_exchange').addClass("hide");
        self.$el.find('.third_exchange').addClass("hide");
    },

    /* Used to show the curr_rate_date and hide curr_rate*/
    show_set_date_options: function(event){
        var self = this;
        self.$el.find('.fourth_exchange').addClass("hide");
        self.$el.find('.third_exchange').removeClass("hide");
    },

     /* Used to hide the curr_rate_date and show curr_rate*/
    show_set_curr_date_options: function(event){
        var self = this;
        self.$el.find('.fourth_exchange').removeClass("hide");
        self.$el.find('.third_exchange').addClass("hide");
    }


	}); //UserFilters

instance.web.ControlButtons = instance.web.Widget.extend({
    template:'ControlButtons',
    events: {
        'click #filter_button': 'filter_button_click',
        'click #apply_button': 'apply_button_click',
        'click #expand_all': 'apply_button_expand_all',
        'click #merge_all': 'apply_button_merge_all',
        'click #pdf_button': 'download_pdf',
        'click #xlsx_button': 'download_xlsx'
    },

    init : function(view, code){
		this._super(view, code);
		},

	start : function(){
	    var self = this;
	    $("#expand_all").toggle();
        $("#merge_all").toggle();
	    }, //start

	filter_button_click : function(event){
        $(".account_filter").slideToggle("slow",function(){
            $("#apply_button").toggle();
            });
	    },

	apply_button_expand_all : function(event){
	    $('.move-sub-line').collapse('show');
	},

	apply_button_merge_all : function(event){
	    $('.move-sub-line').collapse('hide');
	},

	download_pdf : function(event){
	    var self = this;
	    var filter = self.get_filter_datas();

	    return new instance.web.Model('report.account.dynamic.report_generalledger').call('render_html',[filter,'pdf']).then(function(result){
                var action = {
                    'type': 'ir.actions.report.xml',
                    'report_type': 'qweb-pdf',
                    'report_name': 'account.report_generalledger',
                    'report_file': 'account.report_generalledger',
                    'data': result,
                    'context': {'active_model':'account.report.general.ledger',
                                'landscape':1},
                    'display_name': 'General Ledger',
                };
                return self.do_action(action);
            });
	},

	download_xlsx : function(event){
	    var self = this;
	    var filter = self.get_filter_datas();

	    new instance.web.Model('account.account').call('create_wizard',[filter,]).then(function(wizard){
	            var context=  {'active_model': 'general.ledger.webkit',
                                 'xls_export':1}
                new instance.web.Model('general.ledger.webkit').call('xls_export', [[wizard],], {context:context}).then(function(result) {
                    console.log(result);
                    result['context'] = context;
                    return self.do_action(result)
                });
            });
	},

	apply_button_click : function(event){
	    var self = this;
	    var output = self.get_filter_datas();

	    // Hide filter sections when apply filter button
        $(".account_filter").slideToggle("slow",function(){
            $("#apply_button").toggle();
            $("#expand_all").show();
            $("#merge_all").show();
            });

	    var final_html = new instance.web.Model('report.account.dynamic.report_generalledger').call('render_html',[output]).then(function(result){
                $(".DataSection").empty();
                new instance.web.AccountContents(self,result).appendTo($(".DataSection"));
            });
	},

    str_to_date: function(str) {
        if(!str) {
            return str;
        }
        var regex = /^(\d\d)\/(\d\d)\/(\d\d\d\d)$/;
        console.log(str);
        var res = regex.exec(str);
        if ( !res ) {
            throw new Error("'" + str + "' is not a valid date");
        }
        return res[3] + "-" + res[1]+ "-" + res[2];
    },

	get_filter_datas : function(){
	    var self = this;
	    var output = {}

        // Get journals
	    var journal_ids = [];
	    var journal_list = $(".dynamic-journal-multiple").select2('data')
	    for (var i=0; i < journal_list.length; i++){
	        journal_ids.push(parseInt(journal_list[i].id))
	        }
	    output.journal_ids = journal_ids
	    // Get partners
	    var partner_ids = [];
	    var partner_list = $(".dynamic-partner-multiple").select2('data')
	    for (var i=0; i < partner_list.length; i++){
	        partner_ids.push(parseInt(partner_list[i].id))
	        }
	    output.partner_ids = partner_ids
        // Get ous
        var ou_ids = [];
	    var ou_list = $(".dynamic-ou-multiple").select2('data')
	    for (var i=0; i < ou_list.length; i++){
	        ou_ids.push(parseInt(ou_list[i].id))
	        }
	    output.ou_ids = ou_ids
        // Get companies
        var company_ids = [];
	    var company_list = $(".dynamic-company-multiple").select2('data')
	    for (var i=0; i < company_list.length; i++){
	        company_ids.push(parseInt(company_list[i].id))
	        }
	    output.company_ids = company_ids

	    // Get accounts
        var account_ids = [];
	    var account_list = $(".dynamic-account-multiple").select2('data')
	    for (var i=0; i < account_list.length; i++){
	        account_ids.push(parseInt(account_list[i].id))
	        }
	    output.account_ids = account_ids

        // Get operating units
        var units = [];
	    var unitlist = $(".dynamic-unit-multiple").select2('data')
	    for (var i=0; i < unitlist.length; i++){
	        units.push(parseInt(unitlist[i].id))
	        }
	    output.unit_ids = units

	    // Get account tags
        var account_tag_ids = [];
	    var account_tag_list = $(".dynamic-acc-tags-multiple").select2('data')
	    for (var i=0; i < account_tag_list.length; i++){
	        account_tag_ids.push(parseInt(account_tag_list[i].id))
	        }
	    output.account_tag_ids = account_tag_ids

	    // Get analytic account
        var account_analytic_ids = [];
	    var account_analytic_list = $(".dynamic-analytic-acc-multiple").select2('data')
	    for (var i=0; i < account_analytic_list.length; i++){
	        account_analytic_ids.push(parseInt(account_analytic_list[i].id))
	        }
	    output.analytic_account_ids = account_analytic_ids

	    // Get analytic account tags
        var account_analytic_tags_ids = [];
	    var account_analytic_tags_list = $(".dynamic-analytic-acc-tags-multiple").select2('data')
	    for (var i=0; i < account_analytic_tags_list.length; i++){
	        account_analytic_tags_ids.push(parseInt(account_analytic_tags_list[i].id))
	        }
	    output.analytic_tag_ids = account_analytic_tags_ids

	    // Get Date filters
	    output.date_filter = $(".dynamic-datefilter-multiple").select2('data')

	    // Get dates
        if($("#from_date")[0].value){
	        var from_date = self.str_to_date($("#from_date")[0].value)
            output.date_from = from_date;
        }
        if($("#to_date")[0].value){
	        var to_date = self.str_to_date($("#to_date")[0].value)
            output.date_to = to_date
        }
         if($("#curr_rate_date")[0].value){
	        var curr_rate_date = self.str_to_date($("#curr_rate_date")[0].value)
            output.curr_rate_date = curr_rate_date
        }

        // Get checkboxes
	    if ($("#all_posted_entries").is(':checked')){ // All posted
	        output.all_posted = true
	        }else{output.all_posted = false}
	    if ($("#all_entries").is(':checked')){ // All entries
	        output.all_entries = true
	        }else{output.all_entries = false}
	    if ($("#all_datas").is(':checked')){ // All accounts
	        output.all_datas = true
	        }else{output.all_datas = false}
	    if ($("#all_movements").is(':checked')){ // All with movement
	        output.all_movements = true
	        }else{output.all_movements = false}
	    if ($("#all_balance_not_zero").is(':checked')){ // All with non zero
	        output.all_balance_not_zero = true
	        }else{output.all_balance_not_zero = false}
	    if ($("#by_date").is(':checked')){
	        output.by_date = true
	        }else{output.by_date = false}
	    if ($("#by_journal_and_partner").is(':checked')){
	        output.by_journal_and_partner = true
	        }else{output.by_journal_and_partner = false}
	    if ($("#initial_balance_yes").is(':checked')){
	        output.initial_balance = true
	        }else{output.initial_balance = false}
        if ($("#showCurrency").is(':checked')){
	        output.show_currency = true
	        }else{output.show_currency = false}
        if ($("#trans_date").is(':checked')){
	        output.trans_date = true
	        }else{output.trans_date = false}
        if ($("#set_date").is(':checked')){
	        output.set_date = true
	        }else{output.set_date = false}
        if ($("#set_curr_date").is(':checked')){
	        output.set_curr_date = true
	        }else{output.set_curr_date = false}
        if($("#curr_rate")[0].value){
	        output.curr_rate = $("#curr_rate")[0].value
        }else{output.curr_rate = 0.00}

        return output
	},

	}); //ControlButtons

instance.web.AccountContents = instance.web.Widget.extend({
    template:'AccountContents',
    events: {
        // events binding
        'click .view-source': 'view_move_line',
        'click .view-invoice': 'view_invoice'
        },

    init : function(view, code){
		this._super(view, code);
		this.result = JSON.parse(code); // To convert string to JSON
		},
	start : function(){
	    var self = this;

	    }, //start

	format_currency_no_symbol: function(amount, precision){
	    var decimals = precision;
	    if (typeof amount === 'number') {
            amount = instance.web.round_decimals(amount,decimals).toFixed(decimals);
            amount = instance.web.format_value(instance.web.round_decimals(amount, decimals), { type: 'float', digits: [69, decimals]});
        }

        return amount;
	},

	format_currency_with_symbol: function(amount, precision, symbol, position){
	    var decimals = precision;
	    if (typeof amount === 'number') {
            amount = instance.web.round_decimals(amount,decimals).toFixed(decimals);
            amount = instance.web.format_value(instance.web.round_decimals(amount, decimals), { type: 'float', digits: [69, decimals]});
        }
        if (position === 'after') {
            return amount + ' ' + (symbol || '');
        } else {
            return (symbol || '') + ' ' + amount;
        }

        return amount;
	},


	/* Used to redirect to move record */
	view_move_line : function(event){
        var self = this;
        var model_obj = new instance.web.Model('account.move');
        model_obj.call('get_formview_action', [$(event.currentTarget).data('move-id'), {}]).then(function(action){
            self.do_action(action);
            self.do_notify(_("Redirected"), "Window has been redirected");
        });
        },

    /* Used to redirect to invoice record */
    view_invoice : function(event){
        var self = this;

        var generalLedgerModel = new instance.web.Model('report.account.dynamic.report_generalledger');

        generalLedgerModel.call('get_invoice_details',[$(event.currentTarget).data('lref')])
            .then(function(res_id){
                if (res_id){
                    var model_obj = new instance.web.Model('account.invoice');
                    model_obj.call('get_formview_action', [res_id, {}]).then(function(action){
                        self.do_action(action);
                    });
                    self.do_notify(_("Redirected"), "Window has been redirected");
                }
            });

        }, //view_invoice

	}); //AccountContents


instance.web.client_actions.add("dynamic.gl.report", "instance.web.DynamicMain");
};
