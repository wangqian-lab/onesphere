# -*- coding: utf-8 -*-
{
    'name': "onesphere_assemably_industry",

    'summary': """
        智能装配行业扩展模块""",

    'description': """
        智能装配行业扩展模块
    """,

    'author': "上海文享信息科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '14.0.10.1',

    # any module necessary for this one to work correctly
    'depends': ['onesphere_mdm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_category_data.xml',
        'data/quality_data.xml',
        'data/tightening_data.xml',
        'views/tightening_unit_views.xml',
        'views/mdm_menu_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/tightening_vendor_data.xml',
        'demo/tightening_unit_demo.xml',
    ],
}
