from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestHrHospitalDiseases(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env["res.country"].create(
            {"name": "Diseaseland", "code": "DS"}
        )

    def test_defaults_and_hierarchy(self):
        parent = self.env["hr.hospital.diseases"].create(
            {"name": "Respiratory", "description": "Parent disease"}
        )
        child = self.env["hr.hospital.diseases"].create(
            {
                "name": "Flu Child",
                "description": "Child disease",
                "parent_id": parent.id,
                "affected_country_ids": [(6, 0, [self.country.id])],
                "severity": "medium",
                "is_contagious": True,
            }
        )

        self.assertTrue(parent.active)
        self.assertEqual(child.parent_id, parent)
        self.assertFalse(child.child_ids)
        self.assertIn(self.country, child.affected_country_ids)

