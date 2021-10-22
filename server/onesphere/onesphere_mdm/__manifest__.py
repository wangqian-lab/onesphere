# -*- coding: utf-8 -*-
{
    'name': "onesphere_mdm",

    'summary': """
    MOM主数据管理模块
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "上海文享信息科技有限公司",
    'website': "http://www.oneshare.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '14.0.10.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'maintenance', 'onesphere_core'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/work_area_category_data.xml',
        'data/maintenance_category_data.xml',
        'views/assets.xml',
        'views/maintenance_views.xml',
        'views/product_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_routing_workcenter_views.xml',
        'views/work_area_views.xml',
        'views/mrp_workcenter_group_views.xml',
        'views/mdm_menu_views.xml',
    ],
    'demo': [
        'data/mrp_demo.xml',
    ],
}
