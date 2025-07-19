from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PackingOperation(models.Model):
    _name = 'packing.operation'
    _description = 'Packing Operation'
    _rec_name = 'operation_ref'

    operation_ref = fields.Char(string="Operation Reference", readonly=True, copy=False, default='/')
    mo_id = fields.Many2one('mrp.production', string="Manufacturing Order", required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    actual_production_mc = fields.Float(string='Actual Production (MC)')
    actual_production_pack = fields.Integer(string='Actual Production Packets', compute='_compute_actual_production_pack', store=True)
    waste_kg = fields.Float(string='Waste Cig. (Kg)')
    shell_wast = fields.Float(string='Shell Waste (Kg)')
    slide_wast = fields.Float(string='Slides Waste (KG)')
    alum_foil_wast = fields.Float(string='Aluminium Foil Waste (KG)')
    waste_cig = fields.Integer(string='Waste Cig. (Cig)', compute='_compute_waste_cig', store=True)

    line_ids = fields.One2many('packing.operation.line', 'operation_id', string="Material Usage", copy=True)

    @api.constrains('mo_id')
    def _check_mo_id_done(self):
        for rec in self:
            if rec.mo_id and rec.mo_id.state != 'done':
                raise ValidationError("Only a Manufacturing Order in the 'Done' state can be selected!")

    @api.depends('actual_production_mc')
    def _compute_actual_production_pack(self):
        for rec in self:
            rec.actual_production_pack = int(rec.actual_production_mc * 1000) if rec.actual_production_mc else 0

    @api.depends('waste_kg')
    def _compute_waste_cig(self):
        for rec in self:
            rec.waste_cig = int(rec.waste_kg / 0.00095) if rec.waste_kg else 0

    @api.model
    def create(self, vals):
        if not vals.get('operation_ref') or vals['operation_ref'] == '/':
            vals['operation_ref'] = self.env['ir.sequence'].next_by_code('packing.operation') or '/'
        # If line_ids are not present (user did not manually fill), auto-generate them from MO and sub BOM
        if not vals.get('line_ids') and vals.get('mo_id'):
            mo = self.env['mrp.production'].browse(vals['mo_id'])
            if mo and mo.bom_id:
                sub_bom = getattr(mo.bom_id, 'sub_bom_id', False)
                lines = []
                for move in mo.move_raw_ids:
                    qty_mc = 0.0
                    special_calc = False
                    if sub_bom:
                        sub_line = sub_bom.line_ids.filtered(lambda l: l.material.id == move.product_id.id)
                        if sub_line:
                            qty_mc = float(sub_line[0].qty_per_cig or 0.0)
                            special_calc = sub_line[0].special_calc
                    lines.append((0, 0, {
                        'item_code': move.product_id.default_code,
                        'material_id': move.product_id.id,
                        'unit_id': move.product_uom.id,
                        'qty_mc': qty_mc,
                        'special_calc': special_calc,
                    }))
                vals['line_ids'] = lines
        return super().create(vals)

class PackingOperationLine(models.Model):
    _name = 'packing.operation.line'
    _description = 'Packing Operation Line'

    operation_id = fields.Many2one('packing.operation', string="Operation", required=True, ondelete='cascade')
    item_code = fields.Char(string="Item Code")
    material_id = fields.Many2one('product.product', string="Material", required=True)
    unit_id = fields.Many2one('uom.uom', string="Unit", required=True)
    qty_mc = fields.Float(string='Qty /MC', required=True, digits=(12, 6), default=0.0)

    special_calc = fields.Boolean(string="Use Special Calculation", default=False)
    standard_usage = fields.Float(string='Standard Usage', compute='_compute_usage', store=True)
    actual_usage = fields.Float(string='Actual Usage', compute='_compute_usage', store=True)
    difference = fields.Float(string='Difference', compute='_compute_usage', store=True)

    actual_production_pack = fields.Integer(related='operation_id.actual_production_pack', store=True, readonly=True)
    waste_cig = fields.Integer(related='operation_id.waste_cig', store=True, readonly=True)
    shell_wast = fields.Float(related='operation_id.shell_wast', store=True, readonly=True)
    slide_wast = fields.Float(related='operation_id.slide_wast', store=True, readonly=True)
    alum_foil_wast = fields.Float(related='operation_id.alum_foil_wast', store=True, readonly=True)

    @api.depends('actual_production_pack', 'qty_mc', 'waste_cig', 'shell_wast', 'slide_wast', 'alum_foil_wast',
                 'special_calc')
    def _compute_usage(self):
        for rec in self:
            rec.standard_usage = (rec.actual_production_pack or 0) * (rec.qty_mc or 0)

            # If special_calc, use special formula
            if rec.special_calc:
                rec.actual_usage = (rec.waste_cig or 0) + (rec.standard_usage or 0)
            elif rec.shell_wast:
                rec.actual_usage = (rec.standard_usage or 0) + (rec.shell_wast or 0) / 0.0025
            # If slide_wast has a value
            elif rec.slide_wast:
                rec.actual_usage = (rec.standard_usage or 0) + (rec.slide_wast or 0) / 0.002
            # If alum_foil_wast has a value
            elif rec.alum_foil_wast:
                rec.actual_usage = (rec.standard_usage or 0) + (rec.alum_foil_wast or 0) / 0.04
            # Default calculation (no special or waste fields set)
            else:
                rec.actual_usage = (rec.waste_cig or 0) * (rec.qty_mc or 0) + (rec.standard_usage or 0)

            rec.difference = (rec.actual_usage or 0) - (rec.standard_usage or 0)
