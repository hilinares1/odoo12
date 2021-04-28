odoo.define('web_tree_image.web_tree_image', function(require) {
"use strict";

var ListRenderer = require('web.ListRenderer');

	ListRenderer.include({
	    events: _.extend({}, ListRenderer.prototype.events, {
	    	'mouseover tbody tr td .o_field_image': '_onHoverRecord_img',
	    }),
		_onHoverRecord_img: function (event) {
			var get_image = $(event.currentTarget).children().attr('src')
			var img_src ="<img src="+get_image+" />"
			if (get_image === undefined) {
                img_src = $($(event.currentTarget).children()[0]).get('context').innerHTML.toString(2)
            }
	    	$(event.currentTarget).tooltip({
	    		title: img_src,
	    		delay: 0,
	    	});
		}
	});
})
