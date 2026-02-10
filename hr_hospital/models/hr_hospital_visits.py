from odoo import models, fields

class HrHospitalVisits(models.Model):
    _name = 'hr.hospital.visits'
    _description = 'Hospital Visits'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()

    doctor_id = fields.Many2one('hr.hospital.doctors', string='Doctor', required=True)
    patient_id = fields.Many2one('hr.hospital.patients', string='Patient', required=True)
    disease_id = fields.Many2one('hr.hospital.diseases', string='Disease')

    status = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='scheduled',
    )

    plan_datetime = fields.Datetime(
        string='Planned Date & Time',
    )

    fact_datetime = fields.Datetime(
        string='Actual Visit Date & Time',
        readonly=True,
        states={'completed': [('readonly', False)]},
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patients',
        string='Patient',
        required=True,
        ondelete='restrict',
    )

    visit_type = fields.Selection(
        selection=[
            ('primary', 'Primary'),
            ('follow_up', 'Follow-up'),
            ('preventive', 'Preventive'),
            ('emergency', 'Emergency'),
        ],
    )

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.medical.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses',
    )

    recommendations = fields.Html()

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    visit_cost = fields.Monetary(
        currency_field='currency_id',
    )