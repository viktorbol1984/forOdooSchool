"""HR Hospital module."""

from odoo import models, fields, api


class HrHospitalDiagnosisReportWizard(models.TransientModel):
    _name = 'hr.hospital.diagnosis.report.wizard'
    _description = 'Diagnosis Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctors',
        string='Doctors',
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.diseases',
        string='Diseasis',
    )

    date_from = fields.Date()

    date_to = fields.Date()

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids') or []
        if not active_ids and self.env.context.get('active_id'):
            active_ids = [self.env.context['active_id']]
        if active_ids and 'doctor_ids' in fields_list:
            values['doctor_ids'] = [(6, 0, active_ids)]
        return values

    def action_generate(self):
        self.ensure_one()

        domain = []
        if self.doctor_ids:
            domain.append(('visit_id.doctor_id', 'in', self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))
        if self.date_from:
            domain.append(('approval_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('approval_date', '<=', self.date_to))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Diagnosis Report',
            'res_model': 'hr.hospital.medical.diagnosis',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'group_by': 'disease_id',
            },
            'target': 'current',
        }
