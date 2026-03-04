from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestHrHospitalVisits(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._doctor_seq = 0
        cls.country = cls.env["res.country"].create(
            {"name": "Visitland", "code": "VL"}
        )
        cls.speciality = cls.env["hr.hospital.doctor.speciality"].create(
            {"name": "Cardiologist", "code": "CRD"}
        )

    def _create_patient(self, **extra_vals):
        vals = {
            "name": "Visit Patient",
            "birth_date": fields.Date.today() - relativedelta(years=25),
            "country_id": self.country.id,
        }
        vals.update(extra_vals)
        return self.env["hr.hospital.patients"].create(vals)

    def _create_doctor(self, **extra_vals):
        self.__class__._doctor_seq += 1
        vals = {
            "name": "Visit Doctor",
            "license_number": f"LIC-VISIT-{self._doctor_seq}",
            "country_id": self.country.id,
            "speciality_id": self.speciality.id,
        }
        vals.update(extra_vals)
        return self.env["hr.hospital.doctors"].create(vals)

    def _add_work_schedule(self, doctor, plan_datetime):
        self.env["hr.hospital.doctor.schedule"].create(
            {
                "doctor_id": doctor.id,
                "date": fields.Date.to_date(plan_datetime),
                "schedule_type": "working_day",
                "start_time": 9.0,
                "end_time": 18.0,
            }
        )

    def _assign_patient_doctor(self, patient, doctor, assignment_date):
        self.env["hr.hospital.patient.doctor.history"].create(
            {
                "patient_id": patient.id,
                "doctor_id": doctor.id,
                "assignment_date": assignment_date,
            }
        )

    def _create_visit(self, doctor, patient, plan_datetime):
        plan_date = fields.Date.to_date(plan_datetime)
        self._add_work_schedule(doctor=doctor, plan_datetime=plan_datetime)
        self._assign_patient_doctor(
            patient=patient,
            doctor=doctor,
            assignment_date=plan_date - relativedelta(days=1),
        )
        return self.env["hr.hospital.visits"].create(
            {
                "doctor_id": doctor.id,
                "patient_id": patient.id,
                "plan_datetime": plan_datetime,
            }
        )

    def test_duplicate_same_day_forbidden(self):
        doctor = self._create_doctor()
        patient = self._create_patient()
        plan_datetime = fields.Datetime.now() + relativedelta(days=2)
        self._create_visit(doctor=doctor, patient=patient, plan_datetime=plan_datetime)

        with self.assertRaises(ValidationError):
            self.env["hr.hospital.visits"].create(
                {
                    "doctor_id": doctor.id,
                    "patient_id": patient.id,
                    "plan_datetime": plan_datetime + relativedelta(hours=2),
                }
            )

    def test_requires_patient_doctor_history(self):
        doctor = self._create_doctor()
        patient = self._create_patient()
        plan_datetime = fields.Datetime.now() + relativedelta(days=3)
        self._add_work_schedule(doctor=doctor, plan_datetime=plan_datetime)

        with self.assertRaises(ValidationError):
            self.env["hr.hospital.visits"].create(
                {
                    "doctor_id": doctor.id,
                    "patient_id": patient.id,
                    "plan_datetime": plan_datetime,
                }
            )

    def test_mentor_is_computed_for_intern_doctor(self):
        mentor = self._create_doctor(license_number="LIC-MENTOR-VISIT")
        intern = self._create_doctor(
            license_number="LIC-INTERN-VISIT",
            is_intern=True,
            mentor_doctor_id=mentor.id,
        )
        patient = self._create_patient()
        visit = self._create_visit(
            doctor=intern,
            patient=patient,
            plan_datetime=fields.Datetime.now() + relativedelta(days=4),
        )
        self.assertEqual(visit.mentor_doctor_id, mentor)

    def test_write_doctor_forbidden_after_fact_datetime(self):
        doctor = self._create_doctor(license_number="LIC-WRITE-V1")
        another_doctor = self._create_doctor(license_number="LIC-WRITE-V2")
        patient = self._create_patient()
        visit = self._create_visit(
            doctor=doctor,
            patient=patient,
            plan_datetime=fields.Datetime.now() + relativedelta(days=5),
        )

        visit.write({"fact_datetime": fields.Datetime.now()})
        with self.assertRaises(ValidationError):
            visit.write({"doctor_id": another_doctor.id})

    def test_cannot_be_deleted_with_diagnosis(self):
        doctor = self._create_doctor(license_number="LIC-DEL-VISIT")
        patient = self._create_patient()
        visit = self._create_visit(
            doctor=doctor,
            patient=patient,
            plan_datetime=fields.Datetime.now() + relativedelta(days=6),
        )
        self.env["hr.hospital.medical.diagnosis"].create({"visit_id": visit.id})

        with self.assertRaises(UserError):
            visit.unlink()

