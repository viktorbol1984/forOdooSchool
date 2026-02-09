from odoo import models, fields

class Patients(models.Model):
    _name = 'hr.hospital.patients'
    _description = 'Patients'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    primaryDoctor_id = fields.Many2one('hr.hospital.doctors', string='Primary Care Doctor')

    description = fields.Text()