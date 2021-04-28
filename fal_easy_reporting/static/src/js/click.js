odoo.define('fal_easy_reporting', function (require) {
    var core = require('web.core');
    var FormView = require('web.FormView');
    var pyUtils = require('web.py_utils'); /*edited by murha*/
    var framework = require('web.framework');
    var session = require('web.session');
    var FormController = require('web.FormController');
    var QWeb = core.qweb;
    var _t = core._t;

    FormController.include({
        init: function (parent, model, renderer, params) {
            var _super = this._super.apply(this, arguments);
            var self = this;
            if(self.modelName == 'easy.exporting.wizard') {
                setTimeout(function(){
                    if(self.$buttons !== undefined){
                        var x = self.$buttons.find('div.o_form_buttons_edit');
                        x.remove();
                        self.$buttons.append("<button id='easy_export' class='oe_highlight'>Export</button>");    
                        self.$buttons.find('button#easy_export').click(function(){
                            self.on_click_export_data();
                        });
                    }
                }, 100);
            }
            return _super;
        },
        on_click_export_data: function() {
            var self = this;
            var exported_fields = this.$el.find('textarea.fal_temp').val();
            var domains = pyUtils.eval('domain', this.$el.find('textarea.fal_temp_domain').val()); /*edited by murha*/
            var format_file = this.$el.find('select.fal_file_format').val();
            if (!domains) {
                domains = []
            }
            if (!exported_fields) {
                alert(_t("Please select fields to export..."));
                return;
            }
            if (!format_file) {
                alert(_t("Please select format file to export..."));
                return;
            }
            exported_fields = $.map( exported_fields.split(','), function( val, i ) {
                return {name: val ,
                        label: val};
            });
            var model_fields = this.$el.find('input.fal_resource').val()
            exported_fields.unshift({name: 'id', label: 'External ID'});
            var export_format = 'xls';
            if(format_file == "\"CSV\""){
                export_format = "csv";
            }
            var ids_to_export = false;  /*this.$('#export_selection_only').prop('checked')
                    ? this.getParent().get_selected_ids()
                    : this.dataset.ids;
            */
            framework.blockUI;
            console.log(framework);
            session.get_file({
                url: '/web/export/' + export_format,
                data: {data: JSON.stringify({
                    model: model_fields,
                    fields: exported_fields,
                    ids: ids_to_export,
                    domain: domains,
                    //context: pyeval.eval('contexts', [this.record.getContext()]),
                    import_compat: false//!!this.$import_compat_radios.filter(':checked').val(),
                })},

                //complete: framework.unblockUI,
                //error: crash_manager.rpc_error.bind(crash_manager),
            });
            /*console.log(data);*/
        },
    });

    FormView.include({
        on_click_export_data: function() {
            var self = this;
            var exported_fields = this.$el.find('textarea.fal_temp').val();
            var domains = pyUtils.eval('domain', this.$el.find('textarea.fal_temp_domain').val()); /*edited by murha*/
            var format_file = this.$el.find('select.fal_file_format').val();
            if (!domains) {
                domains = []
            }
            if (!exported_fields) {
                alert(_t("Please select fields to export..."));
                return;
            }
            if (!format_file) {
                alert(_t("Please select format file to export..."));
                return;
            }
            exported_fields = $.map( exported_fields.split(','), function( val, i ) {
                return {name: val ,
                        label: val};
            });
            var model_fields = this.$el.find('input.fal_resource').val()
            exported_fields.unshift({name: 'id', label: 'External ID'});
            var export_format = 'xls';
            if(format_file == "\"CSV\""){
                export_format = "csv";
            }
            var ids_to_export = false;  /*this.$('#export_selection_only').prop('checked')
                    ? this.getParent().get_selected_ids()
                    : this.dataset.ids;
            */
            framework.blockUI;
            this.session.get_file({
                url: '/web/export/' + export_format,
                data: {data: JSON.stringify({
                    model: model_fields,
                    fields: exported_fields,
                    ids: ids_to_export,
                    domain: domains, //this.dataset.domain,
                    import_compat: 'yes',
                })},
                complete: framework.unblockUI,
            });
        },
        do_show: function(options) {
            var self = this;
            var res = self._super(options);
            if(self.model == 'easy.exporting.wizard') {
                var x = self.$buttons.find('div.o_form_buttons_edit');
                x.remove();
                self.$buttons.append("<button id='easy_export' class='oe_highlight'>Export</button>");
                self.$buttons.find('button#easy_export').click(function(){
                    self.on_click_export_data();
                });
            }
            return res;
        },
})

});
