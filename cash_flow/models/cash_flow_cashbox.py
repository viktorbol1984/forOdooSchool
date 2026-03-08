from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CashFlowCashbox(models.Model):
    _name = "cash.flow.cashbox"
    _description = "Cashbox"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    city_id = fields.Many2one(
        "res.city",
        string="City",
        required=True,
        ondelete="restrict",
    )
    cashier_user_id = fields.Many2one(
        "res.users",
        string="Cashier",
        required=True,
        ondelete="restrict",
        default=lambda self: self.env.user,
        domain="[('city_id', '=', city_id)]",
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    transaction_ids = fields.One2many(
        "cash.flow.transaction",
        "cashbox_id",
        string="Transactions",
    )

    _cashier_unique = models.Constraint(
        "unique (cashier_user_id)",
        "Each cashier user can be assigned to only one cashbox.",
    )

    @api.constrains("city_id", "cashier_user_id")
    def _check_cashier_city(self):
        for rec in self:
            if rec.cashier_user_id and rec.city_id != rec.cashier_user_id.city_id:
                raise ValidationError("Cashier city must match cashbox city.")
