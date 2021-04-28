odoo.define('web.ChangeBackground', function (require) {
"use strict";

var session = require('web.session');
var rpc = require('web.rpc');

var def  = new $.Deferred();
var url = session.url('/web/image', {
            model: 'res.company',
            id: session.company_id,
            field: 'background_image',
        });
rpc.query({
    model: 'res.company',
    method: 'search_read',
    domain: [['id','=',session.company_id]],
}, {
    timeout: 3000,
    shadow: true,
})
.then(function(results){
    if(results.length){
        if(results[0].background_image){
            def.resolve();
        }else{
            def.reject();        
        }
    }
}, function(type,err){ 
    def.reject();
    console.log(err);
});
def.done(function () {
    function myLoop () {
       setTimeout(function () {
          $("div.o_home_menu").css({
                "background-image": "url(" + url + ")",
                "background-size": "cover"
            });
          if ($("div.o_home_menu").length <= 0) {
             myLoop();
          }
       }, 1000)
    }
    myLoop();
});

});