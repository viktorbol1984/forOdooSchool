{
    'name': 'HR Hospital',
    'author': 'Viktor Bol',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '19.0.1.1.0',
    'depends': ['base',],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',

        'wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml',
        'wizard/hr_hospital_doctor_schedule_wizard_view.xml',
        'wizard/hr_hospital_reschedule_visit_wizard_view.xml',
        'wizard/hr_hospital_disease_report_wizard_view.xml',

        'data/hr_hospital_diseases_data.xml',
        'views/hr_hospital_views.xml',
        'views/hr_hospital_menu.xml',

    ],
    # 'demo': ['demo/hr_hospital_doctors_demo.xml',],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
