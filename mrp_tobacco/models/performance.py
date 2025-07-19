from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MakerPerformance(models.Model):
    _name = 'maker.performance'
    _description = 'Maker Performance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True)
    date = fields.Date('Date', default=fields.Date.today(), required=True)
    making_operation_id = fields.Many2one(
        'making.operation',
        string='Operation'
    )

    # Direct input fields (no longer related to making_operation)
    actual_production_trays = fields.Float(
        'Actual Production (Trays)',
        help="Actual production in trays (1 tray = 4300 cigarettes)"
    )
    waste_cig_kg = fields.Float('Waste Cigarettes (Kg)')
    dust_kg = fields.Float('Dust (Kg)')
    winnows_kg = fields.Float('Winnows (Kg)')

    # Computed fields based on inputs
    actual_production_cig = fields.Float(
        'Actual Production (Cig)',
        compute='_compute_actual_cig',
        store=True
    )
    waste_cigarettes = fields.Float(
        'Waste Cigarettes (Cig)',
        compute='_compute_waste_cig',
        store=True
    )

    # Time tracking
    shift_start = fields.Float('Shift Start (Hours)', default=7.5)
    shift_end = fields.Float('Shift End (Hours)', default=17.5)
    planned_time = fields.Float('Planned Time (Hours)', compute='_compute_planned_time')
    available_time_min = fields.Float('Available Time (Min)', compute='_compute_available_time')
    machine_cleaning = fields.Float('Machine Cleaning (Min)', default=20)
    meal_break = fields.Float('Meal Break (Min)', default=30)
    pray_break = fields.Float('Pray Break (Min)', default=15)
    downtime = fields.Float('Downtime (Min)', compute='_compute_downtime')

    # Production metrics
    machine_speed = fields.Float('Machine Speed (Cig/Min)', default=2000)
    standard_production = fields.Float('Standard Production', compute='_compute_standard_production')
    available_production = fields.Float('Available Production', compute='_compute_available_production')
    actual_running_time = fields.Float('Actual Running Time (Min)', compute='_compute_actual_running_time')

    # Related fields from MO
    product_id = fields.Many2one('product.product', string='Product', related='production_id.product_id', store=True)
    product_qty = fields.Float('Planned Qty', related='production_id.product_qty', store=True)
    qty_produced = fields.Float('Produced Qty', related='production_id.qty_produced', store=True)
    scrap_qty = fields.Float('Scrapped Qty', compute='_compute_scrap_qty', store=True)

    # OEE Calculations
    availability = fields.Float('Availability', compute='_compute_oee', store=True)
    performance = fields.Float('Performance', compute='_compute_oee', store=True)
    quality = fields.Float('Quality', compute='_compute_oee', store=True)
    oee = fields.Float('OEE', compute='_compute_oee', store=True)

    @api.onchange('making_operation_id')
    def _onchange_making_operation(self):
        for rec in self:
            op = rec.making_operation_id
            if op:
                rec.actual_production_trays = op.actual_production_trays
                rec.actual_production_cig = op.actual_production_cig
                rec.waste_cigarettes = op.waste_cig
                rec.waste_cig_kg = op.waste_kg
                rec.dust_kg = op.dust_kg
                rec.winnows_kg = op.winnows_kg

    @api.constrains('actual_production_trays')
    def _check_production_trays(self):
        for record in self:
            if record.actual_production_trays < 0:
                raise ValidationError("Actual production cannot be negative")
            if record.qty_produced > 0 and record.actual_production_trays > record.qty_produced:
                raise ValidationError(
                    f"Actual production ({record.actual_production_trays} trays) cannot exceed "
                    f"MO produced quantity ({record.qty_produced})"
                )

    @api.depends('actual_production_trays')
    def _compute_actual_cig(self):
        for record in self:
            record.actual_production_cig = record.actual_production_trays * 4300  # 1 tray = 4300 cigarettes

    @api.depends('waste_cig_kg')
    def _compute_waste_cig(self):
        for record in self:
            record.waste_cigarettes = record.waste_cig_kg / 0.00095  # Convert kg to cigarettes

    @api.depends('production_id.scrap_ids')
    def _compute_scrap_qty(self):
        for record in self:
            record.scrap_qty = sum(record.production_id.scrap_ids.filtered(
                lambda s: s.product_id == record.product_id
            ).mapped('scrap_qty'))

    @api.depends('shift_start', 'shift_end')
    def _compute_planned_time(self):
        for record in self:
            record.planned_time = (record.shift_end - record.shift_start) * 60  # in minutes

    @api.depends('planned_time', 'machine_cleaning', 'meal_break', 'pray_break')
    def _compute_available_time(self):
        for record in self:
            record.available_time_min = record.planned_time - record.machine_cleaning - record.meal_break - record.pray_break

    @api.depends('available_time_min')
    def _compute_downtime(self):
        for record in self:
            record.downtime = record.available_time_min - record.actual_running_time

    @api.depends('machine_speed', 'planned_time')
    def _compute_standard_production(self):
        for record in self:
            record.standard_production = record.machine_speed * record.planned_time

    @api.depends('machine_speed', 'available_time_min')
    def _compute_available_production(self):
        for record in self:
            record.available_production = record.machine_speed * record.available_time_min

    @api.depends('actual_production_cig', 'machine_speed')
    def _compute_actual_running_time(self):
        for record in self:
            if record.machine_speed:
                record.actual_running_time = record.actual_production_cig / record.machine_speed
            else:
                record.actual_running_time = 0

    @api.depends('actual_running_time', 'available_time_min', 'planned_time', 'qty_produced', 'scrap_qty')
    def _compute_oee(self):
        for record in self:
            # Availability
            if record.available_time_min:
                record.availability = record.actual_running_time / record.available_time_min
            else:
                record.availability = 0

            # Performance
            if record.planned_time:
                record.performance = record.actual_running_time / record.planned_time
            else:
                record.performance = 0

            # Quality - use MO produced quantity minus scrap
            if record.qty_produced:
                record.quality = (record.qty_produced - record.scrap_qty) / record.qty_produced
            else:
                record.quality = 0

            # OEE
            record.oee = record.availability * record.performance * record.quality

    @api.model
    def create(self, vals):
        """Override create to ensure production_id is set"""
        if 'production_id' not in vals:
            raise ValidationError("Manufacturing Order is required for performance tracking")
        return super().create(vals)


