from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowCashbox(TransactionCase):
    def test_01_create_cashbox(self):
        city = self.env["res.city"].create(
            {
                "name": "Test City",
                "country_id": self.env.ref("base.us").id,
            }
        )
        user = self.env["res.users"].create(
            {
                "name": "Cashier",
                "login": "cashier_cashbox",
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
        self.assertTrue(cashbox)
