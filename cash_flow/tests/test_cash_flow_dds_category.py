from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowDDSCategory(TransactionCase):
    """Creation test for DDS categories."""

    def test_01_create_dds_category(self):
        """DDS category can be created with required fields."""
        category = self.env["cash.flow.dds.category"].create({"name": "Test Category"})
        self.assertTrue(category)
