odoo.define('fal_product_attribute.ProductAttributeFormRenderer', function (require) {
"use strict";

var FormRenderer = require('web.FormRenderer');
var ProductConfiguratorMixin = require('fal_product_attribute.ProductAttributeMixin');

var ProductAttributeFormRenderer = FormRenderer.extend(ProductConfiguratorMixin ,{
    /**
     * @override
     */
    init: function (){
        this._super.apply(this, arguments);
        this.pricelistId = this.state.context.default_pricelist_id || 0;
        var get_action = false
        for (var action in arguments[0].actions) {
            get_action = action
        }
        this.model = arguments[0].actions[get_action.toString()].env.modelName;
    },
    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this.$el.append($('<div>', {class: 'configurator_container'}));
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Renders the product configurator within the form
     *
     * Will also:
     *
     * - add events handling for variant changes
     * - trigger variant change to compute the price and other
     *   variant specific changes
     *
     * @param {string} configuratorHtml the evaluated template of
     *   the product configurator
     */
    renderConfigurator: function (configuratorHtml) {
        var $configuratorContainer = this.$('.configurator_container');
        $configuratorContainer.empty();

        var $configuratorHtml = $(configuratorHtml);
        $configuratorHtml.appendTo($configuratorContainer);

        this.triggerVariantChange($configuratorContainer);
    }
});

return ProductAttributeFormRenderer;

});
