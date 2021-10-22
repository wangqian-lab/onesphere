# -*- coding: utf-8 -*-
# from odoo import http


# class OnesphereAssemablyIndustry(http.Controller):
#     @http.route('/onesphere_assemably_industry/onesphere_assemably_industry/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/onesphere_assemably_industry/onesphere_assemably_industry/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('onesphere_assemably_industry.listing', {
#             'root': '/onesphere_assemably_industry/onesphere_assemably_industry',
#             'objects': http.request.env['onesphere_assemably_industry.onesphere_assemably_industry'].search([]),
#         })

#     @http.route('/onesphere_assemably_industry/onesphere_assemably_industry/objects/<model("onesphere_assemably_industry.onesphere_assemably_industry"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('onesphere_assemably_industry.object', {
#             'object': obj
#         })
