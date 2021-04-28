odoo.define('yee_odoo_studio.FormViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var FormEditContent = require('yee_odoo_studio.FormEditContent');
    var FormEditProperty = require('yee_odoo_studio.FormEditProperty');


    var FormViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.sortData = [["._wGroupInner > tbody", "._wGroupInner > tbody"]
                , ["._wComTag ._wSortable,.o_form_sheet,.o_form_nosheet,._wPage", ".o_form_sheet,.o_form_nosheet,._wPage"],
                , ["._wComField ._wSortable", "._wGroupInner > tbody"],
                , ["._wFields", "._wGroupInner > tbody"],
            ];
            this.useSubProp = false;
            this.view.property = FormEditProperty;
            this.view.content = FormEditContent;
        },
        onCloseSubView: function (nodeId, viewType) {
            this.ref.content.closeSubView(nodeId, viewType)
        },
        onClickNode: function (node) {
            if (this.useSubProp) {
                this._renderProperty(true);
                this.useSubProp = false;
            }
            this._super(node);
        },
        useSubPropertyView: function (subProperty) {
            if (!this.useSubProp) {
                const {reloadProperty} = this.props;
                subProperty._renderProperty(true);
                this.useSubProp = true;
                this.ref.property = subProperty.ref.property;
                reloadProperty();
            }
        },
        _prepareParamContent: function () {
            let res = this._super();
            res.changePropertyView = this.useSubPropertyView.bind(this);
            return res;
        }
    });

    return FormViewEdit;
});
