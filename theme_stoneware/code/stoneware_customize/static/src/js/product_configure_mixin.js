odoo.define('stoneware_customize.ProductConfiguratorMixin', function (require) {
'use strict';
var sAnimations = require('website.content.snippets.animation');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

var website_sale_utils = require('website_sale.utils');
var ajax = require('web.ajax');
var OptionalProductsModal = require('sale.OptionalProductsModal');
var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');


  
sAnimations.registry.WebsiteSale.include({
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        this._onChangeCombinationImage.apply(this, arguments);
    },
    _onChangeCombinationImage: function (ev, $parent, combination) {
    var isMainProduct = combination.product_id &&
        ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
        combination.product_id === parseInt($parent.find('.product_id').val());

    if (!this.isWebsite || !isMainProduct){
        return;
    }
	if(combination.product_id){
           		$.get("/variant_change_images",{'product': combination.product_id}).then(function data(data){
         			$('.product-img-box').empty().append(data);
         			$('#pro_detail_zoom').owlCarousel({}) 
         			$.getScript("/laze_customize/static/src/js/zoom.js");
         			$.getScript("/laze_customize/static/src/js/product_image_gallery_js.js");	              

        		})
            
       
        }
            

},
})

sAnimations.registry.WebsiteSaleOptionsFly = sAnimations.Class.extend(ProductConfiguratorMixin, {
    selector: '.oe_website_sale',
    read_events: {
        'click .pro-info .cart_fly': '_onClickSubmitFly',
    },
   _onClickSubmitFly: function (ev, forceSubmit) {
       ev.preventDefault();
        if ($(ev.currentTarget).is('.cart_fly') || $(ev.currentTarget).is('#add_to_cart')) {
            ev.preventDefault();
            var $qty_box = $("#my_cart .my_cart_btn sup.my_cart_quantity");
            ajax.jsonRpc('/shop/cart_update_only', 'call', {
                'product_id': $(ev.currentTarget).parents("form").find("input[name='product_id']").val(),
                'stop_redirect': 1
            }).then(function(data){
                if(data['cart_update_done'] === 1){
                    $qty_box.html(data['qty']);
                    website_sale_utils.animateClone($("#my_cart .my_cart_btn"), $(ev.currentTarget).closest('form'), -50, 10);
                }
            });

            return true

        }
    }
 
 })
 
 return sAnimations.registry.WebsiteSaleOptionsFly;
})

