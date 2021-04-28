odoo.define('hierarchical_chart.hierarchical_chart', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var hierarchicalChart = Widget.extend(ControlPanelMixin, {
        template: "hierarchical_chart.hierarchical_chart_temp",



        init: function (parent, params) {
            this._super(parent, params);
            this.params = params;
        },

        start: function () {
            var self = this;
            var call_data = {
                model: 'hierarchical_chart_model',
                method: "hierarchical_chart_details",
                args: [this.params['context']['model']],
            }
            if(this.params['context']["active_id"] != undefined){
                call_data = {
                    model: 'hierarchical_chart_model',
                    method: "hierarchical_chart_details",
                    args: [this.params['context']['model'], this.params['context']["active_id"]],
                }
            }
            rpc.query(call_data)
                .then(function (result) {
                    self.cols = result['cols'];
                    self.chart_data = result['all_data'];
                    self.fields_names = result['fields_names'];
                    self.fields_types = result['fields_types'];

                    console.log(self.fields_types)
                    $('.account_chart_list').html(QWeb.render('hierarchical_chart.chartList', { widget: self }));
                    $('#basic').simpleTreeTable({
                        expander: $('#expander'),
                        collapser: $('#collapser')
                    });

                    var supportsPdfMimeType = typeof navigator.mimeTypes["application/pdf"] !== "undefined"
                    var isIE = function () {
                        return !!(window.ActiveXObject || "ActiveXObject" in window)
                    }
                    var supportsPdfActiveX = function () {
                        return !!(createAXO("AcroPDF.PDF") || createAXO("PDF.PdfCtrl"))
                    }
                    var supportsPDFs = supportsPdfMimeType || isIE() && supportsPdfActiveX();

                    if (supportsPDFs) {
                        $('#basic').DataTable({
                            dom: 'Bfrtip',
                            paging: false,
                            "ordering": false,
                            "searching": false,
                            "autoWidth": false,
                            "language": {
                                "info": "Showing _MAX_ enteries",
                            },
                            buttons: [
                                'copyHtml5',
                                'excelHtml5',
                                'csvHtml5',
                                {
                                    extend: 'print',
                                    text: 'PDF',
                                },
                                'colvis',
                            ]
                        });
                    }
                    else {
                        $('#basic').DataTable({
                            dom: 'Bfrtip',
                            paging: false,
                            "ordering": false,
                            "searching": false,
                            "autoWidth": false,
                            "language": {
                                "info": "Showing _MAX_ enteries",
                            },
                            buttons: [
                                'copyHtml5',
                                'excelHtml5',
                                'csvHtml5',
                            ]
                        });
                    }






                });

            return this._super();
        },

        open_emp: function (event) {




            try {
                var employee_id = parseInt($(event.currentTarget).data('employee-id'));
                event.stopPropagation();
                event.preventDefault();
                this.do_action({
                    type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: 'hr.employee',
                    views: [[false, 'form']],
                    res_id: employee_id,
                    target: 'current',
                    flags: { action_buttons: true, headless: true },
                })

            } catch (error) {

            }

        },

    });

    core.action_registry.add('hierarchical_view', hierarchicalChart);


    return hierarchicalChart;

});