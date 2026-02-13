from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class HrHospitalVisits(models.Model):
    _name = 'hr.hospital.visits'
    _description = 'Hospital Visits'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()

    doctor_id = fields.Many2one('hr.hospital.doctors', string='Doctor', required=True)
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patients',
        string='Patient',
        required=True,
        ondelete='restrict',
    )
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
        required=True,
    )

    fact_datetime = fields.Datetime(
        string='Actual Visit Date & Time',
        readonly=True,
        states={'completed': [('readonly', False)]},
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

    diagnoses_count = fields.Integer(
        compute='_compute_diagnoses_count',
        store=True,
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

    def write(self, vals):
        for rec in self:
            if rec.fact_datetime:
                if 'doctor_id' in vals or 'plan_datetime' in vals:
                    raise ValidationError(
                        'You cannot modify doctor or planned datetime. Visit is completed.'
                    )
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.diagnosis_ids:
                raise UserError('Cannot delete visit with diagnoses!')
        return super().unlink()

    @api.depends('diagnosis_ids')
    def _compute_diagnoses_count(self):
        for record in self:
            record.diagnoses_count = len(record.diagnosis_ids)

    @api.constrains('doctor_id', 'patient_id', 'plan_datetime')
    def _check_up_visit(self):
        for record in self:
            if record.doctor_id and record.patient_id and record.plan_datetime:
                visit_date = record.plan_datetime.date()

                day_start = fields.Datetime.to_string(
                    fields.Datetime.from_string(f'{visit_date} 00:00:00')
                )
                day_end = fields.Datetime.to_string(
                    fields.Datetime.from_string(f'{visit_date} 23:59:59')
                )

                domain = [
                    ('doctor_id', '=', record.doctor_id.id),
                    ('patient_id', '=', record.patient_id.id),
                    ('id', '!=', record.id),
                    ('plan_datetime', '>=', day_start),
                    ('plan_datetime', '<=', day_end)
                ]

                if self.search_count(domain) > 0:
                    raise ValidationError(
                        'Patient %s already has a visit with Doctor %s on %s!' % (
                            record.patient_id.name,
                            record.doctor_id.name,
                            visit_date
                        )
                    )

                history = self.env['hr.hospital.patient.doctor.history'].search([
                    ('patient_id', '=', record.patient_id.id),
                    ('doctor_id', '=', record.doctor_id.id),
                    ('assignment_date', '<=', visit_date)
                ], limit=1, order='assignment_date desc')

                if not history:
                    raise ValidationError(
                        'Cannot create visit: Doctor %s was not assigned to Patient %s '
                        'before %s!' % (
                            record.doctor_id.name,
                            record.patient_id.name,
                            visit_date
                        )
                    )
