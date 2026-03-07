from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestHrHospitalVisits(TransactionCase):
    def test_cannot_be_deleted_with_diagnosis(self):
        country = self.env["res.country"].create({"name": "Visitland", "code": "VL"})
        speciality = self.env["hr.hospital.doctor.speciality"].create(
            {"name": "Cardiologist", "code": "CRD"}
        )
        doctor = self.env["hr.hospital.doctors"].create(
            {
                "name": "Visit Doctor",
                "license_number": "LIC-DEL-VISIT",
                "country_id": country.id,
                "speciality_id": speciality.id,
            }
        )
        patient = self.env["hr.hospital.patients"].create(
            {
                "name": "Visit Patient",
                "birth_date": fields.Date.today() - relativedelta(years=25),
                "country_id": country.id,
            }
        )
        plan_datetime = fields.Datetime.now() + relativedelta(days=6)
        plan_date = fields.Date.to_date(plan_datetime)
        self.env["hr.hospital.doctor.schedule"].create(
            {
                "doctor_id": doctor.id,
                "date": plan_date,
                "schedule_type": "working_day",
                "start_time": 9.0,
                "end_time": 18.0,
            }
        )
        self.env["hr.hospital.patient.doctor.history"].create(
            {
                "patient_id": patient.id,
                "doctor_id": doctor.id,
                "assignment_date": plan_date - relativedelta(days=1),
            }
        )
        visit = self.env["hr.hospital.visits"].create(
            {
                "doctor_id": doctor.id,
                "patient_id": patient.id,
                "plan_datetime": plan_datetime,
            }
        )
        self.env["hr.hospital.medical.diagnosis"].create({"visit_id": visit.id})

        with self.assertRaises(UserError):
            visit.unlink()
