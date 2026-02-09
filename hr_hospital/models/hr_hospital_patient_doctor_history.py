from odoo import models, fields


class PatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor History'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patients',
        string='Patient',
        required=True,
        ondelete='cascade'
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Doctor',
        required=True,
    )

    assignment_date = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today
    )

    change_date = fields.Date()

    change_reason = fields.Text()

    active = fields.Boolean(
        default=True
    )