odoo.define('yee_odoo_studio.ListViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var ListEditContent = require('yee_odoo_studio.ListEditContent');
    var ListEditProperty = require('yee_odoo_studio.ListEditProperty');


    var ListViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.sortData = [["tr, ._wFields", "tr"], ["._wSortable", "tr"]];
            this.view.property = ListEditProperty;
            this.view.content = ListEditContent;
        },
    });

    return ListViewEdit;
});
