# -*- coding: utf-8 -*-
{
    'name': 'CPK 銷售折扣方案管理',
    'version': '0.0.1',
    'category': 'Sales',
    'summary': '牡蠣搭售折扣方案管理系統',
    'description': """
        CPK 銷售折扣方案管理系統
        ========================
        
        專為解決牡蠣肉搭售促銷需求而設計的完整折扣方案管理系統。
        
        主要功能：
        --------
        * 搭售折扣規則設定 - 主商品搭配多種商品組合
        * 階梯式定價機制 - 購買數量越多折扣越大
        * 價格檔整合功能 - 批次套用到現有價格檔案
        * 自動折扣計算 - 訂單儲存時自動套用最優折扣
        * 多重方案比較 - 自動選擇最優惠的折扣方案
        * 完整報表分析 - 折扣效益與銷售分析
        
        業務場景：
        --------
        * 牡蠣肉為稀缺主商品，需搭配其他商品銷售
        * 支援 A、B、C、D 多種商品組合方案
        * 階梯式數量級距與對應折扣設定
        * 自動記錄每筆訂單使用的具體折扣方案
        
        技術特色：
        --------
        * 可擴展的架構設計，支援未來多種折扣類型
        * 完整的價格檔整合機制
        * 自動化的訂單折扣計算引擎
        * 豐富的權限控制與安全機制
    """,
    'author': 'Cympotek',
    'website': 'https://www.cympotek.com',
    'license': 'LGPL-3',
    
    'depends': [
        'base',
        'sale',
        'product',
        'sale_management',
    ],
    
    'data': [
        # 安全權限
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # 初始資料
        'data/cpk_discount_scheme_type_data.xml',
        'data/ir_sequence_data.xml',
        
        # 視圖檔案
        'views/cpk_discount_scheme_views.xml',
        'views/cpk_bundle_discount_views.xml',
        'views/pricelist_integration_views.xml',
        'views/sale_order_views.xml',
        'views/menus.xml',
        
        # 精靈檔案
        'wizards/pricelist_apply_wizard_views.xml',
        
        # 報表檔案
        'reports/discount_analysis_views.xml',
    ],
    
    'demo': [
        # 示範資料可在此加入
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    
    'external_dependencies': {
        'python': [],
    },
}