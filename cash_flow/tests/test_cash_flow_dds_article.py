from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowDDSArticle(TransactionCase):
    """Creation test for DDS articles."""

    def test_01_create_dds_article(self):
        """DDS article can be created with required fields."""
        category = self.env["cash.flow.dds.category"].create({"name": "Test Category"})
        article = self.env["cash.flow.dds.article"].create(
            {
                "name": "Test Article",
                "category_id": category.id,
                "transaction_type": "expense",
            }
        )
        self.assertTrue(article)
