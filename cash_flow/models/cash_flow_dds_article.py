from odoo import fields, models


class CashFlowDdsArticle(models.Model):
    """DDS article for transaction classification."""

    _name = "cash.flow.dds.article"
    _description = "DDS Article"
    _order = "name"

    name = fields.Char(required=True)
    category_id = fields.Many2one(
        "cash.flow.dds.category",
        string="DDS Category",
        required=True,
        ondelete="restrict",
    )
    active = fields.Boolean(default=True)
    transaction_type = fields.Selection(
        [("income", "Income"), ("expense", "Expense")],
        required=True,
        default="income",
    )
    note = fields.Text()
