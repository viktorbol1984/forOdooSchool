from odoo import models, fields, api


class MassReassignDoctorWizard(models.TransientModel):
    _name = 'hr.hospital.reassign.doctor.wizard'
    _description = 'Mass Reassign Doctor Wizard'

    # old_doctor_id = fields.Many2one( not needed yet, but maybe
    #     comodel_name='hr.hospital.doctors',
    #     string='New Doctor',
    #     required=True,
    # )

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctors',
        string='New Doctor',
        required=True,
    )

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patients',
        string='Patients',
        required=True,
    )
    change_date = fields.Date()
    change_reason = fields.Text()

    @api.model
    def default_get(self, fields_list):
        res = super(MassReassignDoctorWizard, self).default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'hr.hospital.patients' and active_ids:
            res['patient_ids'] = [(6, 0, active_ids)]
        res['change_date'] = fields.Date.today()
        return res

    def action_apply(self):
        history_model = self.env['hr.hospital.patient.doctor.history']
        change_date = self.change_date
        for patient in self.patient_ids:
            history_model.create({
                'patient_id': patient.id,
                'doctor_id': self.new_doctor_id.id,
                'assignment_date': change_date,
                'change_date': change_date,
                'change_reason': self.change_reason,
            })
        return {'type': 'ir.actions.act_window_close'}
