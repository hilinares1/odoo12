odoo.define('product.product_attribute', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var pyUtils = require('web.py_utils');
var dom = require('web.dom');
var core = require('web.core');
var data = require('web.data');
var _t = core._t;
var rpc = require('web.rpc');
var dialogs = require('web.view_dialogs');
var FieldMany2One = relational_fields.FieldMany2One;

dialogs.SelectCreateDialog.include({
    open: function () {
        if (this.options.initial_view !== "search") {
            return this.create_edit_record();
        }
        var self = this;
        if (self.options.isProductAttribute){
            var user_context = this.getSession().user_context;

            var _super = this._super.bind(this);
            var context = pyUtils.eval_domains_and_contexts({
                domains: [],
                contexts: [user_context, this.context]
            }).context;
            var search_defaults = {};
            _.each(context, function (value_, key) {
                var match = /^search_default_(.*)$/.exec(key);
                if (match) {
                    search_defaults[match[1]] = value_;
                }
            });
            this.loadViews(this.dataset.model, this.dataset.get_context().eval(), [[false, 'list'], [false, 'search']], {})
                .then(this.setup.bind(this, search_defaults))
                .then(function (fragment) {
                    self.opened().then(function () {
                        if (self.options.isProductAttribute) {
                            self.$el.remove();//REMOVE PREVIOUS
                            self._rpc({
                                route: '/product_selector/configure',
                                params: {
                                    model: self.options.selfFieldMany2One.model,
                                    variants: [],
                                    many2one: true,
                                }
                            }).then(function (configuratorHtml) {
                                var $body = $('<div>', {class: 'modal-body-product-attribute',  style: 'overflow:auto'});
                                $('.modal-header').after($body);
                                var $configuratorHtml = $(configuratorHtml);
                                $configuratorHtml.appendTo($body);

                                $('input.js_variant_change, select.js_variant_change').each(function(){
                                    $(this).on('click', function(ev){
                                        if($(this).attr('type') === 'radio' && $(this).attr('checked') !== 'checked'){
                                            $(this).parent().addClass("active");
                                        }
                                    });
                                    $(this).on('change', function(ev){
                                        self.onChangeInput(ev);
                                    });

                                });


                            });
                        }
                        dom.append(self.$el, fragment, {
                            callbacks: [{widget: self.list_controller}],
                            in_DOM: true,
                        });
                        self.set_buttons(self.__buttons);
                    });
                    _super();
                });
        }
        else{
            var _super = this._super.bind(this);
            _super();
        }
        
        return this;
    },

    onChangeInput: function (ev) {
        var self = this;
        var variantToPass = [];
        var variants = $('input.js_variant_change:checked, select.js_variant_change option:selected');
        for(var i = 0 ; i < variants.length ; i++){
            if(variants[i].attributes && variants[i].attributes !== undefined){
                if(variants[i].attributes.value && variants[i].attributes.value !== undefined){
                    variantToPass.push({attribute_id:variants[i].attributes.atribute.value,value_id:variants[i].attributes.value.value});
                }
            }
        }
        self._rpc({
            route: '/product_selector/configure',
            params: {
                model: self.options.selfFieldMany2One.model,
                variants: variantToPass,
                many2one: true,
            }
        }).then(function (configuratorHtml) {
            var $body = $('.modal-body-product-attribute');
            $body.empty();
            var $configuratorHtml = $(configuratorHtml);
            $configuratorHtml.appendTo($body);

            for(var i = 0 ; i < variantToPass.length ; i++){
                $('input[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').attr('checked', true);
                $('input[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').parent().addClass("active");
                $('option[atribute="'+variantToPass[i].attribute_id+'"][value="'+variantToPass[i].value_id+'"').attr('selected', true);

                var $avImage = $("<img width='160' height='90' src='/web/image/product.attribute.value/"+variantToPass[i].value_id+"/attribute_value_image'>");
                $('.attributeImage[image_id='+variantToPass[i].attribute_id+']').find('img').remove();
                $('.attributeImage[image_id='+variantToPass[i].attribute_id+']').append($avImage);
            }

            $('input.js_variant_change, select.js_variant_change').each(function(){
                $(this).on('click', function(ev){
                    if($(this).attr('type') === 'radio' && $(this).attr('checked') !== 'checked'){
                        $(this).parent().addClass("active");
                    }
                });
                $(this).on('change', function(ev){
                    self.onChangeInput(ev);
                });
                if($(this).attr('data-is_custom') && $(this).attr('checked') == 'checked'){
                    var $avTextbox = $("<input type='text' class='form-control'>");
                    $(this).parent().append($avTextbox);
                }
            });

            $('img.product_detail_img').each(function(){
                $(this).on('click', function(ev){
                    self.options.selfFieldMany2One.reinitialize({
                        display_name: $(this).attr('product-variant-name'),
                        id: parseInt($(this).attr('product-variant-id'))
                    });
                    self.close();
                });
            });
        });
    },
});

relational_fields.FieldMany2One.include({
    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        if (this.model_name == undefined) {
            this.model_name = [];
        }
    },

    _searchCreatePopup: function (view, ids, context, isProductAttribute) {
        var self = this;
        return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, {
            res_model: this.field.relation,
            domain: this.record.getDomain({fieldName: this.name}),
            context: _.extend({}, this.record.getContext(this.recordParams), context || {}),
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: ids ? _.map(ids, function (x) { return x[0]; }) : undefined,
            initial_view: view,
            disable_multiple_selection: true,
            no_create: !self.can_create,
            isProductAttribute: isProductAttribute? isProductAttribute : false,
            selfFieldMany2One: self,
            on_selected: function (records) {
                self.reinitialize(records[0]);
                self.activate();
            }
        })).open();
    },

    _search: function (search_val) {
        console.log('gggggggggggggggggggggggggggggggg')
        var self = this;
        var def = $.Deferred();
        this.orderer.add(def);

        var context = this.record.getContext(this.recordParams);
        var domain = this.record.getDomain(this.recordParams);

        // Add the additionalContext
        _.extend(context, this.additionalContext);

        var blacklisted_ids = this._getSearchBlacklist();
        if (blacklisted_ids.length > 0) {
            domain.push(['id', 'not in', blacklisted_ids]);
        }

        this._rpc({
            model: this.field.relation,
            method: "name_search",
            kwargs: {
                name: search_val,
                args: domain,
                operator: "ilike",
                limit: this.limit + 1,
                context: context,
            }})
            .then(function (result) {
                // possible selections for the m2o
                var values = _.map(result, function (x) {
                    x[1] = self._getDisplayName(x[1]);
                    return {
                        label: _.str.escapeHTML(x[1].trim()) || data.noDisplayContent,
                        value: x[1],
                        name: x[1],
                        id: x[0],
                    };
                });

                // search more... if more results than limit
                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function () {
                            self._rpc({
                                    model: self.field.relation,
                                    method: 'name_search',
                                    kwargs: {
                                        name: search_val,
                                        args: domain,
                                        operator: "ilike",
                                        limit: 160,
                                        context: context,
                                    },
                                })
                                .then(self._searchCreatePopup.bind(self, "search"));
                        },
                        classname: 'o_m2o_dropdown_option',
                    });
                }
                var create_enabled = self.can_create && !self.nodeOptions.no_create;
                // quick create
                var raw_result = _.map(result, function (x) { return x[1]; });
                if (create_enabled && !self.nodeOptions.no_quick_create &&
                    search_val.length > 0 && !_.contains(raw_result, search_val)) {
                    values.push({
                        label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
                            $('<span />').text(search_val).html()),
                        action: self._quickCreate.bind(self, search_val),
                        classname: 'o_m2o_dropdown_option'
                    });
                }
                // create and edit ...
                if (create_enabled && !self.nodeOptions.no_create_edit) {
                    var createAndEditAction = function () {
                        // Clear the value in case the user clicks on discard
                        self.$('input').val('');
                        return self._searchCreatePopup("form", false, self._createContext(search_val));
                    };
                    values.push({
                        label: _t("Create and Edit..."),
                        action: createAndEditAction,
                        classname: 'o_m2o_dropdown_option',
                    });
                    if(self.model_name.includes(self.model)){
                        if(self.viewType == "form" && self.name == "product_id" && self.recordParams.fieldName == "product_id"){
                            var productAttributeAction = function () {
                                // Clear the value in case the user clicks on discard
                                self.$('input').val('');
                                return self._searchCreatePopup("search", false, self._createContext(search_val), true);
                                /*return self.reinitialize({
                                    display_name: "cae2",
                                    id: 53
                                });*/
                            };
                            values.push({
                                label: _t("Advanced Product Selector..."),
                                action: productAttributeAction,
                                classname: 'o_m2o_dropdown_option',
                            }); 
                        }
                    }
                    
                    
                } else if (values.length === 0) {
                    values.push({
                        label: _t("No results to show..."),
                    });
                }

                def.resolve(values);
            });

        return def;
    },
});

return relational_fields.FieldMany2One;
});
