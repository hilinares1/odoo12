odoo.define('sale_customer_checkin.geoloc', function (require)
{
    "use strict";
var fromController = require('web.FormController');
var fromRender = require('web.FormRenderer');
var FormView = require('web.FormView');
var rpc = require('web.rpc');

    fromController.include({

        _onButtonClicked: function (event) {
            console.log(event.data.attrs);
            if(event.data.attrs.custom === "getlocation"){
                if(navigator.geolocation){
                        navigator.geolocation.getCurrentPosition(function(position) {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        var ctx = {}
                        ctx['lat'] = lat;
                        ctx['lon'] = lon;
                        var userid = event.data.record.getContext().uid;
                        var partnerid = event.data.record.data.id;
                        console.log(userid);
                        console.log(partnerid);
                        rpc.query({
                            model: 'res.partner',
                            method: 'location_checkin',
                            args: [userid,partnerid,lat,lon],},
                            {timeout: 10000,});
                    });

                }
                else
                {
                    alert('Your browser does not support GeoLocation,Please upgrade your browser');
                }
            }
            this._super.apply(this, arguments);
        }
    });

});