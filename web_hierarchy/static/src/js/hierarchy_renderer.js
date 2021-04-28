odoo.define('web.HierarchyRenderer', function (require) {
"use strict";

var BasicRenderer = require('web.BasicRenderer');
var config = require('web.config');
var core = require('web.core');
var Dialog = require('web.Dialog');
var dom = require('web.dom');
var field_utils = require('web.field_utils');
var Pager = require('web.Pager');
var utils = require('web.utils');
var rpc = require('web.rpc');
var _t = core._t;

// Allowed decoration on the list's rows: bold, italic and bootstrap semantics classes
var DECORATIONS = [
    'decoration-bf',
    'decoration-it',
    'decoration-danger',
    'decoration-info',
    'decoration-muted',
    'decoration-primary',
    'decoration-success',
    'decoration-warning'
];

var FIELD_CLASSES = {
    float: 'o_list_number',
    integer: 'o_list_number',
    monetary: 'o_list_number',
    text: 'o_list_text',
};

var HierarchyRenderer = BasicRenderer.extend({
    events: {
        'click tbody tr': '_onRowClicked',
        'click tbody .o_list_record_selector': '_onSelectRecord',
        'click thead th.o_column_sortable': '_onSortColumn',
        'click .o_group_header': '_onToggleGroup',
        'click thead .o_list_record_selector input': '_onToggleSelection',
    },
    /**
     * @constructor
     * @param {Widget} parent
     * @param {any} state
     * @param {Object} params
     * @param {boolean} params.hasSelectors
     */
    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        this.hasHandle = false;
        this.handleField = 'sequence';
        this._processColumns(params.columnInvisibleFields || {});
        this.rowDecorations = _.chain(this.arch.attrs)
            .pick(function (value, key) {
                return DECORATIONS.indexOf(key) >= 0;
            }).mapObject(function (value) {
                return py.parse(py.tokenize(value));
            }).value();
        this.hasSelectors = params.hasSelectors;
        this.selection = [];
        this.pagers = []; // instantiated pagers (only for grouped lists)
        this.editable = params.editable;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    updateState: function (state, params) {
        this._processColumns(params.columnInvisibleFields || {});
        this.selection = [];
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * This method does a in-memory computation of the aggregate values, for
     * each columns that corresponds to a numeric field with a proper aggregate
     * function.
     *
     * The result of these computations is stored in the 'aggregate' key of each
     * column of this.columns.  This will be then used by the _renderFooter
     * method to display the appropriate amount.
     *
     * @private
     */
    _computeAggregates: function () {
        var self = this;
        var data = [];
        if (this.selection.length) {
            utils.traverse_records(this.state, function (record) {
                if (_.contains(self.selection, record.id)) {
                    data.push(record); // find selected records
                }
            });
        } else {
            data = this.state.data;
        }

        _.each(this.columns, this._computeColumnAggregates.bind(this, data));
    },
    /**
     * Compute the aggregate values for a given column and a set of records.
     * The aggregate values are then written, if applicable, in the 'aggregate'
     * key of the column object.
     *
     * @private
     * @param {Object[]} data a list of selected/all records
     * @param {Object} column
     */
    _computeColumnAggregates: function (data, column) {
        var attrs = column.attrs;
        var field = this.state.fields[attrs.name];
        if (!field) {
            return;
        }
        var type = field.type;
        if (type !== 'integer' && type !== 'float' && type !== 'monetary') {
            return;
        }
        var func = (attrs.sum && 'sum') || (attrs.avg && 'avg') ||
                    (attrs.max && 'max') || (attrs.min && 'min');
        if (func) {
            var count = 0;
            var aggregateValue = (func === 'max') ? -Infinity : (func === 'min') ? Infinity : 0;
            _.each(data, function (d) {
                count += 1;
                var value = (d.type === 'record') ? d.data[attrs.name] : d.aggregateValues[attrs.name];
                if (func === 'avg') {
                    aggregateValue += value;
                } else if (func === 'sum') {
                    aggregateValue += value;
                } else if (func === 'max') {
                    aggregateValue = Math.max(aggregateValue, value);
                } else if (func === 'min') {
                    aggregateValue = Math.min(aggregateValue, value);
                }
            });
            if (func === 'avg') {
                aggregateValue = count ? aggregateValue / count : aggregateValue;
            }
            column.aggregate = {
                help: attrs[func],
                value: aggregateValue,
            };
        }
    },
    /**
     * return the number of visible columns.  Note that this number depends on
     * the state of the renderer.  For example, in editable mode, it could be
     * one more that in non editable mode, because there may be a visible 'trash
     * icon'.
     *
     * @private
     * @returns {integer}
     */
    _getNumberOfCols: function () {
        var n = this.columns.length;
        return this.hasSelectors ? n+1 : n;
    },
    /**
     * Removes the columns which should be invisible.
     *
     * @param  {Object} columnInvisibleFields contains the column invisible modifier values
     */
    _processColumns: function (columnInvisibleFields) {
        var self = this;
        self.hasHandle = false;
        self.handleField = null;
        this.columns = _.reject(this.arch.children, function (c) {
            var reject = c.attrs.modifiers.column_invisible;
            // If there is an evaluated domain for the field we override the node
            // attribute to have the evaluated modifier value.
            if (c.attrs.name in columnInvisibleFields) {
                reject = columnInvisibleFields[c.attrs.name];
            }
            if (!reject && c.attrs.widget === 'handle') {
                self.hasHandle = true;
                self.handleField = c.attrs.name;
            }
            return reject;
        });
    },
    /**
     * Render a list of <td>, with aggregates if available.  It can be displayed
     * in the footer, or for each open groups.
     *
     * @private
     * @param {any} aggregateValues
     * @returns {jQueryElement[]} a list of <td> with the aggregate values
     */
    _renderAggregateCells: function (aggregateValues) {
        var self = this;
        return _.map(this.columns, function (column) {
            var $cell = $('<td>');
            if (column.attrs.name in aggregateValues) {
                var field = self.state.fields[column.attrs.name];
                var value = aggregateValues[column.attrs.name].value;
                var help = aggregateValues[column.attrs.name].help;
                var formatFunc = field_utils.format[column.attrs.widget];
                if (!formatFunc) {
                    formatFunc = field_utils.format[field.type];
                }
                var formattedValue = formatFunc(value, field, {escape: true});
                $cell.addClass('o_list_number').attr('title', help).html(formattedValue);
            }
            return $cell;
        });
    },
    /**
     * Render the main body of the table, with all its content.  Note that it
     * has been decided to always render at least 4 rows, even if we have less
     * data.  The reason is that lists with 0 or 1 lines don't really look like
     * a table.
     *
     * @private
     * @returns {jQueryElement} a jquery element <tbody>
     */
    _renderBody: function () {
        var $rows = this._renderRows();
        while ($rows.length < 4) {
            $rows.push(this._renderEmptyRow());
        }
        return $('<tbody>').append($rows);
    },
    /**
     * Render a cell for the table. For most cells, we only want to display the
     * formatted value, with some appropriate css class. However, when the
     * node was explicitely defined with a 'widget' attribute, then we
     * instantiate the corresponding widget.
     *
     * @private
     * @param {Object} record
     * @param {Object} node
     * @param {integer} colIndex
     * @param {Object} [options]
     * @param {Object} [options.mode]
     * @param {Object} [options.renderInvisible=false]
     *        force the rendering of invisible cell content
     * @param {Object} [options.renderWidgets=false]
     *        force the rendering of the cell value thanks to a widget
     * @returns {jQueryElement} a <td> element
     */
    _renderBodyCell: function (record, node, colIndex, options) {
        var tdClassName = 'o_data_cell';

        if (node.tag === 'button') {
            tdClassName += ' o_list_button';
        } else if (node.tag === 'field') {
            var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
            if (typeClass) {
                tdClassName += (' ' + typeClass);
            }
            if (node.attrs.widget) {
                tdClassName += (' o_' + node.attrs.widget + '_cell');
            }
        }
        //.css('padding-left', (groupLevel * 20) + 'px')

        var $td = $('<td>', {class: tdClassName});
        if(colIndex == 0 && record.depth > 0){ //dont add rules padding 0
            $td.css('padding-left', (record.depth * 40) + 'px');
        }

        // We register modifiers on the <td> element so that it gets the correct
        // modifiers classes (for styling)
        var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
        // If the invisible modifiers is true, the <td> element is left empty.
        // Indeed, if the modifiers was to change the whole cell would be
        // rerendered anyway.
        if (modifiers.invisible && !(options && options.renderInvisible)) {
            return $td;
        }

        if (node.tag === 'button') {
            return $td.append(this._renderButton(record, node));
        } else if (node.tag === 'widget') {
            return $td.append(this._renderWidget(record, node));
        }
        if (node.attrs.widget || (options && options.renderWidgets)) {
            var widget = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
            this._handleAttributes(widget.$el, node);
            return $td.append(widget.$el);
        }
        var name = node.attrs.name;
        var field = this.state.fields[name];
        var value = record.data[name];
        var formattedValue = field_utils.format[field.type](value, field, {
            data: record.data,
            escape: true,
            isPassword: 'password' in node.attrs,
        });
        this._handleAttributes($td, node);
        return $td.html(formattedValue);
    },
    /**
     * Renders the button element associated to the given node and record.
     *
     * @private
     * @param {Object} record
     * @param {Object} node
     * @returns {jQuery} a <button> element
     */
    _renderButton: function (record, node) {
        var $button = $('<button>', {
            type: 'button',
            title: node.attrs.string,
        });
        if (node.attrs.icon) {
            $button.addClass('o_icon_button');
            $button.append($('<i>', {class: 'fa ' + node.attrs.icon}));
        } else {
            $button.text(node.attrs.string);
        }
        this._handleAttributes($button, node);
        this._registerModifiers(node, record, $button);

        if (record.res_id) {
            // TODO this should be moved to a handler
            var self = this;
            $button.on("click", function (e) {
                e.stopPropagation();
                self.trigger_up('button_clicked', {
                    attrs: node.attrs,
                    record: record,
                });
            });
        } else {
            if (node.attrs.options.warn) {
                var self = this;
                $button.on("click", function (e) {
                    e.stopPropagation();
                    self.do_warn(_t("Warning"), _t('Please click on the "save" button first'));
                });
            } else {
                $button.prop('disabled', true);
            }
        }

        return $button;
    },
    /**
     * Render a complete empty row.  This is used to fill in the blanks when we
     * have less than 4 lines to display.
     *
     * @private
     * @returns {jQueryElement} a <tr> element
     */
    _renderEmptyRow: function () {
        var $td = $('<td>&nbsp;</td>').attr('colspan', this._getNumberOfCols());
        return $('<tr>').append($td);
    },
    /**
     * Render the footer.  It is a <tfoot> with a single row, containing all
     * aggregates, if applicable.
     *
     * @private
     * @param {boolean} isGrouped if the view is grouped, we have to add an
     *   extra <td>
     * @returns {jQueryElement} a <tfoot> element
     */
    _renderFooter: function (isGrouped) {
        var aggregates = {};
        _.each(this.columns, function (column) {
            if ('aggregate' in column) {
                aggregates[column.attrs.name] = column.aggregate;
            }
        });
        var $cells = this._renderAggregateCells(aggregates);
        if (isGrouped || this.h_view_active) {
            $cells.unshift($('<td>'));
        }
        if (this.hasSelectors) {
            $cells.unshift($('<td>'));
        }
        //$cells.unshift($('<td>'));//add empty for caret
        return $('<tfoot>').append($('<tr>').append($cells));
    },
    /**
     * Renders the pager for a given group
     *
     * @private
     * @param {Object} group
     * @returns {JQueryElement} the pager's $el
     */
    _renderGroupPager: function (group) {
        var pager = new Pager(this, group.count, group.offset + 1, group.limit);
        pager.on('pager_changed', this, function (newState) {
            var self = this;
            pager.disable();
            this.trigger_up('load', {
                id: group.id,
                limit: newState.limit,
                offset: newState.current_min - 1,
                on_success: function (reloadedGroup) {
                    _.extend(group, reloadedGroup);
                    self._renderView();
                },
                on_fail: pager.enable.bind(pager),
            });
        });
        // register the pager so that it can be destroyed on next rendering
        this.pagers.push(pager);

        var fragment = document.createDocumentFragment();
        pager.appendTo(fragment); // starts the pager
        return pager.$el;
    },
    /**
     * Render the row that represent a group
     *
     * @private
     * @param {Object} group
     * @param {integer} groupLevel the nesting level (0 for root groups)
     * @returns {jQueryElement} a <tr> element
     */
    _renderGroupRow: function (group, groupLevel) {
        var aggregateValues = _.mapObject(group.aggregateValues, function (value) {
            return { value: value };
        });
        var $cells = this._renderAggregateCells(aggregateValues);
        if (this.hasSelectors) {
            $cells.unshift($('<td>'));
        }
        var name = group.value === undefined ? _t('Undefined') : group.value;
        var groupBy = this.state.groupedBy[groupLevel];
        if (group.fields[groupBy.split(':')[0]].type !== 'boolean') {
            name = name || _t('Undefined');
        }
        var $th = $('<th>')
                    .addClass('o_group_name')
                    .text(name + ' (' + group.count + ')');
        var $arrow = $('<span>')
                            .css('padding-left', (groupLevel * 20) + 'px')
                            .css('padding-right', '5px')
                            .addClass('fa');
        if (group.count > 0) {
            $arrow.toggleClass('fa-caret-right', !group.isOpen)
                    .toggleClass('fa-caret-down', group.isOpen);
        }
        $th.prepend($arrow);
        if (group.isOpen && !group.groupedBy.length && (group.count > group.data.length)) {
            var $pager = this._renderGroupPager(group);
            var $lastCell = $cells[$cells.length-1];
            $lastCell.addClass('o_group_pager').append($pager);
        }
        return $('<tr>')
                    .addClass('o_group_header')
                    .toggleClass('o_group_open', group.isOpen)
                    .toggleClass('o_group_has_content', group.count > 0)
                    .data('group', group)
                    .append($th)
                    .append($cells);
    },
    /**
     * Render all groups in the view.  We assume that the view is in grouped
     * mode.
     *
     * Note that each group is rendered inside a <tbody>, which contains a group
     * row, then possibly a bunch of rows for each record.
     *
     * @private
     * @param {Object} data the dataPoint containing the groups
     * @param {integer} [groupLevel=0] the nesting level. 0 is for the root group
     * @returns {jQueryElement[]} a list of <tbody>
     */
    _renderGroups: function (data, groupLevel) {
        var self = this;
        groupLevel = groupLevel || 0;
        var result = [];
        var $tbody = $('<tbody>');
        _.each(data, function (group) {
            if (!$tbody) {
                $tbody = $('<tbody>');
            }
            $tbody.append(self._renderGroupRow(group, groupLevel));
            if (group.data.length) {
                result.push($tbody);
                // render an opened group
                if (group.groupedBy.length) {
                    // the opened group contains subgroups
                    result = result.concat(self._renderGroups(group.data, groupLevel + 1));
                } else {
                    // the opened group contains records
                    var $records = _.map(group.data, function (record) {
                        return self._renderRow(record).prepend($('<td>'));
                    });
                    result.push($('<tbody>').append($records));
                }
                $tbody = null;
            }
        });
        if ($tbody) {
            result.push($tbody);
        }
        return result;
    },
    /**
     * Render the main header for the list view.  It is basically just a <thead>
     * with the name of each fields
     *
     * @private
     * @param {boolean} isGrouped
     * @returns {jQueryElement} a <thead> element
     */
    _renderHeader: function (isGrouped) {
        //var $addCaret = $('<th>');
        var $tr = $('<tr>')
                //.append($('<th>'))//add empty column for caret
                .append(_.map(this.columns, this._renderHeaderCell.bind(this)));
        if (this.hasSelectors) {
            $tr.prepend(this._renderSelector('th'));
        }
        if (isGrouped || this.h_view_active) {
            $tr.prepend($('<th>').html('&nbsp;'));
        }
        return $('<thead>').append($tr);
    },
    /**
     * Render a single <th> with the informations for a column. If it is not a
     * field, the th will be empty. Otherwise, it will contains all relevant
     * information for the field.
     *
     * @private
     * @param {Object} node
     * @returns {jQueryElement} a <th> element
     */
    _renderHeaderCell: function (node) {
        var name = node.attrs.name;
        var order = this.state.orderedBy;
        var isNodeSorted = order[0] && order[0].name === name;
        var field = this.state.fields[name];
        var $th = $('<th>');
        if (!field) {
            return $th;
        }
        var description;
        if (node.attrs.widget && this.state.fieldsInfo.list !== undefined) {
            description = this.state.fieldsInfo.list[name].Widget.prototype.description;
        }
        if (description === undefined) {
            description = node.attrs.string || field.string;
        }
        $th
            .text(description)
            .data('name', name)
            .toggleClass('o-sort-down', isNodeSorted ? !order[0].asc : false)
            .toggleClass('o-sort-up', isNodeSorted ? order[0].asc : false)
            .addClass(field.sortable && 'o_column_sortable');

        if (field.type === 'float' || field.type === 'integer' || field.type === 'monetary') {
            $th.css({textAlign: 'right'});
        }

        if (config.debug) {
            var fieldDescr = {
                field: field,
                name: name,
                string: description || name,
                record: this.state,
                attrs: node.attrs,
            };
            this._addFieldTooltip(fieldDescr, $th);
        }
        return $th;
    },
    /**
     * Render a row, corresponding to a record.
     *
     * @private
     * @param {Object} record
     * @returns {jQueryElement} a <tr> element
     */
    _renderRow: function (record) {
        var self = this;
        this.defs = []; // TODO maybe wait for those somewhere ?
        var $cells = _.map(this.columns, function (node, index) {
            return self._renderBodyCell(record, node, index, {mode: 'readonly'});
        });
        
        delete this.defs;
        
        if(record.children){//FIX BUG IF USER SELECT GROUP BY
            if(record.children.length){ 
            //if got children then add caret, can move to a separate function like _renderSelector
                var $arrow = $('<span>')
                    .css('padding','5px 10px')
                    .css('margin-right','2px')
                    .css('border','1px solid #E5E5E5')
                    .css('border-radius','5px')
                    .addClass('fa fa-caret-right caret-hierarchy');
            }else{
                var $arrow = $('<span>');
            }

            $arrow.click(function(event){
                event.stopPropagation();
                if($(this).hasClass('fa-caret-right')){
                    $('.childOf'+record.data.id+'.depth'+(record.parents.length+1)).show();
                    $(this).toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                }else if($(this).hasClass('fa-caret-down')){
                    $('.childOf'+record.data.id).hide();
                    $('.childOf'+record.data.id).each(function(){
                        $(this).find('span.fa-caret-down').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                    });
                    //$('.childOf'+record.data.id).children('span').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                    $(this).toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                }
            });

            $cells[0].prepend($arrow);
        }
        /*var $td = $('<td>');
        $td.append($arrow); //wrap caret with td
        $td.click(function(event){
            event.stopPropagation();
            if($(this).children('span').hasClass('fa-caret-right')){
                $('.childOf'+record.data.id+'.depth'+(record.parents.length+1)).show();
                $(this).children('span').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
            }else if($(this).children('span').hasClass('fa-caret-down')){
                $('.childOf'+record.data.id).hide();
                $('.childOf'+record.data.id).each(function(){
                    $(this).find('span.fa-caret-down').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                });
                //$('.childOf'+record.data.id).children('span').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
                $(this).children('span').toggleClass('fa-caret-right').toggleClass('fa-caret-down');
            }
        });*/

        
        var $tr = $('<tr/>', {class: 'o_data_row'})
                    .data('id', record.id)
                    .append($cells);
        if (this.hasSelectors) {
            $tr.prepend(this._renderSelector('td'));
        }
        this._setDecorationClasses(record, $tr);

        if(record.parents){//FIX BUG IF USER SELECT GROUP BY
            for(var i = 0 ; i < record.parents.length ; i++){ //flagging for caret opening
                $tr.addClass('childOf'+record.parents[i]);
            }

            if(record.depth > 0 && !record.force_show){
                $tr.hide();
            }
            $tr.addClass('depth'+record.parents.length);
        }
        
        return $tr;
    },
    /**
     * Render all rows. This method should only called when the view is not
     * grouped.
     *
     * @private
     * @returns {jQueryElement[]} a list of <tr>
     */
     _list_to_tree: function(list){
        var map = {}, node, roots = [], i;
            for (i = 0; i < list.length; i += 1) {
                map[list[i].data.id] = i; // initialize the map
                list[i].children = []; // initialize the children
            }
            for (i = 0; i < list.length; i += 1) {
                node = list[i];
                if (node.data.parent_id){// otherwise error if no parent id
                    // if you have dangling branches check that map[node.parentId] exists
                    if(list[map[node.data.parent_id.data.id]]){
                        list[map[node.data.parent_id.data.id]].children.push(node);        
                    }else{//work around for search, children without parent
                        node.force_show = true;
                        roots.push(node);
                    }
                }else{
                    roots.push(node);
                }
            }
            return roots;
     },

    _extract_children: function(hierarchial_tree, list){//if need sort or filter, can do here
        for (var i = 0 ; i < list.length ; i ++){
            hierarchial_tree.push(list[i]);
            if (list[i].children.length > 0){
                hierarchial_tree = this._extract_children(hierarchial_tree, list[i].children);
            }
        }
        return hierarchial_tree;
     },

    _renderRows: function () {
        
        /*var hierarchial_tree = this._extract_children([] , this._list_to_tree(this.state.data));
        
        for(var i = 0 ; i < hierarchial_tree.length ; i++){//this is state data conditioned to hierarchy
            hierarchial_tree[i].depth = 0;
            hierarchial_tree[i].parents = [];
            var temp = hierarchial_tree[i];
            while(temp.data.parent_id){
                hierarchial_tree[i].depth++;
                hierarchial_tree[i].parents.push(temp.data.parent_id.data.id);
                var parent = _.filter(hierarchial_tree, function(data){
                    return data.data.id == temp.data.parent_id.data.id;
                }); //can use conventional looping for faster tree cutting
                if(parent.length){//children without parents (search function)
                    temp = parent[0];//there is only room for 1 boss, only 1 parent
                }else{
                    break;
                }
            }
        }*/
        //render hierarchial_tree instead of this.state.data
        //return _.map(hierarchial_tree, this._renderRow.bind(this));
        return _.map(this.state.data, this._renderRow.bind(this));
    },
    _renderTrees: function (h_view_active, trees, treeLevel) {
        var self = this;
        if(!h_view_active){
            return this._renderBody();//return normal body rendering
        }else{
            //return tree rendering
        }
        treeLevel = treeLevel || 0;
        var result = [];
        var $tbody = $('<tbody>');
        _.each(trees, function (tree) {
            
            if (!$tbody) {
                $tbody = $('<tbody>');
            }
            
            result.push($('<tbody data-level='+treeLevel+'>').click(function(){
                var $next = $(this).next();
                if($next.hasClass("hidden")){
                    $(this).find("span").removeClass('fa-caret-right')
                    .addClass('fa-caret-down');
                    $(this).addClass('o_group_open');
                    while($next.data('level') > treeLevel){
                        if($next.data('level') <= treeLevel + 1){
                            $next.removeClass("hidden");
                        }
                        $next = $next.next();
                    }   
                }else{
                    $(this).find("span").addClass('fa-caret-right')
                    .removeClass('fa-caret-down');
                    while($next.data('level') > treeLevel){
                        //if($next.data('level') <= treeLevel + 1){
                            $(this).removeClass('o_group_open');
                            $next.addClass("hidden");
                        //}
                        $next = $next.next();
                    }
                }
                /*while($next.data('level') > treeLevel || $next.data('level') == undefined){
                    $next.toggleClass("hidden");
                    $next = $next.next();
                }*/
            }).toggleClass("hidden", treeLevel > 0).append(self._renderTreeRow(tree, treeLevel)));

            var $records = _.map(tree.rows, function (record) {
                return self._renderRow(record).prepend($('<td>'));
            });
            result.push($('<tbody class="hidden" data-level='+(treeLevel+1)+'>').append($records));
            
            if(tree.children.length){
                    result = result.concat(self._renderTrees(true, tree.children, treeLevel + 1));
            }
            /*if (group.data.length) {
                result.push($tbody);
                // render an opened group
                if (group.groupedBy.length) {
                    // the opened group contains subgroups
                    result = result.concat(self._renderGroups(group.data, groupLevel + 1));
                } else {
                    // the opened group contains records
                    var $records = _.map(group.data, function (record) {
                        return self._renderRow(record).prepend($('<td>'));
                    });
                    result.push($('<tbody>').append($records));
                }
                $tbody = null;
            }*/
        });
        /*if ($tbody) {
            result.push($tbody);
        }*/
        return result;
    },
    _renderTreeRow: function (tree, treeLevel) {

        //tree.isOpen = false;
        var aggregateValues = _.mapObject(tree.aggregateValues, function (value) {
            return { value: value };
        });
        var $cells = this._renderAggregateCells(aggregateValues);
        if (this.hasSelectors) {
            $cells.unshift($('<td>'));
        }
        var name = tree.display_name === undefined ? _t('Undefined') : tree.display_name;
        /*var groupBy = this.state.groupedBy[groupLevel];
        if (group.fields[groupBy.split(':')[0]].type !== 'boolean') {
            name = name || _t('Undefined');
        }*/
        var $th = $('<th>')
                    .addClass('o_group_name')
                    .text(name + ' (' + tree.rows.length + ')');
        var $arrow = $('<span>')
                            .css('padding-left', (treeLevel * 20) + 'px')
                            .css('padding-right', '5px')
                            .addClass('fa');
        if (tree.rows.length) {//ADJUST PRE DETERMINED CARET HERE
            $arrow.toggleClass('fa-caret-right', !tree.isOpen)
                    .toggleClass('fa-caret-down', tree.isOpen);
        }
        $th.prepend($arrow);
        /*if (group.isOpen && !group.groupedBy.length && (group.count > group.data.length)) {
            var $pager = this._renderGroupPager(group);
            var $lastCell = $cells[$cells.length-1];
            $lastCell.addClass('o_group_pager').append($pager);
        }*/
        return $('<tr>')
                    .addClass('o_group_header')
                    //.toggleClass('o_group_open', group.isOpen)
                    .toggleClass('o_group_has_content', tree.rows.length > 0)
                    .data('group', tree)
                    .append($th)
                    .append($cells);
    },
    /**
     * A 'selector' is the small checkbox on the left of a record in a list
     * view.  This is rendered as an input inside a div, so we can properly
     * style it.
     *
     * Note that it takes a tag in argument, because selectores in the header
     * are renderd in a th, and those in the tbody are in a td.
     *
     * @private
     * @param {any} tag either th or td
     * @returns {jQueryElement}
     */
    _renderSelector: function (tag) {
        var $content = dom.renderCheckbox();
        return $('<' + tag + ' width="1">')
                    .addClass('o_list_record_selector')
                    .append($content);
    },
    _revokeParent: function (relation, name) {
        var self = this;
        self.h_view_active = true;
        self.revoking_parent_name = name;
        self.h_view_tree = {};

        rpc.query({
            model: relation,
            method: 'search_read',
            //domain: [['ttype','=','many2one'],['model','=',results[i].relation],['name','=','parent_id']],
            //fields: ['relation'],
        }, {
            timeout: 9999,
            shadow: true,
        })
        .then(function(list){
            if(list.length){
                //extract coresponding parents
                self.h_view_parents = [];
                var have_undefined_parent = false;
                for(var i  = 0 ; i < self.state.data.length; i ++){
                    if(self.state.data[i].data[self.revoking_parent_name]){//if its selected parent is defined
                        par = _.find(list, function(dataList){
                            return dataList.id == self.state.data[i].data[self.revoking_parent_name].data.id;
                        });
                        par.rows = [];//for filling rows later
                        self.h_view_parents.push(par);
                    }else{//if parent is undefined
                        have_undefined_parent = true;
                    }
                }
                //make unique parents
                self.h_view_parents = _.filter(self.h_view_parents, function(v, i, t){
                    return t.indexOf(v) === i;
                });
                if(have_undefined_parent){//add undefined parent to last index
                    var par = [];
                    par.id = 0;
                    par.name = "undefined";
                    par.parent_id = false;
                    par.rows = [];
                    self.h_view_parents.push(par);
                }

                //assign rows to its parent
                for(var i  = 0 ; i < self.state.data.length; i ++){
                    if(self.state.data[i].data[self.revoking_parent_name]){//if have the selected parent
                        for(var j  = 0 ; j < self.h_view_parents.length; j ++){
                            if(self.state.data[i].data[self.revoking_parent_name].data.id == self.h_view_parents[j].id){
                                self.h_view_parents[j].rows.push(self.state.data[i]);
                                //console.log(self.state.data[i].data.name + " assigned to " +self.h_view_parents[j].name);
                            }
                        }           
                    }else{//selected parent is false
                        // var assigned = false;
                        // for(var k  = 0 ; k < self.h_view_parents.length; k ++){
                        //     if(self.state.data[i].data.id == self.h_view_parents[k].id){
                        //         self.h_view_parents[k].rows.push(self.state.data[i]);
                        //         console.log(self.state.data[i].data.name + " assigned to " +self.h_view_parents[k].name);
                        //         assigned = true;
                        //         k = self.h_view_parents.length;//break
                        //     }
                        // }
                        // if(!assigned){
                        //     self.h_view_parents[self.h_view_parents.length-1].rows.push(self.state.data[i]);//assign orphan to undefined parent(last index)
                        //     console.log(self.state.data[i].data.name + " assigned to " +self.h_view_parents[self.h_view_parents.length-1].name);    
                        // }
                        self.h_view_parents[self.h_view_parents.length-1].rows.push(self.state.data[i]);//assign orphan to undefined parent(last index)
                    }
                        
                }

                
                var map = {};
                //self.h_view_node = [];
                self.h_view_roots = [];

                for(var i = 0; i < self.h_view_parents.length ; i++){
                    map[self.h_view_parents[i].id] = i; // initialize the map
                    self.h_view_parents[i].children = []; // initialize children (child_ids only contains id)
                }
                
                for (i = 0; i < self.h_view_parents.length; i ++) {
                    var node = self.h_view_parents[i];
                    if (node.parent_id){// otherwise error if no parent id
                        // if you have dangling branches check that map[node.parentId] exists
                        if(self.h_view_parents[map[node.parent_id[0]]]){//parent_id id at [0], [1] for name
                            self.h_view_parents[map[node.parent_id[0]]].children.push(node);        
                        }else{//work around for search, children without parent
                            node.force_show = true;
                            self.h_view_roots.push(node);
                        }
                    }else{
                        self.h_view_roots.push(node);
                    }
                }
            }
            self._renderView();
        }, function(type,err){ 
            //def.reject();
            console.log(err);
        });
    },
    //RENDER NEW HIERARCHIAL TREE BASED ON SELECTED PARENT
    /*_revokeParent: function (str) {
        var self = this;
        var def  = new $.Deferred();
        //var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
        var domain = [['ttype','=','many2one'],['model','=','hr.employee']];
        rpc.query({
                model: 'ir.model.fields',
                method: 'search_read',
                domain: domain,
            }, {
                timeout: 3000,
                shadow: true,
            })
            .then(function(results){
                for(var i = 0 ; i < results.length ; i++){
                    if(results[i].relation != 'res.users'){//exception, we don't need it
                        rpc.query({
                            model: results[i].relation,
                            method: 'search_read',
                        }, {
                            timeout: 10000,
                            shadow: true,
                        })
                        .then(function(results){
                            if(results.length){
                                if(results[0].parent_id != undefined){
                                    
                                }
                            }
                        }, function(type,err){ 
                            //def.reject();
                            console.log(err);
                        });
                    }
                }
                //if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
                //    def.resolve();
                //} else {
                //    def.reject();
                //}
            }, function(type,err){ 
                //def.reject();
                console.log(err);
            });


        return def;
    },*/
    /**
     * Main render function for the list.  It is rendered as a table. For now,
     * this method does not wait for the field widgets to be ready.
     *
     * @override
     * @private
     * returns {Deferred} this deferred is resolved immediately
     */
    _renderView: function () {
        var self = this;

        this.$el
            .removeClass('table-responsive')
            .empty();

        // destroy the previously instantiated pagers, if any
        _.invoke(this.pagers, 'destroy');
        this.pagers = [];

        // display the no content helper if there is no data to display
        if (!this._hasContent() && this.noContentHelp) {
            this._renderNoContentHelper();
            return this._super();
        }
        //console.log(this.state.data);
        var def  = new $.Deferred();

        var parent_data = [];
        var listlist = [];
        //var limitlimit = 0;
        if(this.state.data.length){
            //var domain = [['ttype','=','many2one'],['model','=',this.state.data[0].model]];
            rpc.query({
                    model: 'ir.model.fields',
                    method: 'search_read',
                    domain: [['ttype','=','many2one'],['model','=',this.state.data[0].model]],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function(results){
                    parent_data = results;
                    var limitlimit = results.length;
                    for(var i = 0 ; i < results.length ; i++){
                        //var selected_field = results[i];
                        //var resolve_counter_array = limitlimit;
                        //self.state.hierarchy_parent_limit = results.length - 2; //minus unique create_uid, write_uid(res.users)
                        if(results[i].relation == 'res.users'){//CHANGE TO NAME CREATE_UID AND WRITE_UID
                            limitlimit--;
                        }else{
                            //if(self.state.hierarchy_parent_tag.length < self.state.hierarchy_parent_limit){
                            //    self.state.hierarchy_parent_tag.push(results[i].relation)    
                            //}
                            rpc.query({
                                model: 'ir.model.fields',
                                method: 'search_read',
                                domain: [['ttype','=','many2one'],['model','=',results[i].relation],['name','=','parent_id']],
                                //fields: ['relation'],
                            }, {
                                timeout: 9999,
                                shadow: true,
                            })
                            .then(function(results){
                                limitlimit--;
                                if(results.length == 1){
                                    listlist.push(results[0]);//only 1 parent_id
                                }
                                if(limitlimit == 0){
                                    def.resolve();
                                }
                            }, function(type,err){ 
                                def.reject();
                                console.log(err);
                            });
                        }
                    }
                }, function(type,err){ 
                    def.reject();
                    console.log(err);
                });
        }

        var $parentSelect = $('<div>').css('display','flex');
        $parentSelect.css('min-height', '80px');//maintain height
        def.done(function () {
            var selectable_relation = [];
            for(var i = 0 ; i < listlist.length ; i++){
                selectable_relation.push(listlist[i].relation);
            }

            //filter selectable to uniques
            selectable_relation = _.filter(selectable_relation, function(v, i, t){
                return t.indexOf(v) === i;
            });

            //insert selecttable data with parent id
            var parent_id_data = [];
            for(var i = 0 ; i < selectable_relation.length ; i++){
                for(var j = 0 ; j < parent_data.length ; j++){
                    if(parent_data[j].relation == selectable_relation[i]){
                        parent_id_data.push(parent_data[j]);
                    }
                }
            }
            //render selectable block
            var flex = (100 / (parent_id_data.length+1)) < 10 ? 10 : (100 / (parent_id_data.length+1));
            for(var i = 0 ; i < parent_id_data.length ; i++){
                if(self.state.data[0].data[parent_id_data[i].name] !== undefined){
                    var $a = ($('<a>').css('flex','0 0 '+flex+'%').attr('data-relation',parent_id_data[i].relation).attr('data-name',parent_id_data[i].name));
                    var $i = $('<i>').addClass('fa fa-sitemap fa-3x').css('display','block');
                    var $span = $('<span>').text(parent_id_data[i].field_description);
                    if(parent_id_data[i].name == 'parent_id'){
                        $i.removeClass('fa-sitemap').addClass('fa-child');
                        var $div = $('<div>').addClass('parentid_primary').append($i).append($span); 
                    }else{
                        var $div = $('<div>').addClass('parentid_item').append($i).append($span); 
                    }
                    
                    $a.append($div);
                    $a.click(function(){
                        self._revokeParent($(this).attr('data-relation'),$(this).attr('data-name'));
                        //self._revokeParent($(this).parent().children().index(this));
                    });
                    if(parent_id_data[i].name == 'parent_id'){
                        $parentSelect.prepend($a);
                    }else{
                        $parentSelect.append($a);    
                    }
                    
                }
            }
            var grouped = !!self.state.groupedBy.length;
            if(!grouped){
                var $a = ($('<a>').css('flex','0 0 '+flex+'%'));
                var $i = $('<i>').addClass('fa fa-remove fa-3x').css('display','block');
                var $span = $('<span>').text("Clear Structure");
                var $div = $('<div>').addClass('parentid_item').append($i).append($span); 
                $a.append($div);
                $a.click(function(){
                    self.h_view_active = false;
                    self._renderView();
                })
                $parentSelect.append($a);
            }
        });

        self.h_view_active;
        self.h_view_roots;
        self.h_view_cancel;
        self.data_length_pager;//fix for filtering
        if(self.data_length_pager != this.state.data.length){
            self.data_length_pager = this.state.data.length;
            self.h_view_active = false;
        }else{
        }

        //TODO FILL PARENT ID SELECTOR
        var $table = $('<table>').addClass('o_list_view table table-condensed table-striped');
        this.$el
            .addClass('table-responsive')
            .append($parentSelect)
            .append($table);
        var is_grouped = !!this.state.groupedBy.length;
        this._computeAggregates();
        $table.toggleClass('o_list_view_grouped', is_grouped || (self.h_view_active == true));//style rows
        $table.toggleClass('o_list_view_ungrouped', !is_grouped && (self.h_view_active == undefined));
        if (is_grouped) {
            $table
                .append(this._renderHeader(true))
                .append(this._renderGroups(this.state.data))
                .append(this._renderFooter(true));
        } else {
            $table
                .append(this._renderHeader())
                //.append(this._renderBody())
                .append(this._renderTrees(self.h_view_active, self.h_view_roots))
                .append(this._renderFooter());
        }
        if (this.selection.length) {
            var $checked_rows = this.$('tr').filter(function (index, el) {
                return _.contains(self.selection, $(el).data('id'));
            });
            $checked_rows.find('.o_list_record_selector input').prop('checked', true);
        }
        return this._super();
    },
    
    /**
     * Each line can be decorated according to a few simple rules. The arch
     * description of the list may have one of the decoration-X attribute with
     * a domain as value.  Then, for each record, we check if the domain matches
     * the record, and add the text-X css class to the element.  This method is
     * concerned with the computation of the list of css classes for a given
     * record.
     *
     * @private
     * @param {Object} record a basic model record
     * @param {jQueryElement} $tr a jquery <tr> element (the row to add decoration)
     */
    _setDecorationClasses: function (record, $tr) {
        _.each(this.rowDecorations, function (expr, decoration) {
            var cssClass = decoration.replace('decoration', 'text');
            $tr.toggleClass(cssClass, py.PY_isTrue(py.evaluate(expr, record.evalContext)));
        });
    },
    /**
     * Update the footer aggregate values.  This method should be called each
     * time the state of some field is changed, to make sure their sum are kept
     * in sync.
     *
     * @private
     */
    _updateFooter: function () {
        this._computeAggregates();
        this.$('tfoot').replaceWith(this._renderFooter(!!this.state.groupedBy.length));
    },
    /**
     * Whenever we change the state of the selected rows, we need to call this
     * method to keep the this.selection variable in sync, and also to recompute
     * the aggregates.
     *
     * @private
     */
    _updateSelection: function () {
        var $selectedRows = this.$('tbody .o_list_record_selector input:checked')
                                .closest('tr');
        this.selection = _.map($selectedRows, function (row) {
            return $(row).data('id');
        });
        this.trigger_up('selection_changed', { selection: this.selection });
        this._updateFooter();
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} event
     */
    _onRowClicked: function (event) {
        // The special_click property explicitely allow events to bubble all
        // the way up to bootstrap's level rather than being stopped earlier.
        if (!$(event.target).prop('special_click')) {
            var id = $(event.currentTarget).data('id');
            if (id) {
                this.trigger_up('open_record', {id:id, target: event.target});
            }
        }
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onSelectRecord: function (event) {
        event.stopPropagation();
        this._updateSelection();
        if (!$(event.currentTarget).find('input').prop('checked')) {
            this.$('thead .o_list_record_selector input').prop('checked', false);
        }
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onSortColumn: function (event) {
        var name = $(event.currentTarget).data('name');
        this.trigger_up('toggle_column_order', {id: this.state.id, name: name});
    },
    /**
     * @private
     * @param {MouseEvent} event
     */
    _onToggleGroup: function (event) {
        var group = $(event.currentTarget).data('group');
        if (group.count) {
            this.trigger_up('toggle_group', {group: group});
        }
    },
    /**
     * When the user clicks on the 'checkbox' on the left of a record, we need
     * to toggle its status.
     *
     * @private
     * @param {MouseEvent} event
     */
    _onToggleSelection: function (event) {
        var checked = $(event.currentTarget).prop('checked') || false;
        this.$('tbody .o_list_record_selector input').prop('checked', checked);
        this._updateSelection();
    },
});

return HierarchyRenderer;
});
