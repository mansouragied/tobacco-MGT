# -*- coding: utf-8 -*-
{
    'name': "Marinti Tobacco Management",
    'version': '17.0.1.0.0',
    "category": "Manufacturing",
    'summary': "Extend Odoo BOM for tobacco production specifics",
    'author': "Khotawat Consultancy",
    'description': "Adds Item Code, Material, and custom usage to standard BOM lines.",
    "license": "LGPL-3",
    'depends': ['base','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/sub_bom_views.xml',
        'views/main_bom.xml',
        'views/show_qty_mc.xml',
        'views/making_operation_views.xml',
        'views/packing_operation_views.xml',
        'views/performance_views.xml',
    ],
    'installable': True,
    'application': True,
}


