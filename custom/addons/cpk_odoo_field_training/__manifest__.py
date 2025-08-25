# -*- coding: utf-8 -*-
{
    'name': "Odoo 欄位類型教育訓練",

    'summary': """
        Odoo 16 所有欄位類型演示與教學模組""",

    'description': """
        Odoo 欄位類型教育訓練模組，包含：
        
        基本欄位類型:
        - Char: 短文字字符串
        - Text: 長文字內容
        - Integer: 整數數值
        - Float: 浮點數數值
        - Boolean: 布林值
        - Date: 日期
        - Datetime: 日期時間
        - Selection: 選項清單
        - Binary: 二進位檔案
        - Image: 圖片檔案

        關係欄位類型:
        - Many2one: 多對一關聯
        - One2many: 一對多關聯
        - Many2many: 多對多關聯

        進階欄位類型:
        - Monetary: 貨幣金額
        - Html: HTML 內容
        - Related: 關聯欄位
        - Reference: 動態參考
        - Json: JSON 資料
        - Properties: 屬性欄位

        每種欄位都包含：
        - Tree view 顯示效果
        - Form view 顯示效果
        - 不同 widget 的使用範例
        - 詳細的使用說明
    """,

    'author': "Cympotek",
    'website': "https://www.cympotek.com",

    'category': 'Education',
    'version': 'saas~16.4.1.0',
    'license': 'LGPL-3',

    # 模組依賴
    'depends': ['base', 'hr', 'account', 'project', 'mail'],

    # 載入的資料檔案
    'data': [
        'security/ir.model.access.csv',
        'views/training_views.xml',
        'reports/field_training_reports.xml',
        'wizard/field_training_report_wizard_views.xml',
        'views/menus.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}