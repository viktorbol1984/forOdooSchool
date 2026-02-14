import base64
import csv
import io
import json
from datetime import datetime, time

from odoo import models, fields, api

class PatientCardExportWizard(models.TransientModel):
    _name = 'hr.hospital.patient.card.export.wizard'
    _description = 'Patient Card Export Wizard'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patients',
        string='Patient',
        required=True,
    )
    date_start = fields.Date(
        string='Date Start',
    )
    date_end = fields.Date(
        string='Date End',
    )
    include_diagnoses = fields.Boolean(
        string='Include Diagnoses',
        default=True,
    )
    include_recommendations = fields.Boolean(
        string='Include Recommendations',
        default=True,
    )
    report_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Report Language',
        default=lambda self: self.patient_id.lang_id.id,
    )
    export_format = fields.Selection(
        selection=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
        ],
        required=True,
    )

    file_data = fields.Binary(
        string='File',
        readonly=True,
    )
    file_name = fields.Char(
        string='File Name',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PatientCardExportWizard, self).default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'hr.hospital.patients' and active_ids:
            res['patient_id'] = active_ids[0]
        return res

    def action_export(self):
        self.ensure_one()
        patient = self.patient_id

        visit_domain = [('patient_id', '=', patient.id)]
        if self.date_start:
            visit_domain.append((
                'plan_datetime',
                '>=',
                fields.Datetime.to_string(datetime.combine(self.date_start, time.min)),
            ))
        if self.date_end:
            visit_domain.append((
                'plan_datetime',
                '<=',
                fields.Datetime.to_string(datetime.combine(self.date_end, time.max)),
            ))
        visits = self.env['hr.hospital.visits'].search(visit_domain)

        diagnoses = self.env['hr.hospital.medical.diagnosis']
        if self.include_diagnoses:
            diag_domain = [('visit_id.patient_id', '=', patient.id)]
            if self.date_start:
                diag_domain.append((
                    'visit_id.plan_datetime',
                    '>=',
                    fields.Datetime.to_string(datetime.combine(self.date_start, time.min)),
                ))
            if self.date_end:
                diag_domain.append((
                    'visit_id.plan_datetime',
                    '<=',
                    fields.Datetime.to_string(datetime.combine(self.date_end, time.max)),
                ))
            diagnoses = self.env['hr.hospital.medical.diagnosis'].search(diag_domain)

        if self.export_format == 'json':
            content = self._export_json(patient, visits, diagnoses)
            filename = f"patient_card_{patient.id}.json"
        else:
            content = self._export_csv(patient, visits, diagnoses)
            filename = f"patient_card_{patient.id}.csv"

        self.write({
            'file_data': base64.b64encode(content),
            'file_name': filename,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': (
                f"/web/content/?model={self._name}&id={self.id}"
                f"&field=file_data&filename_field=file_name&download=true"
            ),
            'target': 'self',
        }

    def _export_json(self, patient, visits, diagnoses):
        data = {
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'full_name': patient.full_name,
                'birth_date': patient.birth_date and patient.birth_date.isoformat(),
                'phone': patient.phone,
                'email': patient.email,
                'country': self._safe_name(patient.country_id),
                'primary_doctor': self._safe_name(patient.primaryDoctor_id),
            },
            'visits': [],
            'diagnoses': [],
        }
        if self.include_recommendations:
            for visit in visits:
                data['visits'].append({
                    'id': visit.id,
                    'date': visit.plan_datetime and visit.plan_datetime.isoformat(),
                    'doctor': self._safe_name(visit.doctor_id),
                    'disease': self._safe_name(visit.disease_id),
                    'recommendations': visit.recommendations,
                })
        if self.include_diagnoses:
            for diag in diagnoses:
                data['diagnoses'].append({
                    'id': diag.id,
                    'visit_id': diag.visit_id.id if diag.visit_id else False,
                    'disease': self._safe_name(diag.disease_id),
                    'description': diag.diagnos_description,
                    'severity': diag.severity,
                    'approved': diag.is_approved,
                    'approved_by': self._safe_name(diag.approved_by_doctor_id),
                    'approval_date': diag.approval_date and diag.approval_date.isoformat(),
                })
        return json.dumps(data, ensure_ascii=True, indent=2).encode('utf-8')

    def _export_csv(self, patient, visits, diagnoses):
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            'patient_id',
            'patient_name',
            'patient_full_name',
            'birth_date',
            'phone',
            'email',
            'country',
            'primary_doctor',
            'visit_id',
            'visit_date',
            'visit_doctor',
            'visit_disease',
            'visit_recommendations',
            'diagnosis_id',
            'diagnosis_disease',
            'diagnosis_description',
            'diagnosis_severity',
            'diagnosis_approved',
            'diagnosis_approved_by',
            'diagnosis_approval_date',
        ]
        writer.writerow(headers)

        base = [
            patient.id,
            patient.name or '',
            patient.full_name or '',
            patient.birth_date.isoformat() if patient.birth_date else '',
            patient.phone or '',
            patient.email or '',
            patient.country_id.name if patient.country_id else '',
            patient.primaryDoctor_id.display_name if patient.primaryDoctor_id else '',
        ]

        diag_list = diagnoses if self.include_diagnoses else self.env['hr.hospital.medical.diagnosis']
        if diag_list:
            for diag in diag_list:
                visit = diag.visit_id
                writer.writerow(base + [
                    visit.id if visit else '',
                    visit.plan_datetime.isoformat() if visit and visit.plan_datetime else '',
                    visit.doctor_id.display_name if visit and visit.doctor_id else '',
                    visit.disease_id.name if visit and visit.disease_id else '',
                    visit.recommendations if (visit and self.include_recommendations) else '',
                    diag.id,
                    diag.disease_id.name if diag.disease_id else '',
                    diag.diagnos_description or '',
                    diag.severity or '',
                    '1' if diag.is_approved else '0',
                    diag.approved_by_doctor_id.display_name if diag.approved_by_doctor_id else '',
                    diag.approval_date.isoformat() if diag.approval_date else '',
                ])
        else:
            writer.writerow(base + [''] * (len(headers) - len(base)))

        return output.getvalue().encode('utf-8')

    def _safe_name(self, record):
        if not record:
            return ''
        return record.display_name or getattr(record, 'name', '') or ''
