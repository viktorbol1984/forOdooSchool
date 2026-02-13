from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class AbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Person Model'
    _inherit = ['image.mixin']

    last_name = fields.Char(
    )
    first_name = fields.Char(
    )
    patronymic = fields.Char(
    )

    phone = fields.Char(
    )

    email = fields.Char(
    )

    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
    )
    birth_date = fields.Date()

    age = fields.Integer(
        compute='_compute_age',
    )

    full_name = fields.Char(
        compute='_compute_full_name',
        store=True
    )

    country_id = fields.Many2one(
        comodel_name='res.country'
    )

    lang_id = fields.Many2one(
        comodel_name='res.lang'
    )

    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if record.birth_date:
                birth_date = record.birth_date
                age = today.year - birth_date.year
                record.age = age
            else:
                record.age = 0

    @api.depends('last_name', 'first_name', 'patronymic')
    def _compute_full_name(self):
        for rec in self:
            parts = [rec.last_name, rec.first_name, rec.patronymic]
            rec.full_name = " ".join(p for p in parts if p)


    @api.constrains('phone')
    def _check_phone(self):
        pattern = re.compile(r'^\+?[0-9\s\-()]{7,20}$')
        for rec in self:
            if rec.phone and not pattern.match(rec.phone):
                raise ValidationError("Wrong phone")

    @api.constrains('email')
    def _check_email(self):
        pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        for rec in self:
            if rec.email and not pattern.match(rec.email):
                raise ValidationError("Wrong email")

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if not self.country_id or not self.country_id.code:
            return
        lang = self.env['res.lang'].search([
            ('active', '=', True),
            ('code', 'ilike', f'%_{self.country_id.code}')
        ], limit=1)
        if lang:
            self.lang_id = lang.id
