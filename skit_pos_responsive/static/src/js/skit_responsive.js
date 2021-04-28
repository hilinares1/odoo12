odoo.define('skit_pos_responsive.skit_responsive',function(require){
    "use strict";
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var NumpadWidget = screens.NumpadWidget;
	var gui = require('point_of_sale.gui');
	var core = require('web.core');
	var _t  = core._t;
	var QWeb = core.qweb;
	var ClientListScreenWidget = screens.ClientListScreenWidget;
	var ActionpadWidget = screens.ActionpadWidget;
	var ProductScreenWidget = screens.ProductScreenWidget;
	var chrome = require('point_of_sale.chrome');

	var _super_posmodel = models.PosModel.prototype;
	
	ActionpadWidget.include({	
	    template: 'ActionpadWidget',
	    /*guest function for mobile guest button for restaurant*/
	    mbl_guests: function() {
	        if (this.pos.get_order()) {
	            return this.pos.get_order().customer_count;
	        } else {
	            return 1;
	        }
	    },
	    /*guest function for mobile guest button for restaurant*/
	    
	    /*Start code for print bill function for mobile for restaurant*/
	    print_xml: function(){
	        var order = this.pos.get('selectedOrder');
	        if(order.get_orderlines().length > 0){
	            var receipt = order.export_for_printing();
	            receipt.bill = true;
	            this.pos.proxy.print_receipt(QWeb.render('BillReceipt',{
	                receipt: receipt, widget: this, pos: this.pos, order: order,
	            }));
	        }
	    },
	    /*End code for print bill function for mobile for restaurant*/
	    renderElement: function() {
	        var self = this;
	        this._super();
	        this.$('.show_numpad').click(function(){
	        	$(".pos .leftpane .numpad").slideToggle("slow");
	        	//$(".pos .control-buttons").slideToggle("slow");
	        });
	        /*Start code for new mobile guest button for restaurant*/
	        this.$('.show_res_guest').click(function(){
	        	self.gui.show_popup('number', {
	                'title':  _t('Guests ?'),
	                'cheap': true,
	                'value':   self.pos.get_order().customer_count,
	                'confirm': function(value) {
	                    value = Math.max(1,Number(value));
	                    self.pos.get_order().set_customer_count(value);
	                    self.renderElement();
	                },
	            });
	        });
	        /*End code for new mobile guest button for restaurant*/
	        /*Start code for new mobile Note button for restaurant*/
	        this.$('.show_res_note').click(function(){
	        	var line = self.pos.get_order().get_selected_orderline();
	            if (line) {
	                self.gui.show_popup('textarea',{
	                    title: _t('Add Note'),
	                    value:   line.get_note(),
	                    confirm: function(note) {
	                        line.set_note(note);
	                    },
	                });
	            }
	        });
	        /*End code for new mobile Note button for restaurant*/
	        /*Start code for new mobile Transfer button for restaurant*/
	        this.$('.show_res_transfer').click(function(){
	        	self.pos.transfer_order_to_different_table();
	        });
	        /*End code for new mobile Transfer button for restaurant*/
	        /*Start code for new mobile bill button for restaurant*/
	        this.$('.show_res_bill').click(function(){
	        	if (!self.pos.config.iface_print_via_proxy) {
	                self.gui.show_screen('bill');
	            } else {
	                self.print_xml();
	            }
	        });
	        /*End code for new mobile bill button for restaurant*/
	        /*Start code for new mobile splitbill button for restaurant*/
	        this.$('.show_res_splitbill').click(function(){
	        	if(self.pos.get_order().get_orderlines().length > 0){
	                self.gui.show_screen('splitbill');
	            }
	        });
	        /*End code for new mobile splitbill button for restaurant*/
	        /*Start code for new mobile order button for restaurant*/
	        this.$('.show_res_submitorder').click(function(){
	        	var order = self.pos.get_order();
	            if(order.hasChangesToPrint()){
	                order.printChanges();
	                order.saveChanges();
	            }
	        });
	        /*End code for new mobile order button for restaurant*/
	    },
	});
	
	chrome.OrderSelectorWidget.include({
	    template: 'OrderSelectorWidget',
	    init: function(parent, options) {
	        this._super(parent, options);
	    }, 
	    renderElement: function(){
	    	var self = this;
	        this._super();
	        this.$('.order-button.select-order').click(function(event){
	            $(".pos .pos-rightheader .orders").css({'display':'inline-flex'});
	        });
	        this.$('.neworder-button').click(function(event){
	            $(".pos .pos-rightheader .orders").css({'display':'inline-flex'});
	        });
	        this.$('.deleteorder-button').click(function(event){
	            $(".pos .pos-rightheader .orders").css({'display':'inline-flex'});
	        });
	        /** showorders Button click **/
	        this.$('.show_ordersbtn').click(function(event){
	        	$(".pos .pos-rightheader .orders").slideToggle("slow");
	        	$(".pos .pos-rightheader .orders").css({'display':'inline-flex'});
	        });
	    },
	});
	
});
