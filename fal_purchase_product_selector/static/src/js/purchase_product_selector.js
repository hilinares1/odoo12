odoo.define('fal_purchase_product_selector.EditableListRenderer', function (require) {
"use strict";

/**
 * Editable List renderer
 *
 * The list renderer is reasonably complex, so we split it in two files. This
 * file simply 'includes' the basic ListRenderer to add all the necessary
 * behaviors to enable editing records.
 *
 * Unlike Odoo v10 and before, this list renderer is independant from the form
 * view. It uses the same widgets, but the code is totally stand alone.
 */
var core = require('web.core');
var dom = require('web.dom');
var ListRenderer = require('web.ListRenderer');
var utils = require('web.utils');
var pyUtils = require('web.py_utils');

var _t = core._t;

ListRenderer.include({
    events: _.extend({}, ListRenderer.prototype.events, {
        'click .o_field_x2many_list_row_add a': '_onAddRecord',
    }),

    unselectRow: function () {
        // Protect against calling this method when no row is selected
        if (this.currentRow === null) {
            return $.when();
        }

        var record = this.state.data[this.currentRow];
        var recordWidgets = this.allFieldWidgets[record.id];
        toggleWidgets(true);

        var def = $.Deferred();
        this.trigger_up('save_line', {
            recordID: record.id,
            onSuccess: def.resolve.bind(def),
            onFailure: def.reject.bind(def),
        });
        return def.fail(toggleWidgets.bind(null, false));

        function toggleWidgets(disabled) {
            _.each(recordWidgets, function (widget) {
                var $el = widget.getFocusableElement();
                $el.prop('disabled', disabled);
            });
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * This method is called when we click on the 'Add a line' button in a sub
     * list such as a one2many in a form view.
     *
     * @param {MouseEvent} ev
     */
    _onAddRecord: function (ev) {
        // we don't want the browser to navigate to a the # url
        ev.preventDefault();

        // we don't want the click to cause other effects, such as unselecting
        // the row that we are creating, because it counts as a click on a tr
        ev.stopPropagation();

        // but we do want to unselect current row
        var self = this;
        this.unselectRow().then(function () {
            var context = ev.currentTarget.dataset.context;
            if (context && pyUtils.py_eval(context).open_purchase_product_selector){
                self.do_action({
                    name: _t('Select a product'),
                    type: 'ir.actions.act_window',
                    res_model: 'product.selector',
                    views: [[false, 'form']],
                    target: 'new',
                    context: context
                }, {
                    on_close: function (products) {
                        if (products && products !== 'special'){
                            self.trigger_up('add_record', {
                                context: self._productsToPurchaseRecords(products),
                                forceEditable: "bottom" ,
                                allowWarning: true,
                                onSuccess: function (){
                                    self.unselectRow();
                                }
                            });
                        }
                    }
                });
            } else {
                self.trigger_up('add_record', {context: context && [context]}); // TODO write a test, the deferred was not considered
            }
        });
    },

    /**
     * Will map the products to appropriate record objects that are
     * ready for the default_get
     *
     * @private
     * @param {Array} products The products to transform into records
     */
    _productsToPurchaseRecords: function (products) {
        var records = [];
        _.each(products, function (product){
            var record = {
                default_product_id: product.product_id,
                default_product_qty: product.quantity,
                default_product_uom_qty: product.quantity,
            };

            if (product.no_variant_attribute_values) {
                var default_product_no_variant_attribute_values = [];
                _.each(product.no_variant_attribute_values, function (attribute_value) {
                        default_product_no_variant_attribute_values.push(
                            [4, parseInt(attribute_value.value)]
                        );
                });
                record['default_product_no_variant_attribute_value_ids']
                    = default_product_no_variant_attribute_values;
            }

            if (product.product_custom_attribute_values) {
                var default_custom_attribute_values = [];
                _.each(product.product_custom_attribute_values, function (attribute_value) {
                    default_custom_attribute_values.push(
                            [0, 0, {
                                attribute_value_id: attribute_value.attribute_value_id,
                                custom_value: attribute_value.custom_value
                            }]
                        );
                });
                record['default_product_custom_attribute_value_ids']
                    = default_custom_attribute_values;
            }

            records.push(record);
        });

        return records;
    },

});

});
