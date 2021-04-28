odoo.define('fal_product_attribute.ProductAttributeFormController', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;
var FormController = require('web.FormController');
var OptionalProductsModal = require('fal_product_attribute.OptionalAttributeModal');

var ProductAttributeFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        field_changed: '_onFieldChanged'
    }),
    className: 'o_product_configurator',
    /**
     * @override
     */
    init: function (){
        this._super.apply(this, arguments);
        var self = this;

        this._rpc({
            route: '/product_selector/configure',
            params: {
                model: this.renderer.model,
                variants: [],
                //product_id: product_id,
                //pricelist_id: this.renderer.pricelistId
            }
        }).then(function (configurator) {
            self.renderer.renderConfigurator(configurator);
            self.$el.find('input.js_variant_change, select.js_variant_change').each(function(){
                $(this).on('change', function(ev){
                    self.onChangeInput(ev);
                });
            });
        });
    },

    onChangeInput: function (ev) {
        var self = this;
        var $parent = $(ev.target).closest('.js_product');
        var variantToPass = [];
        var variants = $parent.find('input.js_variant_change:checked, select.js_variant_change option:selected');
        for(var i = 0 ; i < variants.length ; i++){
            if(variants[i].attributes && variants[i].attributes !== undefined){
                if(variants[i].attributes.value && variants[i].attributes.value !== undefined){
                    variantToPass.push({attribute_id:variants[i].attributes.atribute.value,value_id:variants[i].attributes.value.value});
                }
            }
        }
        this._rpc({
            route: '/product_selector/configure',
            params: {
                model: this.renderer.model,
                variants: variantToPass,
            }
        }).then(function (configurator) {

            var $configuratorContainer = self.$('.configurator_container');
            $configuratorContainer.empty();
            var $configuratorHtml = $(configurator);
            $configuratorHtml.appendTo($configuratorContainer);

            for(var i = 0 ; i < variantToPass.length ; i++){
                $('input[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').attr('checked', true);
                $('input[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').parent().addClass("active");
                $('option[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').attr('selected', true);
                var $avImage = $("<img width='160' height='90' src='/web/image/product.attribute.value/"+variantToPass[i].value_id+"/attribute_value_image'>");
                $('.attributeImage[image_id='+variantToPass[i].attribute_id+']').find('img').remove();
                $('.attributeImage[image_id='+variantToPass[i].attribute_id+']').append($avImage);
            }
            self.$el.find('input.js_variant_change').each(function(){

                $(this).on('click', function(ev){
                    if($(this).attr('checked') === 'checked'){
                        $(this).attr('checked', false);
                        $(this).parent().removeClass("active");
                        self.onChangeInput(ev);
                    }
                });
                if($(this).attr('data-is_custom') && $(this).attr('checked') == 'checked'){
                    var $avTextbox = $("<input type='text' class='form-control'>");
                    $(this).parent().append($avTextbox);
                }
            });
            self.$el.find('input.js_variant_change, select.js_variant_change').each(function(){
                $(this).on('change', function(ev){
                    self.onChangeInput(ev);
                });
            });

            self.$el.find('button.add_one').each(function(){
                $(this).on('click', function(ev){
                    var qty = parseInt($(this).closest('div.input-group').find('button[name="actionadd"]').attr('product-variant-quantity'));
                    $(this).closest('div.input-group').find('button[name="actionadd"]').attr('product-variant-quantity', qty+1);

                });
            });

            self.$el.find('button.remove_one').each(function(){
                $(this).on('click', function(ev){
                    var qty = parseInt($(this).closest('div.input-group').find('button[name="actionadd"]').attr('product-variant-quantity'));
                    if(qty > 1){
                        $(this).closest('div.input-group').find('button[name="actionadd"]').attr('product-variant-quantity', qty-1);
                    }
                });
            });

            self.$el.find('button[name="actionadd"]').each(function(){
                $(this).on('click', function(ev){
                    var id = parseInt($(ev.target).attr('product-variant-id'));
                    var qty = parseInt($(ev.target).attr('product-variant-quantity'));
                    var tmplid = parseInt($(ev.target).attr('product-variant-template-id'));
                    self.modalConfirm(id,qty,tmplid);
                });
            });
        });
    },
    /**
     * We need to override the default click behavior for our "Add" button
     * because there is a possibility that this product has optional products.
     * If so, we need to display an extra modal to choose the options.
     *
     * @override
     */
    _onButtonClicked: function (event) {
        var self = this;
        if (event.stopPropagation){
            event.stopPropagation();
        }
        var attrs = event.data.attrs;
        if (attrs.special === 'cancel') {
            this._super.apply(this, arguments);
        } else {
            /*if(event.target.recordData){
                self.fal_selectedProductID = event.target.recordData.id;
                self.modalConfirm(self.fal_selectedProductID);
            }*/
            /*if (!this.$el
                    .parents('.modal')
                    .find('.o_sale_product_selector_add')
                    .hasClass('disabled')){
                this._handleAdd(this.$el, self.fal_selectedProductID);
            }*/
        }
    },

    modalConfirm: function (productId, productQuantity, productTmplId) {

        var products = [];
        var self = this;
        var noVariantAttributeValues = [];
        var noVarAttrs = 0;
        var selectedVariantNotInProductTemplate = 0;
        self.$el.find('input[checked="checked"], option[selected="selected"]').each(function(){

            if($(this).attr('attribute-create-variant') === "no_variant"){
                noVarAttrs++;
                var attrName = $(this).attr('attribute-name');
                var attrValueId = parseInt($(this).attr('value'));
                var attrValueName = $(this).attr('value-name');
                rpc.query({
                    model: 'product.template.attribute.value',
                    method: 'search_read',
                    domain: [['product_attribute_value_id','=',parseInt($(this).attr('value'))],['product_tmpl_id','=',productTmplId]],
                }, {
                    timeout: 2000,
                    shadow: true,
                })
                .then(function(results){
                    if(results.length){
                        noVariantAttributeValues.push({
                            attribute_name: attrName,
                            attribute_value_id: attrValueId,
                            attribute_value_name: attrValueName,
                            value: results[0].id.toString(),
                        });
                    }else{
                        selectedVariantNotInProductTemplate = 1;
                    }
                });

            }
        });
        function myLoop () {
            setTimeout(function () {
                if(selectedVariantNotInProductTemplate){
                    products.push({
                        product_id: productId,
                        quantity: productQuantity,
                    });
                    self._addProducts(products);

                }else if(noVariantAttributeValues.length < noVarAttrs){
                    myLoop();
                }else{
                    products.push({
                        product_id: productId,
                        quantity: productQuantity,
                        no_variant_attribute_values: noVariantAttributeValues
                    });
                    self._addProducts(products);
                }
            }, 300)
        }
        myLoop();

    },
    /**
     * This is overridden to allow catching the "select" event on our product template select field.
     * This will not work anymore if more fields are added to the form.
     * TODO awa: Find a better way to catch that event.
     *
     * @override
     */
    _onFieldChanged: function (event) {
        this._super.apply(this, arguments);
        var self = this;
        //var product_id = event.data.changes.product_template_id.id;

        // check to prevent traceback when emptying the field
        /*if (!product_id) {
            return;
        }*/
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
    * When the user adds a product that has optional products, we need to display
    * a window to allow the user to choose these extra options.
    *
    * This will also create the product if it's in "dynamic" mode
    * (see product_attribute.create_variant)
    *
    * @private
    * @param {$.Element} $modal
    */
    _handleAdd: function ($modal, id) {
        var self = this;

    },

    /**
     * No optional products found for this product, only add the root product
     *
     * @private
     */
    _onModalOptionsEmpty: function () {
        this._addProducts([this.rootProduct]);
    },

    /**
     * Add all selected products
     *
     * @private
     */
    _onModalConfirm: function () {
        this._addProducts(this.optionalProductsModal.getSelectedProducts());
    },

    /**
     * Update product configurator form
     * when quantity is updated in the optional products window
     *
     * @private
     * @param {integer} quantity
     */
    _onOptionsUpdateQuantity: function (quantity) {
        this.$el
            .find('input[name="add_qty"]')
            .val(quantity)
            .trigger('change');
    },

    /**
    * This triggers the close action for the window and
    * adds the product as the "infos" parameter.
    * It will allow the caller (typically the SO line form) of this window
    * to handle the added products.
    *
    * @private
    * @param {Array} products the list of added products
    *   {integer} products.product_id: the id of the product
    *   {integer} products.quantity: the added quantity for this product
    *   {Array} products.product_custom_attribute_values:
    *     see product_configurator_mixin.getCustomVariantValues
    *   {Array} products.no_variant_attribute_values:
    *     see product_configurator_mixin.getNoVariantAttributeValues
    */
    _addProducts: function (products) {
        this.do_action({type: 'ir.actions.act_window_close', infos: products});
    }
});

return ProductAttributeFormController;

});