from odoo import models, fields

class HrHospitalVisits(models.Model):
    _name = 'hr.hospital.visits'
    _description = 'Hospital Visits'

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()

    doctor_id = fields.Many2one('hr.hospital.doctors', string='Doctor')
    patient_id = fields.Many2one('hr.hospital.patients', string='Patient')
    disease_id = fields.Many2one('hr.hospital.diseases', string='Disease')