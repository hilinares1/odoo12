odoo.define('yee_odoo_studio.PivotViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var PivotViewContent = require('yee_odoo_studio.PivotViewContent');
    var PivotViewProperty = require('yee_odoo_studio.PivotViewProperty');


    var FormViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            // this.sortData = [["._wGroupInner > tbody", "._wGroupInner > tbody"]
            //     , ["._wComTag ._wSortable,.o_form_sheet,.o_form_nosheet,._wPage", ".o_form_sheet,.o_form_nosheet,._wPage"],
            //     , ["._wComField ._wSortable", "._wGroupInner > tbody"],
            //     , ["._wFields", "._wGroupInner > tbody"],
            // ];
            // this.useSubProp = false;
            this.view.property = PivotViewProperty;
            this.view.content = PivotViewContent;
        },

    });

    return FormViewEdit;
});
