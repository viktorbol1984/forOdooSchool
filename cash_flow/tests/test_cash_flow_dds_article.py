from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowDDSArticle(TransactionCase):
    def test_01_create_dds_article(self):
        category = self.env["cash.flow.dds.category"].create({"name": "Test Category"})
        article = self.env["cash.flow.dds.article"].create(
            {
                "name": "Test Article",
                "category_id": category.id,
                "transaction_type": "expense",
            }
        )
        self.assertTrue(article)
