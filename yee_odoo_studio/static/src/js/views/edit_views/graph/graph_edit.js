odoo.define('yee_odoo_studio.GraphViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var GraphViewContent = require('yee_odoo_studio.GraphViewContent');
    var GraphViewProperty = require('yee_odoo_studio.GraphViewProperty');


    var GraphViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.view.property = GraphViewProperty;
            this.view.content = GraphViewContent;
        },

    });

    return GraphViewEdit;
});
