from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Patients(models.Model):
    _name = 'hr.hospital.patients'
    _description = 'Patients'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    passport = fields.Char(size=10)

    contact = fields.Many2one('hr.hospital.contact.person')

    bloodGroup = fields.Selection(
        selection=[
            ('o_positive', 'O(I) Rh+'),
            ('o_negative', 'O(I) Rh-'),
            ('a_positive', 'A(II) Rh+'),
            ('a_negative', 'A(II) Rh-'),
            ('b_positive', 'B(III) Rh+'),
            ('b_negative', 'B(III) Rh-'),
            ('ab_positive', 'AB(IV) Rh+'),
            ('ab_negative', 'AB(IV) Rh-'),
        ],
    )

    allergies = fields.Text()

    insurance = fields.Many2one(comodel_name='res.partner', domain=[('is_company', '=', True)], )

    insurancePolicy = fields.Char(string='Insurance Policy')

    doctors_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_id',
        string='Doctors History'
    )
    active = fields.Boolean(
        default=True
    )

    primaryDoctor_id = fields.Many2one('hr.hospital.doctors', string='Primary Care Doctor')

    description = fields.Text()

    def write(self, vals):
        for rec in self:
            if 'primaryDoctor_id' in vals:
                new_doctor_id = vals.get('primaryDoctor_id')
                if rec.primaryDoctor_id.id != new_doctor_id:
                    self.env[
                        'hr.hospital.patient.doctor.history'
                    ].create({
                        'patient_id': rec.id,
                        'doctor_id': new_doctor_id,
                        'assignment_date': fields.Date.today(),
                        'change_date': fields.Date.today(),

                    })

        return super().write(vals)

    @api.constrains('birth_date')
    def _check_up_patient(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                age_days = (today - record.birth_date).days
                age_years = age_days // 365
                if age_years == 0:
                    raise ValidationError('Patient age is 0')
            else:
                raise ValidationError('Birth date is empty')
