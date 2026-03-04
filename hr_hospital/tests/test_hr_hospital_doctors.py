from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestHrHospitalDoctors(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._doctor_seq = 0
        cls.country = cls.env["res.country"].create(
            {"name": "Doctorland", "code": "DL"}
        )
        cls.speciality = cls.env["hr.hospital.doctor.speciality"].create(
            {"name": "Therapist", "code": "THR"}
        )

    def _create_doctor(self, **extra_vals):
        self.__class__._doctor_seq += 1
        vals = {
            "name": "Doctor Test",
            "license_number": f"LIC-DR-{self._doctor_seq}",
            "country_id": self.country.id,
            "speciality_id": self.speciality.id,
        }
        vals.update(extra_vals)
        return self.env["hr.hospital.doctors"].create(vals)

    def _create_patient(self, **extra_vals):
        vals = {
            "name": "Patient for doctor",
            "birth_date": fields.Date.today() - relativedelta(years=30),
            "country_id": self.country.id,
        }
        vals.update(extra_vals)
        return self.env["hr.hospital.patients"].create(vals)

    def _create_visit(self, doctor, patient, plan_datetime):
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
        return self.env["hr.hospital.visits"].create(
            {
                "doctor_id": doctor.id,
                "patient_id": patient.id,
                "plan_datetime": plan_datetime,
            }
        )

    def test_years_of_experience_compute(self):
        issue_date = fields.Date.today() - relativedelta(years=2)
        doctor = self._create_doctor(license_issue_date=issue_date)
        self.assertGreater(doctor.years_of_experience, 1.9)

    def test_rating_validation(self):
        with self.assertRaises(ValidationError):
            self._create_doctor(rating=5.5)

    def test_archive_with_active_visits_forbidden(self):
        doctor = self._create_doctor()
        patient = self._create_patient()
        self._create_visit(
            doctor=doctor,
            patient=patient,
            plan_datetime=fields.Datetime.now() + relativedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            doctor.write({"active": False})

    def test_mentor_only_for_intern(self):
        mentor = self._create_doctor(license_number="LIC-MENTOR-DR")
        with self.assertRaises(ValidationError):
            self._create_doctor(
                license_number="LIC-NON-INTERN-DR",
                is_intern=False,
                mentor_doctor_id=mentor.id,
            )

