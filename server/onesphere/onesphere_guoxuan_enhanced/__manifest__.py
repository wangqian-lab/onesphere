# -*- coding: utf-8 -*-
{
    'name': "onesphere_guoxuan_enhanced",

    'summary': """
    国轩模块-TS039
        """,

    'description': """
        国轩模块-TS039
    """,

    'author': "上海文享信息科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': 'TS039',

    # any module necessary for this one to work correctly
    'depends': ['onesphere_assembly_industry'],

    # always loaded
    'data': [
        'data/work_step_tag_data.xml',
        'views/quality_views.xml',
        'views/res_company_views.xml',
    ],
    'demo': [
    ],

}
