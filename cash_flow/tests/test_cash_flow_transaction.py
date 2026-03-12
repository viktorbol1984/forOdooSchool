from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowTransaction(TransactionCase):
    def test_01_create_transaction(self):
        city = self.env["res.city"].create(
            {
                "name": "Test City",
                "country_id": self.env.ref("base.us").id,
            }
        )
        user = self.env["res.users"].create(
            {
                "name": "Cashier",
                "login": "cashier_transaction",
                "city_id": city.id,
                "group_ids": [(6, 0, [self.env.ref("cash_flow.group_cash_flow_user").id])],
            }
        )
        cashbox = self.env["cash.flow.cashbox"].create(
            {
                "name": "Test Cashbox",
                "city_id": city.id,
                "cashier_user_id": user.id,
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        category = self.env["cash.flow.dds.category"].create({"name": "Test Category"})
        article = self.env["cash.flow.dds.article"].create(
            {
                "name": "Test Article",
                "category_id": category.id,
                "transaction_type": "income",
            }
        )
        tx = self.env["cash.flow.transaction"].create(
            {
                "cashbox_id": cashbox.id,
                "amount": 100,
                "article_id": article.id,
            }
        )
        self.assertTrue(tx)
