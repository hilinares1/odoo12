odoo.define('web_hierarchy.HierarchyView', function (require) {
"use strict";

/**
 * The hierarchy view.
 */

var viewRegistry = require('web.view_registry');

var BasicView = require('web.BasicView');
var core = require('web.core');
var HierarchyRenderer = require('web.HierarchyRenderer');
var HierarchyController = require('web.HierarchyController');

var _lt = core._lt;

var HierarchyView = BasicView.extend({
    accesskey: "l",
    display_name: _lt('Hierarchy'),
    icon: 'fa-tree',
    config: _.extend({}, BasicView.prototype.config, {
        Renderer: HierarchyRenderer,
        Controller: HierarchyController,
    }),
    viewType: 'hierarchy',
    /**
     * @override
     *
     * @param {Object} viewInfo
     * @param {Object} params
     * @param {boolean} params.hasSidebar
     * @param {boolean} [params.hasSelectors=true]
     */
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        var selectedRecords = []; // there is no selected records by default

        var mode = this.arch.attrs.editable && !params.readonly ? "edit" : "readonly";

        this.controllerParams.editable = this.arch.attrs.editable;
        this.controllerParams.hasSidebar = params.hasSidebar;
        this.controllerParams.toolbarActions = viewInfo.toolbar;
        this.controllerParams.noLeaf = !!this.loadParams.context.group_by_no_leaf;
        this.controllerParams.mode = mode;
        this.controllerParams.selectedRecords = selectedRecords;

        this.rendererParams.arch = this.arch;
        this.rendererParams.hasSelectors =
                'hasSelectors' in params ? params.hasSelectors : true;
        this.rendererParams.editable = params.readonly ? false : this.arch.attrs.editable;
        this.rendererParams.selectedRecords = selectedRecords;

        this.loadParams.limit = this.loadParams.limit || 80;
        this.loadParams.type = 'list';
    },
});

viewRegistry.add('hierarchy', HierarchyView);

return HierarchyView;
});
