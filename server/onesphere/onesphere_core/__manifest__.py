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
    'version': '14.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'security/onesphere_core_rules.xml',
        'security/ir.model.access.csv',
        'data/resource_data.xml',
        'data/base_groups.xml',
        'data/operation_type_data.xml',
        'data/quality_data.xml',
        'data/hmi_user_role_data.xml',
        'views/quality_views.xml',
        'views/res_users_views.xml',
        'views/res_config_settings_views.xml',
        'views/mrp_routing_workcenter_views.xml',
    ],
    'demo': [
        # 'demo/track_code_demo.xml',
    ],
    'post_init_hook': '_onesphere_core_post_init',
    'uninstall_hook': '_oneshare_core_uninstall_hook',
    'auto_install': False
}
