"""HR Hospital module."""

from odoo import models, fields


class HrHospitalDoctorReport(models.AbstractModel):
    _name = 'report.hr_hospital.report_doctor'
    _description = 'Doctor Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.hospital.doctors'].browse(docids)
        report_data = {}

        for doc in docs:
            visits = self.env['hr.hospital.visits'].search([
                ('doctor_id', '=', doc.id),
                ('active', '=', True),
            ], order='plan_datetime desc')

            patient_ids = visits.mapped('patient_id').ids
            patients_with_status = []
            for pid in patient_ids:
                patient = self.env['hr.hospital.patients'].browse(pid)
                latest_visit = self.env['hr.hospital.visits'].search([
                    ('doctor_id', '=', doc.id),
                    ('patient_id', '=', pid),
                    ('active', '=', True),
                ], order='plan_datetime desc', limit=1)
                status = latest_visit.status if latest_visit else ''
                patients_with_status.append((patient, status))

            report_data[doc.id] = {
                'visit_history': visits,
                'patients_with_status': patients_with_status,
            }

        return {
            'docs': docs,
            'report_data': report_data,
        }
