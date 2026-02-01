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

        'views/hr_hospital_views.xml',
        'views/hr_hospital_menu.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}