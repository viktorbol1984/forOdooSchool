from odoo import models, fields

class Diseases(models.Model):
    _name = 'hr.hospital.diseases'
    _description = 'Diseases'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()