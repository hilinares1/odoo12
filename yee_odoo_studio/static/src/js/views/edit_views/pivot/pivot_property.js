odoo.define('yee_odoo_studio.PivotViewProperty', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var FieldBasic = require('yee_odoo_studio.FieldBasic');


    var PivotViewProperty = Base.PropertyBase.extend({
        start: function () {
            this._super();
            const {property, view} = this.property;
            property.display_quantity = {label: "Display Count", widget: FieldBasic.Checkbox};
            property.disable_linking = {label: "Allow Link to List View", widget: FieldBasic.Checkbox};
            property.stacked = {label: "Stacked", widget: FieldBasic.Checkbox};
            view.pivot = {};
            view.pivot.pivot = ["disable_linking", "display_quantity", "stacked"];
        },
        renderTab: function () {},
        renderElement: function () {
            const {viewInfo} = this.props;
            this._super();
            this.renderProperty(viewInfo.arch);
        },
    });

    return PivotViewProperty;
});
