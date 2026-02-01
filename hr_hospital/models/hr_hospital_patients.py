from odoo import models, fields

class Patients(models.Model):
    _name = 'hr.hospital.patients'
    _description = 'Patients'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()