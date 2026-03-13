from odoo import fields, models


class CashFlowDdsCategory(models.Model):
    """Hierarchical DDS category."""

    _name = "cash.flow.dds.category"
    _description = "DDS Category"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "name"

    parent_path = fields.Char(index=True)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one(
        "cash.flow.dds.category",
        string="Parent Category",
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        "cash.flow.dds.category",
        "parent_id",
        string="Child Categories",
    )
