odoo.define('web.FalInternalMessage', function (require) {
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

ChatterComposer.include({
    _preprocessMessage: function () {
        var self = this;
        var def = $.Deferred();
        this._super().then(function (message) {
            message = _.extend(message, {
                subtype: 'mail.mt_comment',
                message_type: 'comment',
                context: self.context,
            });
            // Subtype
            if (self.options.isLog) {
                message.subtype = 'mail.mt_note';
            }
            if (self.options.isInternalMessage) {
                message.subtype = 'mail.mt_internal_message';
            }

            // Partner_ids
            if (!self.options.isLog) {
                var checkedSuggestedPartners = self._getCheckedSuggestedPartners();
                self._checkSuggestedPartners(checkedSuggestedPartners).done(function (partnerIDs) {
                    message.partner_ids = (message.partner_ids || []).concat(partnerIDs);
                    // update context
                    message.context = _.defaults({}, message.context, {
                        mail_post_autofollow: true,
                    });
                    def.resolve(message);
                });
            } else {
                def.resolve(message);
            }

        });

        return def;
    },
});

Chatter.include({
    events: {
        'click .o_chatter_button_new_internal_message': '_onOpenComposerInternalMessage',
        'click .o_chatter_button_new_message': '_onOpenComposerMessage',
        'click .o_chatter_button_log_note': '_onOpenComposerNote',
        'click .o_chatter_button_attachment': '_onClickAttachmentButton',
        'click .o_chatter_button_schedule_activity': '_onScheduleActivity',
    },
    _onOpenComposerInternalMessage: function () {
        var self = this;
        if (!this.suggested_partners_def) {
            this.suggested_partners_def = $.Deferred();
            var method = 'message_get_suggested_recipients';
            var args = [[this.context.default_res_id], this.context];
            this._rpc({model: this.record.model, method: method, args: args})
                .then(function (result) {
                    if (!self.suggested_partners_def) {
                        return; // widget has been reset (e.g. we just switched to another record)
                    }
                    var suggested_partners = [];
                    var thread_recipients = result[self.context.default_res_id];
                    _.each(thread_recipients, function (recipient) {
                        var parsed_email = recipient[1] && mailUtils.parseEmail(recipient[1]);
                        suggested_partners.push({
                            checked: true,
                            partner_id: recipient[0],
                            full_name: recipient[1],
                            name: parsed_email[0],
                            email_address: parsed_email[1],
                            reason: recipient[2],
                        });
                    });
                    self.suggested_partners_def.resolve(suggested_partners);
                });
        }
        this.suggested_partners_def.then(function (suggested_partners) {
            self._openComposer({ isLog: false, isInternalMessage: true, isNormalMessage: false, suggested_partners: suggested_partners });
        });
    },

    _onOpenComposerMessage: function () {
        var self = this;
        if (!this.suggested_partners_def) {
            this.suggested_partners_def = $.Deferred();
            var method = 'message_get_suggested_recipients';
            var args = [[this.context.default_res_id], this.context];
            this._rpc({model: this.record.model, method: method, args: args})
                .then(function (result) {
                    if (!self.suggested_partners_def) {
                        return; // widget has been reset (e.g. we just switched to another record)
                    }
                    var suggested_partners = [];
                    var thread_recipients = result[self.context.default_res_id];
                    _.each(thread_recipients, function (recipient) {
                        var parsed_email = recipient[1] && mailUtils.parseEmail(recipient[1]);
                        suggested_partners.push({
                            checked: true,
                            partner_id: recipient[0],
                            full_name: recipient[1],
                            name: parsed_email[0],
                            email_address: parsed_email[1],
                            reason: recipient[2],
                        });
                    });
                    self.suggested_partners_def.resolve(suggested_partners);
                });
        }
        this.suggested_partners_def.then(function (suggested_partners) {
            self._openComposer({ isLog: false, isInternalMessage: false, isNormalMessage: true, suggested_partners: suggested_partners });
        });
    },

    _onOpenComposerNote: function () {
        this._openComposer({ isLog: true , isInternalMessage: false, isNormalMessage: false});
    },

    _openComposer: function (options) {
        var self = this;
        var oldComposer = this._composer;
        // create the new composer
        this._composer = new ChatterComposer(this, this.record.model, options.suggested_partners || [], {
            commandsEnabled: false,
            context: this.context,
            inputMinHeight: 50,
            isLog: options && options.isLog,
            isInternalMessage: options && options.isInternalMessage,
            isNormalMessage: options && options.isNormalMessage,
            recordName: this.recordName,
            defaultBody: oldComposer && oldComposer.$input && oldComposer.$input.val(),
            defaultMentionSelections: oldComposer && oldComposer.getMentionListenerSelections(),
        });
        this._composer.on('input_focused', this, function () {
            this._composer.mentionSetPrefetchedPartners(this._mentionSuggestions || []);
        });
        this._composer.insertAfter(this.$('.o_chatter_topbar')).then(function () {
            // destroy existing composer
            if (oldComposer) {
                oldComposer.destroy();
            }
            if (!config.device.isMobile) {
                self._composer.focus();
            }
            self._composer.on('post_message', self, function (messageData) {
                self._discardOnReload(messageData).then(function () {
                    self._disableComposer();
                    self.fields.thread.postMessage(messageData).then(function () {
                        self._closeComposer(true);
                        if (self._reloadAfterPost(messageData)) {
                            self.trigger_up('reload');
                        } else if (messageData.attachment_ids.length) {
                            self.trigger_up('reload', {fieldNames: ['message_attachment_count']});
                        }
                    }).fail(function () {
                        self._enableComposer();
                    });
                });
            });
            self._composer.on('need_refresh', self, self.trigger_up.bind(self, 'reload'));
            self._composer.on('close_composer', null, self._closeComposer.bind(self, true));

            self.$el.addClass('o_chatter_composer_active');
            self.$('.o_chatter_button_new_internal_message, .o_chatter_button_new_message, .o_chatter_button_log_note').removeClass('o_active');
            self.$('.o_chatter_button_new_message').toggleClass('o_active', self._composer.options.isNormalMessage);
            self.$('.o_chatter_button_new_internal_message').toggleClass('o_active', self._composer.options.isInternalMessage);
            self.$('.o_chatter_button_log_note').toggleClass('o_active', self._composer.options.isLog);
        });
    },
});

});
