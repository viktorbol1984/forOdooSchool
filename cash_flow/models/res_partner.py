from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_dds_article_id = fields.Many2one(
        "cash.flow.dds.article",
        string="Default DDS Article",
        ondelete="set null",
    )
