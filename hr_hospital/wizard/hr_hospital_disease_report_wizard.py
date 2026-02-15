from odoo import models, fields


class HrHospitalDiseaseReportWizard(models.TransientModel):
    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Disease Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctors',
        string='Doctors',
    )
    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.diseases',
        string='Diseases',
    )
    country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Countries',
    )
    date_start = fields.Date(
        string='Date Start',
    )
    date_end = fields.Date(
        string='Date End',
    )
    report_type = fields.Selection(
        selection=[
            ('short', 'Short'),
            ('full', 'Full'),
        ],
        string='Report Type',
        default='short',
        required=True,
    )
    group_by = fields.Selection(
        selection=[
            ('doctor', 'Doctor'),
            ('disease', 'Disease'),
            ('month', 'Month'),
            ('country', 'Country'),
        ],
        string='Group By',
        required=True,
    )

    def action_generate(self):
        domain = []
        if self.doctor_ids:
            domain.append(('visit_id.doctor_id', 'in', self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))
        if self.country_ids:
            domain.append(('visit_id.patient_id.country_id', 'in', self.country_ids.ids))
        if self.date_start:
            domain.append(('approval_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('approval_date', '<=', self.date_end))

        group_by_map = {
            'doctor': 'visit_id.doctor_id',
            'disease': 'disease_id',
            'month': 'approval_date:month',
            'country': 'visit_id.patient_id.country_id',
        }
        groupby = group_by_map.get(self.group_by)
        if self.report_type == 'short':
            return self._action_generate_short(domain, groupby)

        context = dict(self.env.context)
        if groupby:
            context['group_by'] = groupby

        return {
            'type': 'ir.actions.act_window',
            'name': 'Disease Report',
            'res_model': 'hr.hospital.medical.diagnosis',
            'view_mode': 'list,form',
            'domain': domain,
            'context': context,
            'target': 'current',
        }

    def _action_generate_short(self, domain, groupby):
        diagnosis_model = self.env['hr.hospital.medical.diagnosis']
        groups = diagnosis_model.read_group(
            domain,
            ['id'],
            [groupby] if groupby else [],
            lazy=False
        )
        if not groupby:
            total = groups[0].get('__count', 0) if groups else 0
            message = str(total)
        else:
            parts = []
            for group in groups:
                group_label = self._format_group_label(groupby, group)
                parts.append(f"{group_label}: {group.get('__count', 0)}")
            message = "\n".join(parts) if parts else "0"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Disease Report (Short)',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def _format_group_label(self, groupby, group):
        value = group.get(groupby)
        if isinstance(value, tuple):
            return value[1] or 'Undefined'
        return value or 'Undefined'
