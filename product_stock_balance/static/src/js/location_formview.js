odoo.define('product_stock_balance.location_formview', function (require) {
"use strict";

    var FormView = require("web.FormView");

    FormView = FormView.include({
        _setSubViewLimit: function (attrs) {
            this._super.apply(this, arguments);
            if (attrs.widget === 'locationsHierarchyWidget') {
                attrs.limit = 10000;
            }
        },
    });

    return FormView

});
