from odoo import models, fields, api

class SubBOM(models.Model):
    _name = "sub.bom"
    _description = "Sub Bill of Materials"

    name = fields.Char(string="BOM Name", required=True)
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True
    )
    type = fields.Selection([
        ('making', 'Making'),
        ('packing', 'Packing'),
        ('normal', 'Normal'),
    ], string="BOM Type", default='making', required=True)
    line_ids = fields.One2many('sub.bom.line', 'bom_id', string="BOM Lines")


class SubBOMLine(models.Model):
    _name = "sub.bom.line"
    _description = "Sub BOM Line"

    bom_id = fields.Many2one('sub.bom', string="BOM", required=True, ondelete='cascade')
    material = fields.Many2one('product.product', string="Material", required=True)
    item_code = fields.Char(string="Item Code", compute='_compute_item_code', store=True, readonly=True)
    unit = fields.Many2one('uom.uom', string="Unit", required=True)
    qty_per_cig = fields.Float(string="Qty /Cigarette", required=True, digits=(12, 6))
    special_calc = fields.Boolean(string="Use Special Calculation")

    @api.depends('material')
    def _compute_item_code(self):
        for line in self:
            line.item_code = line.material.default_code or ''
            line.unit = line.material.uom_id.id if line.material and line.material.uom_id else False
