# -*- coding: utf-8 -*-
{
    'name': "費用請款單",

    'summary': """
        費用請款單管理系統""",

    'description': """
        費用請款單管理系統，包含：
        - 請款單據管理
        - 憑證資料處理
        - 請款明細管理
        - 費用類別設定
        - 稅別設定
        - 權限控制
    """,

    'author': "Cympotek",
    'website': "https://www.cympotek.com",

    'category': 'Accounting',
    'version': 'saas~16.4.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'account', 'hr_expense'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/expense_category_data.xml',
        'views/expense_category_views.xml',
        'views/tax_code_views.xml',
        'views/payment_method_views.xml',
        'views/reimburse_views.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

