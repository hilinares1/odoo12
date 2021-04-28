var department_data = [];
var chart_object;
var dep_form_id;

odoo.define("organization_chart_pro.org_chart", function (require) {
  "use strict";

  var core = require('web.core');
  var session = require('web.session');
  var ajax = require('web.ajax');
  var AbstractAction = require('web.AbstractAction');
  var Widget = require('web.Widget');
  var ControlPanelMixin = require('web.ControlPanelMixin');
  var Dialog = require('web.Dialog');
  var QWeb = core.qweb;
  var _t = core._t;
  var _lt = core._lt;

  var OrgChartDepartment = AbstractAction.extend(ControlPanelMixin, {
    events: _.extend({}, Widget.prototype.events, {
          'click #btn-reload': 'reload_org_chart',
          'click #btn-export': 'export_org_chart',
          'click .add_node': 'add_noeud',
          'click .edit_node': 'edit_noeud',
          'click .delete_node': 'delete_noeud',
  	}),
    init: function(parent, context) {
      this._super(parent, context);
        var self = this;
        if (context.tag == 'organization_chart_pro.org_chart_department') {
            self._rpc({
                model: 'org.chart.department',
                method: 'get_department_data',
            }, []).then(function(result){
                department_data = result;
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    willStart: function() {
      return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
      var self = this;
      return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var org_chart = QWeb.render('organization_chart_pro.org_chart_template', {
            widget: self,
        });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(org_chart).prependTo(self.$el);
        return org_chart;
    },
    reload: function () {
      window.location.href = this.href;
    },
    reload_org_chart: function(event) {
      $("#chart-container").remove();
      $("#btn-reload").remove();
      $("#btn-export").remove();
      $("#key-word").remove();
      var self = this;
      self._rpc({
          model: 'org.chart.department',
          method: 'get_department_data',
      }, []).then(function(result){
          department_data = result;
      }).done(function(){
          self.render();
          self.href = window.location.href;
      });
    },
    export_org_chart: function (event) {
      var orgchart_width = $('.orgchart').get(0).scrollWidth;
      var orgchart_height = $('.orgchart').get(0).scrollHeight;
      var that = chart_object;
      that.export(that.options.exportFilename, that.options.exportFileextension);
    },
    add_noeud: function (event){
      var self = this;
      event.stopPropagation();
      event.preventDefault();
      self.do_action({
          name: _t("Add new Department"),
          type: 'ir.actions.act_window',
          res_model: 'slife.department',
          view_mode: 'form',
          view_type: 'form',
          context: {
            'parent_id': event.target.id,
            'create': true,
          },
          views: [[dep_form_id, 'form']],
          target: 'new'
      },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    edit_noeud: function (event){
      var self = this;
      event.stopPropagation();
      event.preventDefault();
      self.do_action({
          name: _t("Edit Department"),
          type: 'ir.actions.act_window',
          res_model: 'slife.department',
          view_mode: 'form',
          view_type: 'form',
          context: {
            'dep_id': event.target.id,
            'edit': true,
          },
          views: [[dep_form_id, 'form']],
          target: 'new'
      },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    delete_noeud: function (event){
      var self = this;
      var options = {
        confirm_callback: function () {
          self._rpc({
              model: 'hr.department',
              method: 'unlink',
              args: [parseInt(event.target.id)],
          }, [])
          .done(function(){
            location.reload();
          });
        }
      };
      Dialog.confirm(this, _t("Do you Want to Delete this record ?"), options);
    },
  });

  core.action_registry.add('organization_chart_pro.org_chart_department', OrgChartDepartment);

  return OrgChartDepartment;

});
