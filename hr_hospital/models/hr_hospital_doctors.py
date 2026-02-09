from odoo import models, fields

class Doctors(models.Model):
    _name = 'hr.hospital.doctors'
    _description = 'Doctors'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    speciality_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.speciality',
        string='Speciality'
    )

    description = fields.Text()