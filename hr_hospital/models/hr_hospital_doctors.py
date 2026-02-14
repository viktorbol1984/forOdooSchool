from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Doctors(models.Model):
    _name = 'hr.hospital.doctors'
    _description = 'Doctors'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
    )

    speciality_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.speciality',
        string='Speciality'
    )

    is_intern = fields.Boolean()

    mentor_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Mentor',
        domain=[('is_intern', '=', False)]
    )

    license_number = fields.Char(
        required=True,
        copy=False
    )
    # old fashioned way didn't work
    _license_number_unique = models.Constraint(
        'unique (license_number)',
        'License number must be unique!'
    )

    license_issue_date = fields.Date()

    years_of_experience = fields.Integer(
        compute='_compute_years_of_experience',
    )

    rating = fields.Float(
        digits=(3, 2),
    )

    schedule_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.schedule',
        inverse_name='doctor_id',
        string='Work Schedule'
    )

    education_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Education Country'
    )

    description = fields.Text()

    @api.depends('license_issue_date')
    def _compute_years_of_experience(self):
        today = fields.Date.today()
        for record in self:
            if record.license_issue_date:
                delta = today - record.license_issue_date
                record.years_of_experience = delta.days/365
            else:
                record.years_of_experience = 0

    @api.constrains('active')
    def _check_visits(self):
        for record in self:
            if not record.active:
                active_visits = self.env['hr.hospital.visits'].search([
                    ('doctor_id', '=', record.id),
                    ('active', '=', True)
                ])
                if active_visits:
                    raise ValidationError('Cannot archive doctor with active visits!')

    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if record.rating and (record.rating < 0.0 or record.rating > 5.0):
                raise ValidationError('Rating must be between 0.00 and 5.00')

    @api.onchange('is_intern')
    def _onchange_is_intern(self):
        if not self.is_intern:
            self.mentor_doctor_id = False

    @api.constrains('is_intern', 'mentor_doctor_id')
    def _check_mentor_only_for_interns(self):
        for record in self:
            if not record.is_intern and record.mentor_doctor_id:
                raise ValidationError('Only interns can have a mentor doctor!')
            if record.mentor_doctor_id == record:
                raise ValidationError('Doctor cannot be their own mentor!')

    @api.depends('name', 'speciality_id', 'speciality_id.name')
    def _compute_display_name(self):
        for record in self:
            name = record.name or ''
            if record.speciality_id and record.speciality_id.name:
                name = f"{name} ({record.speciality_id.name})"
            record.display_name = name
