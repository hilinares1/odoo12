odoo.define('web_editor.summernote_override', function (require) {
'use strict';

var core = require('web.core');

var editor = require('web_editor.summernote');

require('summernote/summernote'); // wait that summernote is loaded

var _t = core._t;

var options = $.summernote.options;

options.fontSizes = [_t('Default'), 8, 9, 10, 11, 12, 13, 14, 16, 18, 24, 36, 48, 62];

return $.summernote;

});