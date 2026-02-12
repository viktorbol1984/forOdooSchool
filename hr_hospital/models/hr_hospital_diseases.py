from odoo import models, fields

class Diseases(models.Model):
    _name = 'hr.hospital.diseases'
    _description = 'Diseases'
    _parent_name = 'parent_id'
    _parent_store = True
    parent_path = fields.Char(index=True)

    name = fields.Char()

    active = fields.Boolean(
        default=True
    )

    description = fields.Text()

    parent_id = fields.Many2one(
        'hr.hospital.diseases',
        string='Parent',
    )

    child_ids = fields.One2many(
        'hr.hospital.diseases',
        'parent_id',
        string='Child Diseases',
    )

    icd10_code = fields.Char(
        string='ICD-10 Code',
        size=10,
    )

    severity = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
    )

    is_contagious = fields.Boolean()

    symptoms = fields.Text()

    affected_country_ids = fields.Many2many(
        'res.country',
        'disease_country_rel',
        'disease_id',
        'country_id',
        string='Affected Regions',
    )