from datetime import timedelta
from odoo import models, fields


class DoctorScheduleWizard(models.TransientModel):
    _name = 'hr.hospital.doctor.schedule.wizard'
    _description = 'Doctor Schedule Wizard'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='Doctor',
        required=True,
    )
    week_start = fields.Date(
        string='Week Start',
        required=True,
    )
    weeks_count = fields.Integer(
        string='Weeks Count',
        default=1,
        required=True,
    )
    schedule_type = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('even_week', 'Even Week'),
            ('odd_week', 'Odd Week'),
        ],
        string='Schedule Type',
    )

    monday = fields.Boolean(string='Monday')
    tuesday = fields.Boolean(string='Tuesday')
    wednesday = fields.Boolean(string='Wednesday')
    thursday = fields.Boolean(string='Thursday')
    friday = fields.Boolean(string='Friday')
    saturday = fields.Boolean(string='Saturday')
    sunday = fields.Boolean(string='Sunday')

    time_start = fields.Float(string='Start Time')
    time_end = fields.Float(string='End Time')

    break_start = fields.Float(string='Break From')
    break_end = fields.Float(string='Break To')

    def action_apply(self):
        self.ensure_one()
        if not self.doctor_id or not self.week_start:
            return {'type': 'ir.actions.act_window_close'}

        day_flags = [
            ('monday', self.monday, 0),
            ('tuesday', self.tuesday, 1),
            ('wednesday', self.wednesday, 2),
            ('thursday', self.thursday, 3),
            ('friday', self.friday, 4),
            ('saturday', self.saturday, 5),
            ('sunday', self.sunday, 6),
        ]
        selected_days = [(name, offset) for name, flag, offset in day_flags if flag]
        if not selected_days:
            return {'type': 'ir.actions.act_window_close'}

        week_start = fields.Date.to_date(self.week_start)
        weeks_count = max(self.weeks_count or 0, 0)
        notes = []
        if self.schedule_type:
            notes.append(f"Schedule: {self.schedule_type}")
        if self.break_start or self.break_end:
            notes.append(f"Break: {self.break_start}-{self.break_end}")
        note_text = " | ".join(notes) if notes else False

        values = []
        for week_index in range(weeks_count):
            if self.schedule_type == 'even_week' and (week_index + 1) % 2 != 0:
                continue
            if self.schedule_type == 'odd_week' and (week_index + 1) % 2 == 0:
                continue
            week_base = week_start + timedelta(days=week_index * 7)
            for day_name, day_offset in selected_days:
                values.append({
                    'doctor_id': self.doctor_id.id,
                    'day_of_week': day_name,
                    'date': week_base + timedelta(days=day_offset),
                    'start_time': self.time_start,
                    'end_time': self.time_end,
                    'schedule_type': 'working_day',
                    'notes': note_text,
                })

        if values:
            self.env['hr.hospital.doctor.schedule'].create(values)

        return {'type': 'ir.actions.act_window_close'}
