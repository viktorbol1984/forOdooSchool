"""HR Hospital module."""

from datetime import datetime, time, timedelta

from odoo import models, fields


class RescheduleVisitWizard(models.TransientModel):
    _name = 'hr.hospital.reschedule.visit.wizard'
    _description = 'Reschedule Visit Wizard'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visits',
        string='Visit',
    )
    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='New Doctor',
    )
    new_date = fields.Date(
        string='New Date',
        required=True,
    )
    new_time = fields.Float(
        string='New Time',
        required=True,
    )
    reschedule_reason = fields.Text(
        string='Reschedule Reason',
        required=True,
    )

    def action_apply(self):
        self.ensure_one()
        if not self.visit_id:
            return {'type': 'ir.actions.act_window_close'}

        new_doctor = self.new_doctor_id or self.visit_id.doctor_id
        if not new_doctor:
            return {'type': 'ir.actions.act_window_close'}

        plan_datetime = datetime.combine(
            self.new_date,
            time.min
        ) + timedelta(hours=self.new_time)

        self.visit_id.write({'active': False})
        self.env['hr.hospital.visits'].create({
            'doctor_id': new_doctor.id,
            'patient_id': self.visit_id.patient_id.id,
            'plan_datetime': fields.Datetime.to_string(plan_datetime),
        })

        return {'type': 'ir.actions.act_window_close'}
