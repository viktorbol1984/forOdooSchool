from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "access")
class TestAccessRights(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env["res.country"].create({"name": "Doctorland", "code": "DL"})
        cls.speciality = cls.env["hr.hospital.doctor.speciality"].create(
            {"name": "Therapist", "code": "THR"}
        )
        cls.intern_group = cls.env.ref("hr_hospital.group_hr_hospital_intern")

        cls.intern_user = cls.env["res.users"].create(
            {
                "name": "Intern User 1",
                "login": "intern_user_1",
                "email": "intern_user_1@example.com",
                "group_ids": [Command.set([cls.intern_group.id])],
            }
        )
        cls.other_intern_user = cls.env["res.users"].create(
            {
                "name": "Intern User 2",
                "login": "intern_user_2",
                "email": "intern_user_2@example.com",
                "group_ids": [Command.set([cls.intern_group.id])],
            }
        )
        cls.intern_doctor = cls.env["hr.hospital.doctors"].create(
            {
                "name": "Intern Doctor 1",
                "license_number": "LIC-INTERN-1",
                "country_id": cls.country.id,
                "speciality_id": cls.speciality.id,
                "is_intern": True,
                "user_id": cls.intern_user.id,
            }
        )
        cls.other_intern_doctor = cls.env["hr.hospital.doctors"].create(
            {
                "name": "Intern Doctor 2",
                "license_number": "LIC-INTERN-2",
                "country_id": cls.country.id,
                "speciality_id": cls.speciality.id,
                "is_intern": True,
                "user_id": cls.other_intern_user.id,
            }
        )
        cls.patient_1 = cls.env["hr.hospital.patients"].create(
            {
                "name": "Patient 1",
                "birth_date": fields.Date.today() - relativedelta(years=30),
                "country_id": cls.country.id,
            }
        )
        cls.patient_2 = cls.env["hr.hospital.patients"].create(
            {
                "name": "Patient 2",
                "birth_date": fields.Date.today() - relativedelta(years=35),
                "country_id": cls.country.id,
            }
        )
        cls.first_plan_datetime = fields.Datetime.now() + relativedelta(days=1)
        cls.second_plan_datetime = fields.Datetime.now() + relativedelta(days=2)
        first_plan_date = fields.Date.to_date(cls.first_plan_datetime)
        second_plan_date = fields.Date.to_date(cls.second_plan_datetime)

        cls.env["hr.hospital.doctor.schedule"].create(
            {
                "doctor_id": cls.intern_doctor.id,
                "date": first_plan_date,
                "schedule_type": "working_day",
                "start_time": 9.0,
                "end_time": 18.0,
            }
        )
        cls.env["hr.hospital.doctor.schedule"].create(
            {
                "doctor_id": cls.other_intern_doctor.id,
                "date": second_plan_date,
                "schedule_type": "working_day",
                "start_time": 9.0,
                "end_time": 18.0,
            }
        )
        cls.env["hr.hospital.patient.doctor.history"].create(
            {
                "patient_id": cls.patient_1.id,
                "doctor_id": cls.intern_doctor.id,
                "assignment_date": first_plan_date - relativedelta(days=1),
            }
        )
        cls.env["hr.hospital.patient.doctor.history"].create(
            {
                "patient_id": cls.patient_2.id,
                "doctor_id": cls.other_intern_doctor.id,
                "assignment_date": second_plan_date - relativedelta(days=1),
            }
        )
        cls.own_visit = cls.env["hr.hospital.visits"].create(
            {
                "doctor_id": cls.intern_doctor.id,
                "patient_id": cls.patient_1.id,
                "plan_datetime": cls.first_plan_datetime,
            }
        )
        cls.env["hr.hospital.visits"].create(
            {
                "doctor_id": cls.other_intern_doctor.id,
                "patient_id": cls.patient_2.id,
                "plan_datetime": cls.second_plan_datetime,
            }
        )


    def test_01_intern_can_access_only_own_visits(self):
        visible_visits = self.env["hr.hospital.visits"].with_user(self.intern_user).search([])
        self.assertEqual(visible_visits.ids, [self.own_visit.id])
