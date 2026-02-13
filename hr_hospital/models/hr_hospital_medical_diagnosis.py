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

    def _get_current_doctor(self):
        return self.env['hr.hospital.doctors'].search(
            [('user_id', '=', self.env.user.id)],
            limit=1
        )

    @api.model_create_multi
    def create(self, vals_list):
        doctor = self._get_current_doctor()
        now = fields.Datetime.now()
        for vals in vals_list:
            if vals.get('is_approved'):
                if doctor:
                    vals['approved_by_doctor_id'] = doctor.id
                vals['approval_date'] = now
        return super().create(vals_list)

    def write(self, vals):
        doctor = self._get_current_doctor()
        now = fields.Datetime.now()
        for rec in self:
            rec_vals = vals
            if vals.get('is_approved') and not rec.is_approved:
                rec_vals = dict(vals)
                if doctor:
                    rec_vals['approved_by_doctor_id'] = doctor.id
                rec_vals['approval_date'] = now
            elif vals.get('approved_by_doctor_id') and not rec.is_approved:
                rec_vals = dict(vals)
                rec_vals['is_approved'] = True
                rec_vals['approval_date'] = now
            super(MedicalDiagnosis, rec).write(rec_vals)
        return True


