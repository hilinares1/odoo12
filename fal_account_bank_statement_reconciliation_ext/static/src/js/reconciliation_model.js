odoo.define('fal_account_bank_statement_reconciliation_ext.ReconciliationModel', function (require) {
"use strict";

var BasicModel = require('web.BasicModel');
var field_utils = require('web.field_utils');
var utils = require('web.utils');
var session = require('web.session');
var CrashManager = require('web.CrashManager');
var core = require('web.core');
var _t = core._t;

var ReconciliationModel = require('account.ReconciliationModel');

var Fal_Reconciliation = {
    quickCreateFields: ['account_id', 'amount', 'analytic_account_id', 'label', 'tax_id', 'product_id', 'force_tax_included', 'analytic_tag_ids'],

    _formatQuickCreate: function (line, values) {
        var self = this;
        // Add journal to created line
        if (values && values.product_id === undefined && line && line.createForm && line.createForm.product_id) {
            values.product_id = line.createForm.product_id;
        }
        return this._super(line, values)
    },

    quickCreateProposition: function (handle, reconcileModelId) {
        var line = this.getLine(handle);
        var reconcileModel = _.find(this.reconcileModels, function (r) {return r.id === reconcileModelId;});
        var fields = ['account_id', 'amount', 'amount_type', 'analytic_account_id', 'journal_id', 'label', 'force_tax_included', 'tax_id', 'analytic_tag_ids', 'product_id'];
        this._blurProposition(handle);

        var focus = this._formatQuickCreate(line, _.pick(reconcileModel, fields));
        focus.reconcileModelId = reconcileModelId;
        line.reconciliation_proposition.push(focus);

        if (reconcileModel.has_second_line) {
            var second = {};
            _.each(fields, function (key) {
                second[key] = ("second_"+key) in reconcileModel ? reconcileModel["second_"+key] : reconcileModel[key];
            });
            focus = this._formatQuickCreate(line, second);
            focus.reconcileModelId = reconcileModelId;
            line.reconciliation_proposition.push(focus);
            this._computeReconcileModels(handle, reconcileModelId);
        }
        line.createForm = _.pick(focus, this.quickCreateFields);
        return this._computeLine(line);
    },
};

ReconciliationModel.StatementModel.include(Fal_Reconciliation);

});
