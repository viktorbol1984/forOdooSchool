from odoo import models, fields, api

class MedicalDiagnosis(models.Model):
    _name = 'hr.hospital.medical.diagnosis'
    _description = 'Medical Diagnosis'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visits',
        string='Visit',
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.diseases',
        string='Disease',
    )

    diagnos_description = fields.Text(
        string='Diagnos'
    )

    prescribed_treatment = fields.Html(
        string='Prescribed Treatment'
    )

    is_approved = fields.Boolean(
        string='Approved',
        default=False,
        copy=False
    )

    approved_by_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Doctor',
        readonly=True,
        copy=False
    )

    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False
    )

    severity = fields.Selection(
        selection=[
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
            ('critical', 'Critical')
        ],
        default='mild'
    )