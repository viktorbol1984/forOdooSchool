from odoo import models, fields

class Doctors(models.Model):
    _name = 'hr.hospital.doctors'
    _description = 'Doctors'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()