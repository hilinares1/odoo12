odoo.define('fal_internal_email.FalInternalEmail', function (require) {
"use strict";

var Activity = require('mail.Activity');
var AttachmentBox = require('mail.AttachmentBox');
var ChatterComposer = require('mail.composer.Chatter');
var Followers = require('mail.Followers');
var ThreadField = require('mail.ThreadField');
var mailUtils = require('mail.utils');

var concurrency = require('web.concurrency');
var config = require('web.config');
var core = require('web.core');
var Widget = require('web.Widget');
var Chatter = require('mail.Chatter');
var QWeb = core.qweb;

var ChatterExt = Chatter.include({
    init: function () {
        this._super.apply(this, arguments);
        this.events = _.extend(this.events, {
            'click .o_fal_allow_external_email': '_falAllowExternal',
            'click .o_test': '_test',
        });
        this._falDefAllowExternal();
        console.log(this);
        //this._falFilterFollowers();
    },
    update: function () {
        this._super.apply(this, arguments);
        this._falDefAllowExternal();
        //this._falFilterFollowers();
    },
    _falAllowExternal: function (ev) {
        ev.preventDefault();
        self = this;
        if(this.record.res_id){
            var kwargs = {
                value: $(".o_fal_allow_external_email").prop("checked"),
                context: {}, // FIXME
            };
            this._rpc({
                model: 'mail.thread',
                method: 'fal_allow_external',
                args: [{
                    'model': this.record.model,
                    'res_id': this.record.res_id
                }],
                kwargs: kwargs,
            })
            .then(self.trigger_up('reload', { db_id: self.record_id }));
        }
    },
    _falDefAllowExternal: function(){ //Set default value for External Textbox
        if(this.record.res_id){
            this._rpc({
                model: 'mail.thread',
                method: 'get_fal_allow_external',
                args: [{
                    'model': this.record.model,
                    'res_id': this.record.res_id
                }],
            })
            .then(function (result) {
                $(".o_fal_allow_external_email"). prop("checked", result);
            });
        }
    },
    // _falFilterFollowers: function(){ //Fitler the follower for External Textbox
    //     if(this.record.res_id){
    //         this._rpc({
    //             model: 'mail.thread',
    //             method: 'get_partners',
    //             args: [{
    //                 'model': this.record.model,
    //                 'res_id': this.record.res_id
    //             }],
    //         })
    //         .then(function (result) {
    //             //alert(result)
    //         });
    //     }
    // },

});

});

