from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sub_bom_id = fields.Many2one('sub.bom', string="Sub BOM")
    bom_factor = fields.Float(string="BOM Factor", default=1.0, required=True)

    @api.onchange('sub_bom_id', 'bom_factor')
    def _onchange_sub_bom_id_or_bom_factor(self):
        if self.sub_bom_id:
            self.bom_line_ids = [(5, 0, 0)]
            vals_list = []
            for sub_line in self.sub_bom_id.line_ids:
                qty = (sub_line.qty_per_cig or 0.0) * (self.bom_factor or 1.0)
                vals_list.append((0, 0, {
                    'product_id': sub_line.material.id,
                    'product_qty': qty,
                    'product_uom_id': sub_line.unit.id,
                }))
            self.bom_line_ids = vals_list
