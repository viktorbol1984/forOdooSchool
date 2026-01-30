{
    'name': 'Odoo School Library',
    'author': 'Viktor Bol',
    'website': 'https://odoo.school/',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '19.0.2.1.1',
    'depends': ['base',],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'security/ir.model.access.csv',

        'views/odoo_school_library_menu.xml',
        'views/odoo_school_library_book_views.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
        'demo/odoo.school.library.book.csv',
    ],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}