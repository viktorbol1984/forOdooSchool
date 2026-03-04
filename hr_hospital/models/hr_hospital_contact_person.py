"""HR Hospital module."""

from odoo import models, fields


class ContactPerson(models.Model):
    """Emergency or related contact information for a patient."""

    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = ['hr.hospital.abstract.person']

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patients',
        string='Patient',
        domain=[
            ('allergies', '!=', ''),
        ],
    )

    description = fields.Text()
