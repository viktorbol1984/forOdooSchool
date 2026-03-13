from odoo import api, models


class CashFlowReportBalances(models.AbstractModel):
    """Report for cashbox balances."""

    _name = "report.cash_flow.report_cashbox_balances"
    _description = "Cashbox Balances Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Build report lines with income/expense per cashbox."""
        Сashbox = self.env["cash.flow.cashbox"].sudo()
        Transaction = self.env["cash.flow.transaction"].sudo()

        totals = {}
        transactions = Transaction.search(
            [("is_planned", "=", False), ]
        )
        for tx in transactions:
            cashbox_id = tx.cashbox_id.id
            entry = totals.setdefault(cashbox_id, {"income": 0.0, "expense": 0.0})
            if tx.transaction_type == "income":
                entry["income"] += tx.amount
            elif tx.transaction_type == "expense":
                entry["expense"] += tx.amount

        lines = []
        cashboxes = Сashbox.browse(list(totals.keys())).sorted(lambda a: a.name or "")
        for cashbox in cashboxes:
            amounts = totals.get(cashbox.id, {"income": 0.0, "expense": 0.0})
            income = amounts.get("income", 0.0)
            expense = amounts.get("expense", 0.0)
            balance = income - expense
            lines.append(
                {
                    "cashbox": cashbox,
                    "currency": cashbox.currency_id,
                    "income": income,
                    "expense": expense,
                    "balance": balance,
                }
            )

        return {
            "doc_ids": docids,
            "doc_model": "cash.flow.cashbox",
            "docs": cashboxes,
            "lines": lines,
        }
