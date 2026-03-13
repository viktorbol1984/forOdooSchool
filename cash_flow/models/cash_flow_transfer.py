from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CashFlowTransfer(models.Model):
    """Transfer between two cashboxes with posting logic."""

    _name = "cash.flow.transfer"
    _description = "Cashbox Transfer"
    _order = "date desc, id desc"

    name = fields.Char(required=True, default="Transfer №0", copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.today)
    source_cashbox_id = fields.Many2one(
        "cash.flow.cashbox",
        string="Source Cashbox",
        required=True,
        ondelete="restrict",
    )
    destination_cashbox_id = fields.Many2one(
        "cash.flow.cashbox",
        string="Destination Cashbox",
        required=True,
        ondelete="restrict",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="source_cashbox_id.currency_id",
        store=True,
        readonly=True,
    )
    amount = fields.Monetary(required=True)
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")],
        default="draft",
        required=True,
        readonly=True,
    )
    expense_transaction_id = fields.Many2one(
        "cash.flow.transaction",
        string="Expense Transaction",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    income_transaction_id = fields.Many2one(
        "cash.flow.transaction",
        string="Income Transaction",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Assign a human-readable transfer name after creation."""
        records = super().create(vals_list)
        for rec in records:
            rec.name = f"Transfer {rec.id}"
        return records

    @api.constrains("source_cashbox_id", "destination_cashbox_id")
    def _check_cashboxes_are_different(self):
        """Ensure source and destination cashboxes are not the same."""
        for rec in self:
            if rec.source_cashbox_id and rec.source_cashbox_id == rec.destination_cashbox_id:
                raise ValidationError("Source and destination cashboxes must be different.")

    @api.constrains("source_cashbox_id", "destination_cashbox_id")
    def _check_same_currency(self):
        """Ensure both cashboxes use the same currency."""
        for rec in self:
            if (
                rec.source_cashbox_id
                and rec.destination_cashbox_id
                and rec.source_cashbox_id.currency_id != rec.destination_cashbox_id.currency_id
            ):
                raise ValidationError("Cashboxes must have the same currency for transfer.")

    @api.constrains("amount")
    def _check_positive_amount(self):
        """Ensure transfer amount is positive."""
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Transfer amount must be greater than zero.")

    def action_post(self):
        """Post transfer and create matching income/expense transactions."""
        for rec in self:
            if rec.state != "draft":
                continue
            expense = self.env["cash.flow.transaction"].create(
                {
                    "name": f"Transfer to {rec.destination_cashbox_id.name}",
                    "date": rec.date,
                    "cashbox_id": rec.source_cashbox_id.id,
                    "transaction_type": "expense",
                    "amount": rec.amount,
                    "note": rec.note,
                    "transfer_id": rec.id,
                }
            )
            income = self.env["cash.flow.transaction"].create(
                {
                    "name": f"Transfer from {rec.source_cashbox_id.name}",
                    "date": rec.date,
                    "cashbox_id": rec.destination_cashbox_id.id,
                    "transaction_type": "income",
                    "amount": rec.amount,
                    "note": rec.note,
                    "transfer_id": rec.id,
                }
            )
            rec.write(
                {
                    "expense_transaction_id": expense.id,
                    "income_transaction_id": income.id,
                    "state": "posted",
                }
            )

    def unlink(self):
        """Prevent deletion of posted transfers."""
        for rec in self:
            if rec.state == "posted":
                raise UserError("You cannot delete a posted transfer.")
        return super().unlink()
