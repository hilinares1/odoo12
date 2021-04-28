odoo.define('yee_odoo_studio.KanbanViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('yee_odoo_studio.BaseEdit');
    var KanbanViewContent = require('yee_odoo_studio.KanbanViewContent');
    var KanbanViewProperty = require('yee_odoo_studio.KanbanViewProperty');


    var KanbanViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.sortData = [[".oe_kanban_card", ".oe_kanban_card"]];
            this.view.property = KanbanViewProperty;
            this.view.content = KanbanViewContent;
        },
        _prepareParamProperty: function () {
            let res = this._super();
            res.onChangeTemplate = this.onChangeTemplate.bind(this);
            res.onChangeFieldSelect = this.onChangeFieldSelect.bind(this);
            return res;
        },
        _prepareParamContent: function () {
            let res = this._super();
            res.onAddTag = this.onAddTag.bind(this);
            return res;
        },
        onChangeFieldSelect: function (fieldName, addId) {
            this.ref.content.onChangeFieldSelect(fieldName, addId)
        },
        onChangeTemplate: function (template) {
            this.ref.content.changeTemplate(template);
        },
        onAddTag: function (tagType, addId) {
            this.ref.property.onClickAddTag(tagType, addId);
        },
    });

    return KanbanViewEdit;
});
