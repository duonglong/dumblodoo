# -*- coding: utf-8 -*-
{
    'name': 'Notification Management',
    'version': '1.2',
    'summary': 'Notification Management',
    'sequence': 10,
    'description': """
Notification management
====================
TO_FILL_IN
    """,
    'category': 'hidden',
    'website': 'https://apps.odoo.com/apps/modules/15.0/notification_configuration/',
    'images': [],
    'depends': ['base', 'mail'],
    'data': [
        'data/ir_cron.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/notification_configuration.xml',
        'views/notification_compare_fields.xml',
        'views/notification_compare_value.xml',
        'views/notification_management_menuitem.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {

    },
    'license': 'LGPL-3',
}
