# -*- coding: utf-8 -*-
{
    'name': 'Alert Management',
    'version': '1.2',
    'summary': 'Alert Management',
    'sequence': 10,
    'description': """
Alert management
====================
TO_FILL_IN
    """,
    'category': 'hidden',
    'website': 'https://apps.odoo.com/apps/modules/15.0/alert_configuration/',
    'images': [],
    'depends': ['base', 'mail'],
    'data': [
        'data/ir_cron.xml',
        'security/alert_security.xml',
        'security/ir.model.access.csv',
        'views/alert_configuration.xml',
        'views/alert_management_menuitem.xml',

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
