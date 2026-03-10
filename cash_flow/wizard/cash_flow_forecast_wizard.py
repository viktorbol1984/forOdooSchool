from datetime import timedelta

from odoo import api, fields, models


class CashFlowForecastWizard(models.TransientModel):
    _name = "cash.flow.forecast.wizard"
    _description = "Cash Flow Forecast Wizard"

    cashbox_ids = fields.Many2many(
        comodel_name="cash.flow.cashbox",
        string="Cashboxes",
        help="Leave empty for all cashboxes",
    )
    date_from = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self) + timedelta(days=30),
    )
    include_planned = fields.Boolean(string="Include planned", default=True)
    include_actual = fields.Boolean(string="Include actual", default=True)

    line_ids = fields.One2many(
        comodel_name="cash.flow.forecast.wizard.line",
        inverse_name="wizard_id",
        string="Forecast",
        readonly=True,
    )

    def _compute_lines(self):
        self.ensure_one()
        self.line_ids.unlink()

        cashboxes = self.cashbox_ids or self.env["cash.flow.cashbox"].search([])
        if not cashboxes:
            return

        kinds = []
        if self.include_actual:
            kinds.append(False)
        if self.include_planned:
            kinds.append(True)

        lines_to_create = []
        for cashbox in cashboxes:
            start_balance = self._compute_start_balance(cashbox)
            current_balance = start_balance

            current_date = self.date_from
            while current_date <= self.date_to:
                day_domain = [
                    ("cashbox_id", "=", cashbox.id),
                    ("date", "=", current_date),
                    ("is_planned", "in", kinds),
                ]
                day_lines = self.env["cash.flow.transaction"].search(day_domain)
                income = sum(
                    day_lines.filtered(lambda l: l.transaction_type == "income").mapped("amount")
                )
                expense = sum(
                    day_lines.filtered(lambda l: l.transaction_type == "expense").mapped("amount")
                )
                current_balance = current_balance + income - expense

                lines_to_create.append(
                    {
                        "wizard_id": self.id,
                        "cashbox_id": cashbox.id,
                        "date": current_date,
                        "income": income,
                        "expense": expense,
                        "balance": current_balance,
                        "is_gap": current_balance < 0,
                    }
                )
                current_date += timedelta(days=1)

        if lines_to_create:
            self.env["cash.flow.forecast.wizard.line"].create(lines_to_create)

    def action_compute(self):
        self.ensure_one()
        self._compute_lines()
        return {
            "type": "ir.actions.act_window",
            "name": "Forecast Pivot",
            "res_model": "cash.flow.forecast.wizard.line",
            "view_mode": "pivot",
            "target": "current",
            "domain": [("wizard_id", "=", self.id)],
            "views": [(self.env.ref("cash_flow.view_cash_flow_forecast_wizard_line_pivot").id, "pivot")],
        }

    def _compute_start_balance(self, cashbox):
        domain = [
            ("cashbox_id", "=", cashbox.id),
            ("date", "<", self.date_from),
            ("is_planned", "=", False),
        ]
        lines = self.env["cash.flow.transaction"].search(domain)
        income = sum(lines.filtered(lambda l: l.transaction_type == "income").mapped("amount"))
        expense = sum(lines.filtered(lambda l: l.transaction_type == "expense").mapped("amount"))
        return income - expense


class CashFlowForecastWizardLine(models.TransientModel):
    _name = "cash.flow.forecast.wizard.line"
    _description = "Cash Flow Forecast Wizard Line"
    _order = "cashbox_id, date asc"

    wizard_id = fields.Many2one(
        comodel_name="cash.flow.forecast.wizard",
        ondelete="cascade",
    )
    cashbox_id = fields.Many2one(
        comodel_name="cash.flow.cashbox",
        string="Cashbox",
        required=True,
    )
    currency_id = fields.Many2one(
        related="cashbox_id.currency_id",
        store=True,
        readonly=True,
    )
    date = fields.Date(required=True)
    income = fields.Monetary(currency_field="currency_id")
    expense = fields.Monetary(currency_field="currency_id")
    balance = fields.Monetary(currency_field="currency_id")
    is_gap = fields.Boolean(string="Cash Gap")
