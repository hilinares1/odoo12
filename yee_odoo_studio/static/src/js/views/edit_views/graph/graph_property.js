odoo.define('yee_odoo_studio.GraphViewProperty', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');


    var GraphViewProperty = Base.PropertyBase.extend({
        start: function () {
            this._super();
            const {view} = this.property;
            view.graph = {};
            view.graph.graph = [];
        },
        renderTab: function () {},
    });

    return GraphViewProperty;
});
