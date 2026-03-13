from odoo import fields, models


class ResUsers(models.Model):
    """Extend users with a city reference for cash flow rules."""

    _inherit = "res.users"

    city_id = fields.Many2one(
        "res.city",
        string="City",
        ondelete="restrict",
    )
