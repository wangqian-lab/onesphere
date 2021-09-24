# -*- coding: utf-8 -*-
{
    'name': "onesphere_core",

    'summary': """
        MOM 核心模块""",

    'description': """
        Long description of module's purpose
    """,

    'author': "上海文享信息科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/base_groups.xml',
        'views/res_users_views.xml',
    ],
    'post_init_hook': '_onesphere_core_post_init',
    'auto_install': False
}
