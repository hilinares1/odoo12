odoo.define('project_timesheet.fal_dashboard', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var data = require('web.data');
var pyUtils = require('web.py_utils');
var SearchView = require('web.SearchView');
var datepicker = require('web.datepicker');
var field_utils = require('web.field_utils');
var _t = core._t;
var QWeb = core.qweb;


var PlanAction = AbstractAction.extend(ControlPanelMixin, {
    events: {
        "click .oe_stat_button": "_onClickStatButton",
        'click .o_project_dashboard_summary': 'edit_summary',
        'click .js_project_dashboard_save_summary': 'save_summary',
    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.action = action;
        this.action_manager = parent;
        this.set('title', action.name || _t('Dashboard'));
        this.project_ids = [];
    },

    willStart: function () {
        var self = this;
        var view_id = this.action && this.action.search_view_id && this.action.search_view_id[0];
        var def = this
            .loadViews('account.analytic.account', this.action.context || {}, [[view_id, 'search']])
            .then(function (result) {
                self.fields_view = result.search;
            });
        return $.when(this._super(), def);
    },

    start: function(){
        var self = this;

        // find default search from context
        var search_defaults = {};
        var context = this.action.context || [];
        _.each(context, function (value, key) {
            var match = /^search_default_(.*)$/.exec(key);
            if (match) {
                search_defaults[match[1]] = value;
            }
        });

        // create searchview
        var options = {
            $buttons: $("<div>"),
            action: this.action,
            disable_groupby: true,
            search_defaults: search_defaults,
        };

        var dataset = new data.DataSetSearch(this, 'account.analytic.account');
        this.searchview = new SearchView(this, dataset, this.fields_view, options);
        this.searchview.on('search', this, this._onSearch);

        var def1 = this._super.apply(this, arguments);
        var def2 = this.searchview.appendTo($("<div>")).then(function () {
            self.$searchview_buttons = self.searchview.$buttons.contents();
        });

        return $.when(def1, def2).then(function(){
            self.searchview.do_search();
        });
    },

    edit_summary: function(e) {
        var $textarea = $(e.target).parents('.o_project_plan').find('textarea[name="summary"]');
        var height = Math.max($(e.target).parents('.o_project_plan').find('.o_project_dashboard_summary').height(), 100); // Compute the height that will be needed
        // TODO master: remove replacing <br /> (this was kept for existing data)
        var text = $textarea.val().replace(new RegExp('<br />', 'g'), '\n'); // Remove unnecessary spaces and line returns
        $textarea.height(height); // Give it the right height
        $textarea.val(text);
        $(e.target).parents('.o_project_plan').find('.o_project_dashboard_summary_edit').show();
        $(e.target).parents('.o_project_plan').find('.o_project_dashboard_summary').hide();
        $(e.target).parents('.o_project_plan').find('textarea[name="summary"]').focus();
    },
    save_summary: function(e) {
        var self = this;
        var text = $(e.target).siblings().val().replace(/[ \t]+/g, ' ');

        return this._rpc({
                model: 'account.analytic.account',
                method: 'create_note',
                args: [self.project_ids, {summary: text}],
            })
            .then(function(result){
                self.$el.find('.o_project_dashboard_summary_edit').hide();
                self.$el.find('.o_project_dashboard_summary').show();

                if (!text) {
                    var $content = $("<input type='text' class='o_input' name='summary'/>");
                    $content.attr('placeholder', _t('Add a note'));
                } else {
                    var $content = $('<span />').text(text).html(function (i, value) {
                        return value.replace(/\n/g, '<br>\n');
                    });
                }
                return $(e.target).parent().siblings('.o_project_dashboard_summary').find('> .o_project_dashboard_summary').html($content);
            });
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    do_show: function () {
        this._super.apply(this, arguments);
        this.searchview.do_search();
        this.action_manager.do_push_state({
            action: this.action.id,
            active_id: this.action.context.active_id,
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Refresh the DOM html
     * @param {string|html} dom
     * @private
     */
    _refreshPlan: function(dom){
        this.$el.html(dom);
    },
    _appendFilter: function(dom){
        var object = $('<div/>').html(dom).contents();
        this.$searchview_buttons.last().append(object);
    },
    /**
     * Call controller to get the html content
     * @private
     * @returns {Deferred}
     */

    _fetchPlan: function (domain, options = null) {
        var self = this;
        //DECLARE DATE OPTIONS
        self.report_options = options;
        self.domain_param = domain;
        if(self.report_options == null){
            //TODO fill with current date and month for default date
            self.report_options = {};
            self.report_options.option_value = "company_currency";
            self.report_options.date = {};
            self.report_options.date.date_from = "not None type, we use only date range options not single date options";
            //self.report_options.date.date_to = "2018-10-31";
            self.report_options.date.filter = "this_year";
            self.report_options.date.string = "This Financial Year";
        }

        return this._rpc({
            route:"/fal/dashboard",
            params: {domain: domain, options: self.report_options},
        }).then(function(result){
            self._refreshPlan(result.html_content);
            self._updateControlPanel(result.actions);
            self.project_ids = result.project_ids;
            if(self.$searchview_buttons.find('.js_account_report_date_filter').length <= 0){
                self._appendFilter(result.searchview_html);
                var $datetimepickers = self.$searchview_buttons.find('.js_account_reports_datetimepicker');
                var options = { // Set the options for the datetimepickers
                    locale : moment.locale(),
                    format : 'L',
                    icons: {
                        date: "fa fa-calendar",
                    },
                };
                // attach datepicker
                $datetimepickers.each(function () {
                    $(this).datetimepicker(options);
                    var dt = new datepicker.DateWidget(options);
                    dt.replace($(this));
                    dt.$el.find('input').attr('name', $(this).find('input').attr('name'));
                    if($(this).data('default-value')) { // Set its default value if there is one
                        dt.setValue(moment($(this).data('default-value')));
                    }
                });

                //assign click event
                self.$searchview_buttons.find('.js_account_report_date_filter').click(function (event) {
                    self.report_options.date.filter = $(this).data('filter');
                    var error = false;
                    if ($(this).data('filter') === 'custom') {
                        var date_from = self.$searchview_buttons.find('.o_datepicker_input[name="date_from"]');
                        var date_to = self.$searchview_buttons.find('.o_datepicker_input[name="date_to"]');
                        if (date_from.length > 0){
                            error = date_from.val() === "" || date_to.val() === "";
                            self.report_options.date.date_from = field_utils.parse.date(date_from.val());
                            self.report_options.date.date_to = field_utils.parse.date(date_to.val());
                        }
                        else {
                            error = date_to.val() === "";
                            self.report_options.date.date = field_utils.parse.date(date_to.val());
                        }
                    }
                    if (error) {
                        crash_manager.show_warning({data: {message: _t('Date cannot be empty')}});
                    } else {
                        self._fetchPlan(self.domain_param,self.report_options);
                    }
                });

                // fold custom date
                self.$searchview_buttons.find('.js_foldable_trigger').click(function (event) {
                    $(this).toggleClass('o_closed_menu o_open_menu');
                    self.$searchview_buttons.find('.o_foldable_menu').toggleClass('o_closed_menu o_open_menu');
                });
            }

            if(self.$searchview_buttons.find('.js_account_report_date_filter.selected').length <= 0){
                self.$searchview_buttons.find('.js_account_report_bool_filter').click(function (event) {
                    var option_value = $(this).data('filter');
                    self.report_options.option_value = option_value;
                    self._fetchPlan(self.domain_param,self.report_options);
                });
            }

            //hide note textarea
            self.$el.find('div.o_project_dashboard_summary_edit').hide();
            // render filter (add selected class to the options that are selected)
            self.$searchview_buttons.find('.o_account_reports_filter_date').find('a.dropdown-toggle')[0].lastChild.nodeValue = " " + result.searchview_options.date.string;
            _.each(self.report_options, function(k) {
                self.$searchview_buttons.find('.js_account_report_date_filter').removeClass('selected');
                self.$searchview_buttons.find('.js_account_report_bool_filter').removeClass('selected');
                if (self.report_options.option_value) {
                    self.$searchview_buttons.find('[data-filter="'+self.report_options.option_value+'"]').addClass('selected');
                }
                if (k!== null && k.filter !== undefined) {
                    self.$searchview_buttons.find('[data-filter="'+k.filter+'"]').addClass('selected');
                }
            });
        });
    },

    _updateControlPanel: function (buttons) {
        // set actions button
        if (this.$buttons) {
            this.$buttons.off().destroy();
        }
        var buttons = buttons || [];
        this.$buttons = $(QWeb.render("project.plan.ControlButtons", {'buttons': buttons}));
        this.update_control_panel({
            cp_content: {
                $buttons: this.$buttons,
                $searchview: this.searchview.$el,
                $searchview_buttons: this.$searchview_buttons,
            },
            searchview: this.searchview,
        });

    },

    _onClickStatButton: function (event) {
        var self = this;
        var data = $(event.currentTarget).data();
        var parameters = {
            domain: data.domain || [],
            res_model: data.resModel,
        }
        if (data.resId) {
            parameters['res_id'] = data.resId;
        }
        return this._rpc({
            route:"/fal/dashboard/action",
            params: parameters,
        }).then(function(action){
            self.do_action(action);
        });
    },

    _onSearch: function (event) {
        event.stopPropagation();
        var session = this.getSession();
        // group by are disabled, so we don't take care of them
        var result = pyUtils.eval_domains_and_contexts({
            domains: event.data.domains,
            contexts: [session.user_context].concat(event.data.contexts)
        });

        this._fetchPlan(result.domain);
    },
});

core.action_registry.add('fal.dashboard', PlanAction);

});
