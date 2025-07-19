from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_mc = fields.Float(
        string="QTY/MC",
        compute='_compute_qty_mc',
        store=True,
        readonly=True,
    )

    @api.depends('raw_material_production_id.bom_id', 'product_id')
    def _compute_qty_mc(self):
        for move in self:
            qty = 0.0
            if move.raw_material_production_id and move.raw_material_production_id.bom_id:
                bom_line = move.raw_material_production_id.bom_id.bom_line_ids.filtered(
                    lambda l: l.product_id == move.product_id
                )
                if bom_line:
                    qty = bom_line[0].product_qty
            move.qty_mc = qty
