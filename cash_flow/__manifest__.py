{
    "name": "Cash Flow",
    "summary": "Cash flow accounting",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "author": "viktorbol1984",
    "license": "LGPL-3",
    "images": ["static/description/icon.png"],
    "depends": ["base", "base_address_extended"],
    "data": [
        "security/ir.model.access.csv",
        "views/cash_flow_views.xml",
        "wizard/cash_flow_forecast_wizard_views.xml",
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
    ],
    "demo": [
        "demo/cash_flow_demo.xml",
    ],
    "application": True,
    "installable": True,
}
