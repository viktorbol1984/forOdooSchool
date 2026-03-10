from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CashFlowTransaction(models.Model):
    _name = "cash.flow.transaction"
    _description = "Cashbox Transaction"
    _order = "date desc, id desc"

    name = fields.Char(required=True, default="Transaction 0", copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.today)
    is_planned = fields.Boolean(string="Planned", default=False)
    cashbox_id = fields.Many2one(
        "cash.flow.cashbox",
        required=True,
        ondelete="restrict",
    )
    transfer_id = fields.Many2one(
        "cash.flow.transfer",
        string="Transfer",
        ondelete="set null",
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        ondelete="set null",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="cashbox_id.currency_id",
        store=True,
        readonly=True,
    )
    transaction_type = fields.Selection(
        [("income", "Income"), ("expense", "Expense")],
        required=True,
        default="income",
    )
    amount = fields.Monetary(required=True)
    note = fields.Text()
    article_id = fields.Many2one(
        "cash.flow.dds.article",
        string="DDS Article",
        ondelete="restrict",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_set_default_article(self):
        for rec in self:
            if rec.partner_id and not rec.article_id:
                rec.article_id = rec.partner_id.default_dds_article_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec.name = f"Transaction {rec.id}"
        return records

    @api.constrains("is_planned", "date")
    def _check_planned_date_is_future(self):
        today = fields.Date.today()
        for rec in self:
            if rec.is_planned and rec.date and rec.date <= today:
                raise ValidationError("Planned transaction must have a future date.")
