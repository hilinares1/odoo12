odoo.define('fal_sale_calculator.ProductAttributeFormController', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;
var FormController = require('web.FormController');
var OptionalProductsModal = require('fal_product_attribute.OptionalAttributeModal');
var ProductSelectorFromController = require('fal_product_attribute.ProductAttributeFormController');

var ProductAttributeFormController = ProductSelectorFromController.include({
    onChangeInput: function (ev) {
        var self = this;
        var $parent = $(ev.target).closest('.js_product');
        var variantToPass = [];
        var variants = $parent.find('input.js_variant_change:checked, select.js_variant_change option:selected');
        // Custom value for sale calculator (06/05/2019)
        var customs = $('div.active').find('input[type=text].form-control');
        var custom_value = [];
        var data = [];
        for(var i = 0 ; i < variants.length ; i++){
            if(variants[i].attributes && variants[i].attributes !== undefined){
                if(variants[i].attributes.value && variants[i].attributes.value !== undefined){
                    if(customs.length > 0){
                        custom_value[i] = "0";
                        for(var j = 0; j < customs.length; j++){
                            if(customs[j].id == "attr"+variants[i].attributes.atribute.value){
                                custom_value[i] = customs[j].value;
                            }
                        }
                    } else {
                        custom_value[i] = "0";
                    }
                    variantToPass.push({attribute_id:variants[i].attributes.atribute.value,value_id:variants[i].attributes.value.value,custom_value:custom_value[i]});
                }
            }
        }
        //console.log(variantToPass);
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
                data[variantToPass[i].attribute_id] = variantToPass[i].custom_value;
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
                    var $avTextbox = $("<input type='text' class='form-control' id='attr"+$(this).attr('atribute')+"' value='"+data[$(this).attr('atribute')]+"'>");  
                    $avTextbox.attr('av-id',$(this).attr('value'));
                    $avTextbox.attr('av-name',$(this).attr('value-name'));
                    $(this).parent().append($avTextbox);
                    $('input[type=text][id=attr'+$(this).attr('atribute')+']').on('change', function(ev){
                        self.onChangeInput(ev);
                    });
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
                    //Pass total unit price after calculating sale price based on product attribute value (06/05/2019)
                    if(parseFloat($(ev.target).attr('price_unit')) == undefined){ 
                        var price_unit = 0.00;
                    } else {
                        var price_unit = parseFloat($(ev.target).attr('price-unit'));
                    }
                    self.modalConfirm(id,qty,tmplid,price_unit);
                });
            });
        });
    },

    modalConfirm: function (productId, productQuantity, productTmplId, price_unit) {
        
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
                    console.log(results)
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
                        price_unit: price_unit,
                    });
                    self._addProducts(products);

                }else if(noVariantAttributeValues.length < noVarAttrs){
                    myLoop();
                }else{
                    products.push({
                        product_id: productId,
                        quantity: productQuantity,
                        price_unit: price_unit,
                        no_variant_attribute_values: noVariantAttributeValues
                    });
                    self._addProducts(products);
                }
            }, 300)
        }
        myLoop();
        
    },
});

});
