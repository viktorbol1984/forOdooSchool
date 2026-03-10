from odoo import fields, models


class ForecastWizard(models.TransientModel):
    _name = "forecast.wizard"
    _description = "Cash Flow Forecast Wizard"

    date_from = fields.Date()
    date_to = fields.Date()

    def action_generate(self):
        return {"type": "ir.actions.act_window_close"}
