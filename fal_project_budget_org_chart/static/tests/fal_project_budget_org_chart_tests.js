odoo.define('fal_project_budget_org_chart.tests', function (require) {
"use strict";

var FormView = require('web.FormView');
var testUtils = require("web.test_utils");

var createView = testUtils.createView;

QUnit.module('fal_project_budget_org_chart', {
    before: function () {
        this.data = {
            fal_project_budget: {
                fields: {
                    child_ids: {string: "one2many Subordinates field", type: "one2many", relation: 'fal_project_budget'},
                },
                records: [{
                    id: 1,
                    child_ids: [],
                }]
            }
        };
    },
}, function () {
    QUnit.test("fal project budget org chart: empty render", function (assert) {
        assert.expect(2);

        var form = createView({
            View: FormView,
            model: 'fal_project_budget',
            data: this.data,
            arch:
                '<form>' +
                    '<field name="child_ids" widget="fal_project_budget_org_chart"/>' +
                '</form>',
            res_id: 1,
            mockRPC: function (route, args) {
                if (route === '/fal_project_budget/get_org_chart') {
                    assert.ok('project_budget_id' in args, "it should have 'fal_project_budget_id' as argument");
                    return $.when({
                        children: [],
                        parents: [],
                        parents_more: false,
                    });
                }
                return this._super(route, args);
            }
        });
        assert.strictEqual(form.$('[name="child_ids"]').children().length, 1, "the chart should have 1 child");
        form.destroy();
    });
    QUnit.test("fal project budget org chart: basic render", function (assert) {
        assert.expect(3);

        var form = createView({
            View: FormView,
            model: 'fal_project_budget',
            data: this.data,
            arch:
                '<form>' +
                    '<sheet>' +
                        '<div id="o_fal_project_budget_container"><div id="o_fal_project_budget_main">' +
                            '<div id="o_fal_project_budget_right">' +
                                '<field name="child_ids" widget="fal_project_budget_org_chart"/>' +
                            '</div>' +
                        '</div></div>' +
                    '</sheet>' +
                '</form>',
            res_id: 1,
            mockRPC: function (route, args) {
                if (route === '/fal_project_budget/get_org_chart') {
                    assert.ok('fal_project_budget_id' in args, "it should have 'fal_project_budget_id' as argument");
                    return $.when({
                        children: [{
                            direct_sub_count: 0,
                            indirect_sub_count: 0,
                            fal_project_budget_type: 'View-Root',
                            link: 'fake_link',
                            name: 'Fake Sub Project Budget',
                            id: 2,
                        }],
                        parents: [],
                        parents_more: false,
                        self: {
                            direct_sub_count: 1,
                            id: 1,
                            indirect_sub_count: 1,
                            fal_project_budget_type: 'Root',
                            link: 'fake_link',
                            name: 'Fake Root Project Budget',
                        }
                    });
                }
                return this._super(route, args);
            }
        });
        assert.strictEqual(form.$('.o_org_chart_entry_sub').length, 1,
            "the chart should have 1 subordinate");
        assert.strictEqual(form.$('.o_org_chart_entry_self').length, 1,
            "the current project budget should only be displayed once in the chart");
        form.destroy();
    });
    QUnit.test("fal project budget org chart: basic parent render", function (assert) {
        assert.expect(4);

        var form = createView({
            View: FormView,
            model: 'fal_project_budget',
            data: this.data,
            arch:
                '<form>' +
                    '<sheet>' +
                        '<div id="o_fal_project_budget_container"><div id="o_fal_project_budget_main">' +
                            '<div id="o_fal_project_budget_right">' +
                                '<field name="child_ids" widget="fal_project_budget_org_chart"/>' +
                            '</div>' +
                        '</div></div>' +
                    '</sheet>' +
                '</form>',
            res_id: 1,
            mockRPC: function (route, args) {
                if (route === '/fal_project_budget/get_org_chart') {
                    assert.ok('fal_project_budget_id' in args, "should have 'fal_project_budget_id' as argument");
                    return $.when({
                        children: [{
                            direct_sub_count: 0,
                            indirect_sub_count: 0,
                            fal_project_budget_type: 'View-Root',
                            link: 'fake_link',
                            name: 'Fake Sub Project Budget',
                            id: 2,
                        }],
                        managers: [{
                            direct_sub_count: 1,
                            id: 1,
                            indirect_sub_count: 2,
                            fal_project_budget_type: 'View-Root',
                            link: 'fake_link',
                            name: 'Antoine Langlais',
                        }],
                        managers_more: false,
                        self: {
                            direct_sub_count: 1,
                            id: 1,
                            indirect_sub_count: 1,
                            fal_project_budget_type: 'View-Root',
                            link: 'fake_link',
                            name: 'John Smith',
                        }
                    });
                }
                return this._super(route, args);
            }
        });
        assert.strictEqual(form.$('.o_org_chart_group_up .o_org_chart_entry_parent').length, 1, "the chart should have 1 parent");
        assert.strictEqual(form.$('.o_org_chart_group_down .o_org_chart_entry_sub').length, 1, "the chart should have 1 child");
        assert.strictEqual(form.$('.o_org_chart_entry_self').length, 1, "the chart should have only once the current project budget");
        form.destroy();
    });
});

});