from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpWasteWizard(models.TransientModel):
    _name = 'mrp.waste.wizard'
    _description = 'Waste Wizard for MO'

    production_id = fields.Many2one('mrp.production', required=True)
    product_id = fields.Many2one('product.product', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', readonly=True)
    product_qty = fields.Float(string="Produced Quantity", readonly=True)
    waste_qty = fields.Float(string="Waste Quantity", required=True)

    @api.constrains('waste_qty')
    def _check_max_waste(self):
        for rec in self:
            if rec.waste_qty > rec.product_qty * 0.05:
                raise UserError("Maximum allowed waste is 5% of the produced quantity.")

    def action_apply_waste(self):
        self.ensure_one()
        production = self.production_id

        if production.state not in ['progress', 'done']:
            raise UserError("You can only register waste when MO is in 'In Progress' or 'Done'.")

        # Scrap for Finished Good
        self.env['stock.scrap'].create({
            'product_id': production.product_id.id,
            'product_uom_id': production.product_uom_id.id,
            'scrap_qty': self.waste_qty,
            'origin': production.name,
            'company_id': production.company_id.id,
            'location_id': production.location_dest_id.id,
            'production_id': production.id,
            'scrap_type': 'fg',
        })

        # Scrap for all components
        for move in production.move_raw_ids.filtered(lambda m: m.state != 'cancel'):
            component_waste_qty = move.product_uom_qty * (self.waste_qty / self.product_qty)
            self.env['stock.scrap'].create({
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'scrap_qty': component_waste_qty,
                'origin': production.name,
                'company_id': production.company_id.id,
                'location_id': move.location_id.id,
                'production_id': production.id,
                'scrap_type': 'component',
            })
