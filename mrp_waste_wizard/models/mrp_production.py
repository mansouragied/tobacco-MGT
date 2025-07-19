
from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_open_waste_wizard(self):
        return {
            'name': 'Register Waste',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.waste.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_production_id': self.id,
                'default_product_id': self.product_id.id,
                'default_product_uom_id': self.product_uom_id.id,
                'default_product_qty': self.product_qty,
            }
        }

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    scrap_type = fields.Selection([
        ('fg', 'Finished Good'),
        ('component', 'Component')
    ], string="Scrap Type", default='component')
