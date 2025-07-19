# -*- coding: utf-8 -*-
# from odoo import http


# class MarintiMrpTobacco(http.Controller):
#     @http.route('/marinti_mrp_tobacco/marinti_mrp_tobacco', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/marinti_mrp_tobacco/marinti_mrp_tobacco/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('marinti_mrp_tobacco.listing', {
#             'root': '/marinti_mrp_tobacco/marinti_mrp_tobacco',
#             'objects': http.request.env['marinti_mrp_tobacco.marinti_mrp_tobacco'].search([]),
#         })

#     @http.route('/marinti_mrp_tobacco/marinti_mrp_tobacco/objects/<model("marinti_mrp_tobacco.marinti_mrp_tobacco"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('marinti_mrp_tobacco.object', {
#             'object': obj
#         })

