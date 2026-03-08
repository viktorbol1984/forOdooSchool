from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    city_id = fields.Many2one(
        "res.city",
        string="City",
        ondelete="restrict",
    )
