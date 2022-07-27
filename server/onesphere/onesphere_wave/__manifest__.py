# -*- coding: utf-8 -*-
{
    'name': "onesphere_wave",

    'summary': """
        曲线查看模块""",

    'description': """
        Long description of module's purpose
    """,

    'author': "上海文享数据科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'web_echarts', 'base', 'web_notify', 'onesphere_assembly_industry'],

    "external_dependencies": {
        "python": ['minio'],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/operation_result_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/wave_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # only loaded in demonstration mode
}