class PackerPerformance(models.Model):
    _name = 'packer.performance'
    _description = 'Packer Performance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True)
    date = fields.Date('Date', default=fields.Date.today(), required=True)
    packing_operation_id = fields.Many2one(
        'packing.operation',
        string='Operation'
    )

    # Direct input fields
    actual_production_mc = fields.Float('Actual Production (MC)')
    actual_production_cig = fields.Float('Actual Production Cig')
    waste_cig_kg = fields.Float('Waste Cigarettes (Kg)')
    shell_waste_kg = fields.Float('Shell Waste (Kg)')
    slides_waste_kg = fields.Float('Slides Waste (Kg)')
    aluminium_foil_waste_kg = fields.Float('Aluminium Foil Waste (Kg)')

    # Computed fields
    actual_production_packets = fields.Float(
        'Actual Production (Packets)',
        compute='_compute_actual_packets',
        store=True
    )
    waste_cigarettes = fields.Float(
        'Waste Cigarettes (Cig)',
        compute='_compute_waste_cig',
        store=True
    )

    # Time tracking
    shift_start = fields.Float('Shift Start (Hours)', default=7.5)
    shift_end = fields.Float('Shift End (Hours)', default=15.5)
    planned_time = fields.Float(
        'Planned Time (Hours)',
        compute='_compute_planned_time',
        store=True
    )
    available_time_min = fields.Float('Available Time (Min)', compute='_compute_available_time')
    machine_cleaning = fields.Float('Machine Cleaning (Min)', default=20)
    meal_break = fields.Float('Meal Break (Min)', default=30)
    pray_break = fields.Float('Pray Break (Min)', default=15)
    downtime = fields.Float('Downtime (Min)', compute='_compute_downtime')

    # Production metrics
    machine_speed = fields.Float('Machine Speed (Pkts/Min)', default=180)
    standard_production = fields.Float('Standard Production', compute='_compute_standard_production')
    available_production = fields.Float('Available Production', compute='_compute_available_production')
    actual_running_time = fields.Float('Actual Running Time (Min)', compute='_compute_actual_running_time')

    # Related fields from MO
    product_id = fields.Many2one('product.product', string='Product', related='production_id.product_id', store=True)
    product_qty = fields.Float('Planned Qty', related='production_id.product_qty', store=True)
    qty_produced = fields.Float('Produced Qty', related='production_id.qty_produced', store=True)
    scrap_qty = fields.Float('Scrapped Qty', compute='_compute_scrap_qty', store=True)

    # OEE Calculations
    availability = fields.Float('Availability', compute='_compute_oee', store=True)
    performance = fields.Float('Performance', compute='_compute_oee', store=True)
    quality = fields.Float('Quality', compute='_compute_oee', store=True)
    oee = fields.Float('OEE', compute='_compute_oee', store=True)

    @api.onchange('packing_operation_id')
    def _onchange_packing_operation(self):
        for rec in self:
            op = rec.packing_operation_id
            if op:
                rec.actual_production_mc = op.actual_production_mc
                rec.actual_production_cig = op.actual_production_pack
                rec.waste_cig_kg = op.waste_kg
                rec.waste_cigarettes = op.waste_cig
                rec.shell_waste_kg = op.shell_wast
                rec.slides_waste_kg = op.slide_wast
                rec.aluminium_foil_waste_kg = op.alum_foil_wast

    @api.constrains('actual_production_mc')
    def _check_production_mc(self):
        for record in self:
            if record.actual_production_mc < 0:
                raise ValidationError("Actual production cannot be negative")
            if record.qty_produced > 0 and record.actual_production_mc > record.qty_produced:
                raise ValidationError(
                    f"Actual production ({record.actual_production_mc} MC) cannot exceed "
                    f"MO produced quantity ({record.qty_produced})"
                )

    @api.depends('actual_production_mc')
    def _compute_actual_packets(self):
        for record in self:
            record.actual_production_packets = record.actual_production_mc * 1000  # 1 MC = 1000 packets

    @api.depends('waste_cig_kg')
    def _compute_waste_cig(self):
        for record in self:
            record.waste_cigarettes = record.waste_cig_kg / 0.00095  # Convert kg to cigarettes

    @api.depends('shift_start', 'shift_end')
    def _compute_planned_time(self):
        for rec in self:
            rec.planned_time = (rec.shift_end or 0.0) - (rec.shift_start or 0.0) * 24

    @api.depends('planned_time', 'machine_cleaning', 'machine_cleaning', 'meal_break', 'pray_break')
    def _compute_available_time(self):
        for rec in self:
            rec.available_time_min = (rec.planned_time or 0.0) - (rec.machine_cleaning or 0.0) - (rec.meal_break or 0.0) - (rec.pray_break or 0.0)

    @api.depends('available_time_min', 'actual_running_time')
    def _compute_downtime(self):
        for rec in self:
            rec.downtime = (rec.available_time_min or 0.0) - (rec.actual_running_time or 0.0)

    @api.depends('actual_production_cig', 'machine_speed')
    def _compute_actual_running_time(self):
        for rec in self:
            rec.actual_running_time = (rec.actual_production_cig or 0.0) / (rec.machine_speed or 0.0)

    @api.depends('machine_speed', 'planned_time')
    def _compute_standard_production(self):
        for rec in self:
            rec.standard_production = (rec.machine_speed or 0.0) * (rec.planned_time or 0.0)

    @api.depends('available_time_min', 'machine_speed')
    def _compute_available_production(self):
        for rec in self:
            rec.available_production = (rec.available_time_min or 0.0) * (rec.machine_speed or 0.0)