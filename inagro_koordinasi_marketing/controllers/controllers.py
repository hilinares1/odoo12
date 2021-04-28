# -*- coding: utf-8 -*-
from odoo import http

# class InagroKoordinasiMarketing(http.Controller):
#     @http.route('/inagro_koordinasi_marketing/inagro_koordinasi_marketing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inagro_koordinasi_marketing/inagro_koordinasi_marketing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inagro_koordinasi_marketing.listing', {
#             'root': '/inagro_koordinasi_marketing/inagro_koordinasi_marketing',
#             'objects': http.request.env['inagro_koordinasi_marketing.inagro_koordinasi_marketing'].search([]),
#         })

#     @http.route('/inagro_koordinasi_marketing/inagro_koordinasi_marketing/objects/<model("inagro_koordinasi_marketing.inagro_koordinasi_marketing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inagro_koordinasi_marketing.object', {
#             'object': obj
#         })