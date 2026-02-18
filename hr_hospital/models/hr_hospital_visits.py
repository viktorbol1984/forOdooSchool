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

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Doctor',
        required=True,
        domain=[('license_number', '!=', False)],
    )

    mentor_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Mentor Doctor',
        compute='_compute_mentor_doctor_id',
        store=True,
    )

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

    visit_count = fields.Integer(default=1,
        readonly=True,
    )

    @api.onchange('doctor_id', 'patient_id', 'plan_datetime')
    def _onchange_plan_datetime_set_doctor_domain(self):
        domain = []
        schedule_domain = []
        if self.plan_datetime:
            plan_date = fields.Date.to_date(self.plan_datetime)
            schedules = self.env['hr.hospital.doctor.schedule'].search([
                ('date', '=', plan_date),
                ('schedule_type', '=', 'working_day'),
            ])
            schedule_domain = [('id', 'in', schedules.mapped('doctor_id').ids)]
        patient = self.patient_id
        if patient and (patient.country_id or patient.lang_id):
            country_id = patient.country_id.id if patient.country_id else False
            lang_id = patient.lang_id.id if patient.lang_id else False
            domain = [
                '|', '|',
                ('country_id', '=', country_id),
                ('education_country_id', '=', country_id),
                ('lang_id', '=', lang_id),
            ]
        if schedule_domain:
            domain = ['&'] + domain + schedule_domain if domain else schedule_domain
        return {'domain': {'doctor_id': domain}}

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

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': 'Allergy:',
                    'message': self.patient_id.allergies
                }
            }

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

    @api.constrains('doctor_id', 'patient_id', 'plan_datetime')
    def _check_doctor_availability_and_match(self):
        for record in self:
            if record.doctor_id and record.plan_datetime:
                plan_date = fields.Date.to_date(record.plan_datetime)
                schedule = self.env['hr.hospital.doctor.schedule'].search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('date', '=', plan_date),
                    ('schedule_type', '=', 'working_day'),
                ], limit=1)
                if not schedule:
                    raise ValidationError(
                        'Doctor is not available on the selected date.'
                    )
            if record.doctor_id and record.patient_id:
                patient = record.patient_id
                same_country = (
                    patient.country_id
                    and record.doctor_id.country_id == patient.country_id
                )
                education_country = (
                    patient.country_id
                    and record.doctor_id.education_country_id == patient.country_id
                )
                same_lang = (
                    patient.lang_id
                    and record.doctor_id.lang_id == patient.lang_id
                )
                if not (same_country or education_country or same_lang):
                    raise ValidationError(
                        'Doctor does not match patient country, education country, '
                        'or language.'
                    )

    @api.depends('doctor_id', 'doctor_id.is_intern', 'doctor_id.mentor_doctor_id')
    def _compute_mentor_doctor_id(self):
        for record in self:
            if record.doctor_id and record.doctor_id.is_intern:
                record.mentor_doctor_id = record.doctor_id.mentor_doctor_id
            else:
                record.mentor_doctor_id = False
