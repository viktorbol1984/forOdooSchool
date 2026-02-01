from odoo import models, fields

class HrHospitalVisits(models.Model):
    _name = 'hr.hospital.visits'
    _description = 'Hospital Visits'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()