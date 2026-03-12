from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "cash_flow")
class TestCashFlowTransfer(TransactionCase):
    def test_01_create_transfer(self):
        city = self.env["res.city"].create(
            {
                "name": "Test City",
                "country_id": self.env.ref("base.us").id,
            }
        )
        user_1 = self.env["res.users"].create(
            {
                "name": "Cashier 1",
                "login": "cashier_transfer_1",
                "city_id": city.id,
                "group_ids": [(6, 0, [self.env.ref("cash_flow.group_cash_flow_user").id])],
            }
        )
        user_2 = self.env["res.users"].create(
            {
                "name": "Cashier 2",
                "login": "cashier_transfer_2",
                "city_id": city.id,
                "group_ids": [(6, 0, [self.env.ref("cash_flow.group_cash_flow_user").id])],
            }
        )
        cashbox_1 = self.env["cash.flow.cashbox"].create(
            {
                "name": "Test Cashbox 1",
                "city_id": city.id,
                "cashier_user_id": user_1.id,
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        cashbox_2 = self.env["cash.flow.cashbox"].create(
            {
                "name": "Test Cashbox 2",
                "city_id": city.id,
                "cashier_user_id": user_2.id,
                "currency_id": self.env.ref("base.USD").id,
            }
        )
        transfer = self.env["cash.flow.transfer"].create(
            {
                "source_cashbox_id": cashbox_1.id,
                "destination_cashbox_id": cashbox_2.id,
                "amount": 50,
            }
        )
        self.assertTrue(transfer)
