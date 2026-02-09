from odoo import models, fields

class ContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()