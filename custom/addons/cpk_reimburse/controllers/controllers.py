# -*- coding: utf-8 -*-
# from odoo import http


# class CpkReimburse(http.Controller):
#     @http.route('/cpk_reimburse/cpk_reimburse', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpk_reimburse/cpk_reimburse/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpk_reimburse.listing', {
#             'root': '/cpk_reimburse/cpk_reimburse',
#             'objects': http.request.env['cpk_reimburse.cpk_reimburse'].search([]),
#         })

#     @http.route('/cpk_reimburse/cpk_reimburse/objects/<model("cpk_reimburse.cpk_reimburse"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpk_reimburse.object', {
#             'object': obj
#         })

