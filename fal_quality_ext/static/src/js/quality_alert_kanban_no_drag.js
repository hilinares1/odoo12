odoo.define('fal_quality_ext.quality_alert_kanban_no_drag', function (require) {

var KanbanColumn = require('web.KanbanColumn');

KanbanColumn.include({
    init: function () {
        this._super.apply(this, arguments);
        if (this.modelName === 'quality.alert') {
            this.draggable = false;
        }
    },
});

});
