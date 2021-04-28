odoo.define('yee_odoo_studio.CalendarViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var CalendarViewContent = require('yee_odoo_studio.CalendarViewContent');
    var CalendarViewProperty = require('yee_odoo_studio.CalendarViewProperty');


    var FormViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.view.property = CalendarViewProperty;
            this.view.content = CalendarViewContent;
        },

    });

    return FormViewEdit;
});
