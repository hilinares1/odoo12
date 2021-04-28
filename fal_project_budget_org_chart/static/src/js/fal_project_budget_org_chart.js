odoo.define('web.FalProjectBudgetOrgChart', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var concurrency = require('web.concurrency');
var core = require('web.core');
var field_registry = require('web.field_registry');

var QWeb = core.qweb;
var _t = core._t;

var FieldFalOrgChart = AbstractField.extend({

    events: {
        "click .o_fal_project_budget_redirect": "_onFalProjectBudgetRedirect",
        "click .o_fal_project_budget_sub_redirect": "_onFalProjectBudgetSubRedirect",
    },
    /**
     * @constructor
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.dm = new concurrency.DropMisordered();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Get the chart data through a rpc call.
     *
     * @private
     * @param {integer} employee_id
     * @returns {Deferred}
     */
    _getOrgData: function (fal_project_budget_id) {
        var self = this;
        return this.dm.add(this._rpc({
            route: '/fal_project_budget/get_org_chart',
            params: {
                fal_project_budget_id: fal_project_budget_id,
            },
        })).then(function (data) {
            self.orgData = data;
        });
    },
    /**
     * @override
     * @private
     */
    _render: function () {
        if (!this.recordData.id) {
            return this.$el.html(QWeb.render("fal_project_budget_org_chart", {
                parents: [],
                children: [],
            }));
        }

        var self = this;
        return this._getOrgData(this.recordData.id).then(function () {
            self.$el.html(QWeb.render("fal_project_budget_org_chart", self.orgData));
            self.$('[data-toggle="popover"]').each(function () {
                $(this).popover({
                    html: true,
                    title: function () {
                        var $title = $(QWeb.render('fal_project_budget_orgchart_fpb_popover_title', {
                            fal_project_budget: {
                                name: $(this).data('fpb-name'),
                                id: $(this).data('fpb-id'),
                                fal_project_budget_type: $(this).data('fpb-type'),
                            },
                        }));
                        $title.on('click',
                            '.o_fal_project_budget_redirect', _.bind(self._onFalProjectBudgetRedirect, self));
                        return $title;
                    },
                    container: 'body',
                    placement: 'left',
                    trigger: 'focus',
                    content: function () {
                        var $content = $(QWeb.render('fal_project_budget_orgchart_fpb_popover_content', {
                            fal_project_budget: {
                                id: $(this).data('fpb-id'),
                                name: $(this).data('fpb-name'),
                                direct_sub_count: parseInt($(this).data('fpb-dir-subs')),
                                indirect_sub_count: parseInt($(this).data('fpb-ind-subs')),
                            },
                        }));
                        $content.on('click',
                            '.o_fal_project_budget_sub_redirect', _.bind(self._onFalProjectBudgetSubRedirect, self));
                        return $content;
                    },
                    template: QWeb.render('fal_project_budget_orgchart_fpb_popover', {}),
                });
            });
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Redirect to the project budget form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Deferred} action loaded
     */
    _onFalProjectBudgetRedirect: function (event) {
        event.preventDefault();
        var fal_project_budget_id = parseInt($(event.currentTarget).data('fal-project-budget-id'));
        return this.do_action({
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current',
            res_model: 'fal.project.budget',
            res_id: fal_project_budget_id,
        });
    },
    /**
     * Redirect to the sub project budget form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Deferred} action loaded
     */
    _onFalProjectBudgetSubRedirect: function (event) {
        event.preventDefault();
        var fal_project_budget_id = parseInt($(event.currentTarget).data('fal-project-budget-id'));
        var fal_project_budget_name = $(event.currentTarget).data('fal-project-budget-name');
        var type = $(event.currentTarget).data('type') || 'direct';
        var domain = [['parent_id', '=', fal_project_budget_id]];
        var name = _.str.sprintf(_t("Direct Child of %s"), fal_project_budget_name);
        if (type === 'total') {
            domain = ['&', ['parent_id', 'child_of', fal_project_budget_id], ['id', '!=', fal_project_budget_id]];
            name = _.str.sprintf(_t("Childs of %s"), fal_project_budget_name);
        } else if (type === 'indirect') {
            domain = ['&', '&',
                ['parent_id', 'child_of', fal_project_budget_id],
                ['parent_id', '!=', fal_project_budget_id],
                ['id', '!=', fal_project_budget_id]
            ];
            name = _.str.sprintf(_t("Indirect Childs of %s"), fal_project_budget_name);
        }
        if (fal_project_budget_id) {
            return this.do_action({
                name: name,
                type: 'ir.actions.act_window',
                view_mode: 'kanban,list,form',
                views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
                target: 'current',
                res_model: 'fal.project.budget',
                domain: domain,
            });
        }
    },
});

field_registry.add('fal_project_budget_org_chart', FieldFalOrgChart);

return FieldFalOrgChart;

});
