odoo.define('fal_product_attribute.ProductAttributeFormView', function (require) {
"use strict";

var ProductAttributeFormController = require('fal_product_attribute.ProductAttributeFormController');
var ProductAttributeFormRenderer = require('fal_product_attribute.ProductAttributeFormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var ProductAttributeFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: ProductAttributeFormController,
        Renderer: ProductAttributeFormRenderer,
    }),
});

viewRegistry.add('product_attribute_form', ProductAttributeFormView);

return ProductAttributeFormView;

});