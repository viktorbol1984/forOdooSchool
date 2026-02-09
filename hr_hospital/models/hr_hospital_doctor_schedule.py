from odoo import models, fields

class DoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Doctor',
        required=True,
    )

    day_of_week = fields.Selection(
        selection=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday')
        ],
        string='Day of Week'
    )

    date = fields.Date()

    start_time = fields.Float()

    end_time = fields.Float()

    schedule_type = fields.Selection(
        selection=[
            ('working_day', 'Working Day'),
            ('vacation', 'Vacation'),
            ('sick_leave', 'Sick Leave'),
            ('conference', 'Conference')
        ],
        default='working_day'
    )

    notes = fields.Char()