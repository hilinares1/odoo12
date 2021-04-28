odoo.define('fal_production_order_product_selector', function (require) {
"use strict";

	var relational_fields = require('product.product_attribute');

	relational_fields.include({
	    init: function (parent, state, params) {
	        this._super.apply(this, arguments);
	        if (this.model_name !== undefined) {
	            this.model_name.push("fal.production.order");
	        }
	    },
	});
});
