# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class marinti_mrp_tobacco(models.Model):
#     _name = 'marinti_mrp_tobacco.marinti_mrp_tobacco'
#     _description = 'marinti_mrp_tobacco.marinti_mrp_tobacco'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

