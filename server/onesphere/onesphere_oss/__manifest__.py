# -*- coding: utf-8 -*-
{
    'name': "onesphere_oss",

    'summary': """
        Onesphere对象存储支持模块""",

    'description': """
        Onesphere对象存储支持模块
    """,

    'author': "Oneshare",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '14.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base_setup'],

    'external_dependencies': {
        'python': ['minio', 'urllib3'],
    },

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ]
}
