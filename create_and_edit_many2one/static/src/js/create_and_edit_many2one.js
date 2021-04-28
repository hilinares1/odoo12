odoo.define('create_and_edit_many2one.create_and_edit_many2one', function(require) {
    "use strict";

var FieldMany2One = require('web.relational_fields').FieldMany2One;
var field_registry = require('web.field_registry');
var CreateEditField = FieldMany2One.extend({
    init: function () {
        this._super.apply(this, arguments);
         this._rpc({route: '/web/create_and_edit_many2one/create_edit_allowed',}).then(
             function(result) {
                 this.can_create = result;
                 this.can_write = result;
             }.bind(this));
    },
});

field_registry.add('create_edit_many2one', CreateEditField);

return CreateEditField;
});