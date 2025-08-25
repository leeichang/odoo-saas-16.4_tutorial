# CPK 銷售折扣方案管理系統

**版本**: 16.0.1.0.0  
**作者**: Cympotek  
**授權**: LGPL-3

## 🎯 專案概述

CPK 銷售折扣方案管理系統是專為解決牡蠣肉搭售促銷需求而設計的完整折扣方案管理模組。系統支援複雜的搭售規則設定、階梯式定價機制，以及與現有價格檔的無縫整合。

### 核心業務場景

根據您提供的牡蠣銷售價格方案（圖片中的 A、B、C、D 組合），本系統解決以下業務需求：

- **稀缺商品促銷**：牡蠣肉為主商品，必須搭配其他商品銷售
- **庫存去化**：透過搭售機制促銷庫存商品
- **階梯式優惠**：購買數量越多，折扣越大
- **組合商品銷售**：支援多種商品組合方案
- **價格檔整合**：自動套用到現有的客戶價格檔案

## 🏗️ 系統架構

### 模組結構

```
cpk_sale_discount_scheme/
├── __manifest__.py                      # 模組清單檔
├── README.md                           # 本檔案 - 完整規劃說明
├── models/                             # 資料模型
│   ├── cpk_discount_scheme.py          # 折扣方案主檔
│   ├── cpk_discount_scheme_type.py     # 方案類型定義
│   ├── cpk_bundle_discount_rule.py     # 搭售折扣規則
│   ├── cpk_bundle_product_line.py      # 搭售商品明細
│   ├── cpk_bundle_tier.py             # 階梯式數量級距
│   ├── product_pricelist.py           # 擴展價格檔功能
│   └── sale_order.py                  # 擴展銷售訂單功能
├── views/                              # 使用者介面
│   ├── cpk_discount_scheme_views.xml   # 主要方案管理介面
│   ├── cpk_bundle_discount_views.xml   # 搭售規則設定介面
│   ├── pricelist_integration_views.xml # 價格檔整合介面
│   ├── sale_order_views.xml           # 訂單折扣資訊顯示
│   ├── menus.xml                       # 選單結構定義
│   └── reports.xml                     # 報表分析介面
├── wizards/                           # 精靈程式
│   ├── pricelist_apply_wizard.py      # 批次套用價格檔精靈
│   └── pricelist_apply_wizard_views.xml
├── data/                              # 初始資料
│   ├── cpk_discount_scheme_type_data.xml # 預設折扣方案類型
│   └── ir_sequence_data.xml           # 自動編號設定
└── security/                          # 安全權限
    ├── security.xml                   # 使用者群組定義
    └── ir.model.access.csv           # 模型存取權限
```

## 📊 資料模型設計

### 核心模型關係圖

```
┌─────────────────────────┐
│   cpk.discount.scheme   │ ◄──┐
│      (折扣方案主檔)        │    │
└─────────────────────────┘    │
             │                │
             │ 1:N            │ N:M
             ▼                │
┌─────────────────────────┐    │
│ cpk.bundle.discount.rule│    │
│     (搭售折扣規則)        │    │
└─────────────────────────┘    │
         │           │        │
         │ 1:N       │ 1:N    │
         ▼           ▼        │
┌──────────────┐ ┌──────────────┐
│cpk.bundle.   │ │cpk.bundle.   │
│product.line  │ │tier          │
│(搭售商品明細) │ │(數量級距)     │
└──────────────┘ └──────────────┘
                            │
                            │
              ┌─────────────────────────┐
              │  product.pricelist      │
              │     (價格檔整合)         │
              └─────────────────────────┘
```

### 1. 折扣方案主檔 (`cpk.discount.scheme`)

**用途**：管理所有折扣方案的主要資訊

**核心欄位**：
- `name`: 方案名稱 (例如：「牡蠣搭售促銷方案」)
- `code`: 方案代碼 (自動編號：DS202412001)
- `scheme_type_id`: 方案類型 (搭售折扣、數量折扣等)
- `priority`: 優先順序 (多方案時選擇最優惠)
- `date_start/date_end`: 有效期間
- `pricelist_ids`: 適用價格檔 (M2M)
- `partner_ids`: 適用客戶 (M2M)
- `state`: 狀態 (草稿/啟用/停用)

**業務邏輯**：
```python
def is_applicable(self, order):
    """檢查方案是否適用於訂單"""
    # 檢查時間範圍、價格檔、客戶等條件
    pass
```

### 2. 搭售折扣規則 (`cpk.bundle.discount.rule`)

**用途**：設定具體的搭售規則和條件

**核心欄位**：
- `main_product_id`: 主商品 (牡蠣肉)
- `bundle_selection_type`: 搭售條件類型
  - `all_required`: 全部必選
  - `min_quantity`: 最少選購數量
  - `min_amount`: 最少選購金額
  - `min_products`: 最少選購品項數
- `bundle_product_ids`: 搭售商品清單 (O2M)
- `tier_ids`: 數量級距設定 (O2M)

**範例設定** (對應您的價格方案)：
```
主商品：牡蠣肉 (1KG包裝)
搭售條件：最少選購 2 個不同商品組合
搭售商品：
- A 組：商品 A1, A2, A3
- B 組：商品 B1, B2, B3  
- C 組：商品 C1, C2, C3
- D 組：商品 D1, D2, D3
```

### 3. 搭售商品明細 (`cpk.bundle.product.line`)

**用途**：定義每個搭售商品的具體條件

**核心欄位**：
- `product_id`: 搭售商品
- `product_group`: 商品組別 (A、B、C、D)
- `is_required`: 是否必選
- `min_qty/max_qty`: 數量限制
- `group_min_select`: 組內最少選擇品項

**範例資料**：
```
商品組 A：
- 商品 A1 (最少 1 個，非必選)
- 商品 A2 (最少 1 個，非必選)
- 商品 A3 (最少 1 個，非必選)
- 組內條件：至少選 1 個商品
```

### 4. 數量級距設定 (`cpk.bundle.tier`)

**用途**：設定階梯式定價規則

**核心欄位**：
- `min_main_qty/max_main_qty`: 主商品數量範圍
- `main_discount_type/value`: 主商品折扣類型和值
- `bundle_discount_type/value`: 搭售商品折扣類型和值

**對應您的價格方案**：
```
級距 1：購買 1-4 包牡蠣肉
- 主商品：8 折 (20% 折扣)
- 搭售商品：9 折 (10% 折扣)

級距 2：購買 5-9 包牡蠣肉  
- 主商品：7.5 折 (25% 折扣)
- 搭售商品：8.5 折 (15% 折扣)

級距 3：購買 10+ 包牡蠣肉
- 主商品：7 折 (30% 折扣)
- 搭售商品：8 折 (20% 折扣)
```

## 🎮 核心功能詳解

### 1. 折扣方案設定流程

#### Step 1: 建立折扣方案
```
選單：折扣方案管理 > 折扣方案 > 建立

設定內容：
- 方案名稱：牡蠣搭售促銷 2024Q4
- 方案類型：搭售折扣
- 有效期間：2024/10/01 - 2024/12/31
- 適用客戶：(可選特定客戶或全部)
- 適用價格檔：(可選特定價格檔或全部)
```

#### Step 2: 設定搭售規則
```
在折扣方案中新增搭售規則：

規則名稱：牡蠣肉組合方案
主商品：牡蠣肉 (1KG 裝)
搭售條件：最少選購 2 個不同品項

搭售商品設定：
┌─────────┬─────────┬─────────┬─────────┐
│ 商品組 A │ 商品組 B │ 商品組 C │ 商品組 D │
├─────────┼─────────┼─────────┼─────────┤
│ 商品 A1  │ 商品 B1  │ 商品 C1  │ 商品 D1  │
│ 商品 A2  │ 商品 B2  │ 商品 C2  │ 商品 D2  │
│ 商品 A3  │ 商品 B3  │ 商品 C3  │ 商品 D3  │
└─────────┴─────────┴─────────┴─────────┘
每組至少選 1 個商品，總共至少選 2 組
```

#### Step 3: 設定數量級距
```
級距設定對應您的價格表：

級距 1：1-4 包
- 主商品折扣：20%
- 搭售商品折扣：10%

級距 2：5-9 包  
- 主商品折扣：25%
- 搭售商品折扣：15%

級距 3：10+ 包
- 主商品折扣：30%
- 搭售商品折扣：20%
```

### 2. 價格檔整合機制

#### 批次套用流程
```
選單：折扣方案管理 > 價格檔整合 > 批次套用價格檔

操作步驟：
1. 選擇要套用的折扣方案
2. 選擇目標價格檔 (可選特定或全部)
3. 設定套用選項：
   - 更新現有項目 ✓
   - 移除過期項目 ✓
4. 預覽變更內容
5. 執行批次套用

系統會自動：
- 為每個級距建立對應的價格項目
- 設定最少購買數量條件
- 標記項目來源為折扣方案
- 建立價格檔與方案的關聯
```

#### 自動產生的價格項目範例
```
價格檔：一般客戶價格檔

新增項目：
┌──────────┬──────────┬──────────┬──────────┐
│   商品    │ 最少數量  │ 折扣類型  │  折扣值   │
├──────────┼──────────┼──────────┼──────────┤
│ 牡蠣肉    │    1     │ 百分比   │   20%    │
│ 牡蠣肉    │    5     │ 百分比   │   25%    │  
│ 牡蠣肉    │   10     │ 百分比   │   30%    │
│ 商品 A1   │    1     │ 百分比   │   10%    │
│ 商品 A2   │    1     │ 百分比   │   10%    │
│   ...     │   ...    │   ...    │   ...    │
└──────────┴──────────┴──────────┴──────────┘
```

### 3. 訂單自動折扣計算

#### 計算引擎邏輯
```python
def _apply_discount_schemes(self):
    """訂單確認時自動套用折扣"""
    
    # 1. 取得適用的折扣方案 (按優先順序排列)
    applicable_schemes = self._get_applicable_discount_schemes()
    
    # 2. 逐一檢查並套用最優方案
    for scheme in applicable_schemes:
        if self._apply_bundle_discount(scheme):
            break  # 套用成功即停止
    
    # 3. 記錄套用結果
    self._log_discount_application()
```

#### 搭售條件檢查
```python
def check_bundle_conditions(self, main_lines, bundle_lines):
    """檢查是否滿足搭售條件"""
    
    # 檢查主商品
    if not main_lines:
        return False
        
    # 檢查搭售條件
    if self.bundle_selection_type == 'min_products':
        # 檢查是否選購足夠的不同品項
        unique_products = len(set(bundle_lines.mapped('product_id.id')))
        return unique_products >= self.min_bundle_products
    
    # 其他條件檢查...
    return True
```

#### 自動折扣套用範例
```
客戶訂單內容：
- 牡蠣肉 1KG × 6 包 = $300/包
- 商品 A1 × 2 個 = $50/個  
- 商品 C2 × 1 個 = $80/個

系統自動判斷：
✓ 主商品：牡蠣肉 6 包 (符合級距 2: 5-9 包)
✓ 搭售商品：A1 + C2 = 2 個不同品項 (符合最少 2 品項條件)

自動套用折扣：
- 牡蠣肉：原價 $300 → 折扣 25% → 實售 $225
- 商品 A1：原價 $50 → 折扣 15% → 實售 $42.5  
- 商品 C2：原價 $80 → 折扣 15% → 實售 $68

訂單明細會記錄：
- 套用方案：牡蠣搭售促銷 2024Q4
- 套用規則：牡蠣肉組合方案
- 套用級距：級距 2 (5-9 包)
```

### 4. 多重方案競爭機制

當訂單符合多個折扣方案時，系統會：

```python
def _select_best_discount(self, applicable_schemes):
    """選擇最優惠的折扣方案"""
    
    best_scheme = None
    best_total_discount = 0
    
    for scheme in applicable_schemes:
        # 計算該方案的總折扣金額
        total_discount = self._calculate_total_discount(scheme)
        
        if total_discount > best_total_discount:
            best_scheme = scheme
            best_total_discount = total_discount
    
    return best_scheme
```

**優先順序規則**：
1. **優先順序數值**：數值越高優先權越高
2. **實際折扣金額**：選擇折扣金額最大的方案
3. **方案建立時間**：相同條件下選擇較新的方案

## 🔧 安裝與設定

### 系統需求
- Odoo 16.0+
- Python 3.8+
- PostgreSQL 12+

### 依賴模組
- `base` - Odoo 基礎框架
- `sale` - 銷售管理
- `product` - 商品管理  
- `sale_management` - 銷售管理進階功能

### 安裝步驟

#### 1. 模組安裝
```bash
# 1. 將模組複製到 addons 目錄
cp -r cpk_sale_discount_scheme /path/to/odoo/addons/

# 2. 更新應用程式列表
# 在 Odoo 後台：設定 > 技術 > 應用程式 > 更新應用程式列表

# 3. 搜尋並安裝「CPK 銷售折扣方案管理」
```

#### 2. 權限設定
```
使用者權限設定：

折扣方案管理員：
- 可建立、修改、刪除所有折扣方案
- 可執行批次價格檔套用
- 可查看所有分析報表

折扣方案使用者：
- 可查看折扣方案 (唯讀)
- 可在訂單中看到折扣資訊
- 可查看基本分析報表

一般使用者：
- 訂單會自動套用折扣
- 可在訂單中看到折扣明細
```

#### 3. 初始設定

**A. 建立折扣方案類型** (已預設建立)
- 搭售折扣
- 數量折扣  
- 季節性折扣
- 忠誠度折扣

**B. 設定商品資料**
```
確保您的商品資料完整：
- 牡蠣肉商品已建立
- 搭售商品 (A、B、C、D 組) 已建立
- 商品分類設定完成
- 價格資料正確
```

**C. 設定價格檔**
```
確認現有價格檔設定：
- 一般客戶價格檔
- VIP 客戶價格檔
- 批發客戶價格檔
```

### 快速開始指南

#### 第一個牡蠣搭售方案

**Step 1: 建立折扣方案**
```
選單：折扣方案管理 > 折扣方案 > 建立

填寫資訊：
- 方案名稱：牡蠣搭售促銷測試
- 方案類型：搭售折扣
- 優先順序：10
- 開始日期：今天
- 結束日期：一個月後
```

**Step 2: 建立搭售規則**
```
在方案中新增規則：
- 規則名稱：測試規則
- 主商品：選擇您的牡蠣商品
- 搭售條件：最少選購品項數 = 2

新增搭售商品：
- 隨意選擇 4-6 個商品作為搭售商品
- 設定商品組別：A、B、C、D
```

**Step 3: 設定級距**
```
新增數量級距：
- 級距 1：1-4 包，主商品 15% 折扣，搭售商品 10% 折扣
- 級距 2：5+ 包，主商品 20% 折扣，搭售商品 15% 折扣
```

**Step 4: 啟用方案**
```
點擊「啟用」按鈕，狀態變更為「啟用」
```

**Step 5: 測試訂單**
```
建立銷售訂單：
- 選擇客戶
- 新增牡蠣商品 6 包  
- 新增 2 個不同的搭售商品
- 確認訂單

檢查結果：
- 訂單明細應顯示對應的折扣
- 折扣資訊頁籤顯示套用的方案資訊
```

## 📈 報表與分析

### 折扣效益分析

**樞紐分析表**：
- **列分組**：折扣方案、月份
- **欄分組**：客戶類型、銷售人員  
- **度量**：銷售金額、折扣金額、訂單數量

**圖表分析**：
- 折扣方案使用趨勢圖
- 各方案折扣效益對比
- 客戶接受度分析

### 搭售效果追蹤

**搭售成功率分析**：
```sql
-- 搭售成功率計算
SELECT 
    ds.name as scheme_name,
    COUNT(DISTINCT sol.order_id) as total_orders,
    COUNT(DISTINCT CASE 
        WHEN sol.is_bundle_main_product = true 
        THEN sol.bundle_group_id 
    END) as bundle_success_count,
    ROUND(
        COUNT(DISTINCT CASE WHEN sol.is_bundle_main_product = true THEN sol.bundle_group_id END) * 100.0 / 
        COUNT(DISTINCT sol.order_id), 2
    ) as success_rate
FROM sale_order_line sol
JOIN cpk_discount_scheme ds ON sol.applied_discount_scheme_id = ds.id  
GROUP BY ds.name;
```

**商品搭售分析**：
- 哪些商品組合最受歡迎
- 各商品組的銷售貢獻度
- 庫存去化效果分析

## 🔄 擴展開發指南

### 新增折扣類型

本系統採用可擴展的架構設計，支援未來新增多種折扣類型。

#### 1. 建立新的折扣引擎

```python
# models/discount_engine_volume.py
class VolumeDiscountEngine(models.Model):
    _name = 'cpk.discount.engine.volume'
    _description = '數量折扣引擎'
    
    def apply_discount(self, order, scheme):
        """實作數量折扣邏輯"""
        # 實作邏輯...
        pass
    
    def validate_conditions(self, order, rule):
        """驗證數量折扣條件"""
        # 驗證邏輯...
        pass
```

#### 2. 擴展規則模型

```python  
# models/volume_discount_rule.py
class VolumeDiscountRule(models.Model):
    _name = 'cpk.volume.discount.rule'
    _description = '數量折扣規則'
    
    scheme_id = fields.Many2one('cpk.discount.scheme')
    product_id = fields.Many2one('product.product')
    volume_tiers = fields.One2many('cpk.volume.tier', 'rule_id')
```

#### 3. 註冊折扣類型

```xml
<!-- data/new_discount_types.xml -->
<record id="scheme_type_volume_discount" model="cpk.discount.scheme.type">
    <field name="name">數量折扣</field>
    <field name="code">volume_discount</field>
    <field name="engine_class">cpk.discount.engine.volume</field>
</record>
```

### API 整合範例

#### REST API 端點

```python
# controllers/api.py
from odoo import http
from odoo.http import request

class DiscountSchemeAPI(http.Controller):
    
    @http.route('/api/discount/schemes', type='json', auth='user')
    def get_applicable_schemes(self, partner_id, product_ids):
        """取得適用的折扣方案"""
        # API 邏輯實作...
        pass
    
    @http.route('/api/discount/calculate', type='json', auth='user')  
    def calculate_discount(self, order_data):
        """計算訂單折扣"""
        # 計算邏輯實作...
        pass
```

### 第三方系統整合

#### Webhook 通知

```python
# models/discount_webhook.py  
class DiscountWebhook(models.Model):
    _name = 'cpk.discount.webhook'
    _description = '折扣方案 Webhook'
    
    def notify_scheme_applied(self, order, scheme):
        """通知外部系統折扣方案已套用"""
        payload = {
            'order_id': order.id,
            'scheme_id': scheme.id,
            'discount_amount': order.amount_total - order.amount_untaxed,
            'timestamp': fields.Datetime.now().isoformat()
        }
        
        # 發送 HTTP 請求到外部系統
        requests.post(self.webhook_url, json=payload)
```

## 🚀 效能優化建議

### 資料庫優化

#### 1. 索引優化
```sql
-- 建立複合索引加速查詢
CREATE INDEX idx_sale_order_line_discount_scheme 
ON sale_order_line (applied_discount_scheme_id, order_id);

CREATE INDEX idx_bundle_product_line_rule_product
ON cpk_bundle_product_line (rule_id, product_id);
```

#### 2. 查詢優化
```python
# 使用批次載入避免 N+1 查詢
schemes = self.env['cpk.discount.scheme'].search(domain)
schemes.mapped('bundle_rule_ids.bundle_product_ids.product_id')
```

### 快取機制

```python
# 使用 Odoo 內建快取
from odoo.tools import ormcache

class CpkDiscountScheme(models.Model):
    _name = 'cpk.discount.scheme'
    
    @ormcache('self.id', 'partner_id')
    def _get_applicable_rules_cached(self, partner_id):
        """快取適用規則查詢結果"""
        # 查詢邏輯...
        pass
```

### 背景任務

```python
# 使用佇列處理大批量價格檔更新
from odoo.addons.queue_job.job import job

class PricelistApplyWizard(models.TransientModel):
    _name = 'cpk.pricelist.apply.wizard'
    
    @job  
    def _async_apply_to_pricelists(self, pricelist_ids):
        """背景執行批次套用"""
        # 處理邏輯...
        pass
```

## ⚠️ 注意事項與限制

### 使用限制

1. **商品數量限制**：單一規則建議不超過 100 個搭售商品
2. **級距數量限制**：單一規則建議不超過 20 個數量級距  
3. **方案數量限制**：同時啟用的方案建議不超過 50 個
4. **計算複雜度**：複雜的搭售條件會影響訂單確認速度

### 效能考量

1. **大量訂單處理**：建議在低峰時段執行批次價格檔套用
2. **快取策略**：系統會快取常用的折扣計算結果
3. **資料庫維護**：定期清理過期的折扣記錄
4. **並發處理**：多使用者同時修改方案時可能出現衝突

### 資料一致性

1. **價格檔同步**：修改折扣方案後需重新套用到價格檔
2. **訂單歷史**：已確認的訂單折扣不會因方案變更而改變
3. **刪除保護**：使用中的折扣方案無法直接刪除
4. **權限控制**：確保只有授權人員可修改關鍵設定

## 🆘 常見問題 FAQ

### Q1: 為什麼訂單沒有自動套用折扣？

**檢查清單**：
1. ✅ 折扣方案是否已啟用？
2. ✅ 訂單日期是否在方案有效期內？
3. ✅ 客戶是否在適用範圍內？
4. ✅ 價格檔是否關聯到方案？
5. ✅ 是否滿足搭售條件？
6. ✅ 主商品數量是否符合級距要求？

**解決方法**：
```python
# 在訂單中手動觸發折扣計算
order.action_recalculate_discounts()
```

### Q2: 如何處理折扣方案衝突？

**衝突情況**：多個方案都適用於同一訂單

**系統處理邏輯**：
1. 按優先順序排序方案
2. 計算每個方案的實際折扣金額
3. 自動選擇折扣金額最大的方案
4. 在訂單中記錄選擇原因

**手動處理**：
```python
# 重置所有折扣後手動選擇
order.action_reset_discounts()
# 手動套用特定方案
scheme.apply_to_order(order)
```

### Q3: 如何批次更新現有訂單的折扣？

**注意**：建議只對草稿狀態的訂單進行批次更新

**操作步驟**：
```python
# 找到需要更新的訂單
draft_orders = self.env['sale.order'].search([
    ('state', '=', 'draft'),
    ('create_date', '>=', '2024-10-01'),
])

# 批次重新計算折扣
for order in draft_orders:
    order.action_recalculate_discounts()
```

### Q4: 如何匯出折扣使用報表？

**內建報表**：
- 選單：折扣方案管理 > 報表分析 > 折扣效益分析
- 支援 Excel 匯出功能

**自訂報表**：
```sql
SELECT 
    so.name as order_number,
    rp.name as customer,
    ds.name as discount_scheme,
    sol.product_id,
    sol.product_uom_qty,
    sol.price_unit,
    sol.discount,
    sol.price_subtotal
FROM sale_order_line sol
JOIN sale_order so ON sol.order_id = so.id
JOIN res_partner rp ON so.partner_id = rp.id  
JOIN cpk_discount_scheme ds ON sol.applied_discount_scheme_id = ds.id
WHERE sol.applied_discount_scheme_id IS NOT NULL;
```

## 📞 技術支援

### 支援管道

- **官方網站**：https://www.cympotek.com
- **技術文件**：請參考本 README.md
- **問題回報**：請透過 Odoo 後台的問題追蹤功能

### 版本更新

**版本命名規則**：`16.0.Major.Minor.Patch`

**更新建議**：
1. 在測試環境先進行更新測試
2. 備份現有的折扣方案設定
3. 檢查客製化程式碼相容性
4. 更新後重新測試關鍵業務流程

---

## 📋 附錄

### A. 資料庫欄位清單

#### 折扣方案主檔 (cpk_discount_scheme)
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| name | Char | ✓ | 方案名稱 |
| code | Char |  | 方案代碼 (自動產生) |
| scheme_type_id | Many2one | ✓ | 方案類型 |
| active | Boolean |  | 是否啟用 |
| priority | Integer |  | 優先順序 |
| date_start | Date |  | 開始日期 |
| date_end | Date |  | 結束日期 |
| company_id | Many2one |  | 公司 |
| state | Selection |  | 狀態 |

#### 搭售折扣規則 (cpk_bundle_discount_rule)  
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| scheme_id | Many2one | ✓ | 所屬折扣方案 |
| name | Char | ✓ | 規則名稱 |
| main_product_id | Many2one | ✓ | 主商品 |
| bundle_selection_type | Selection | ✓ | 搭售條件類型 |
| min_bundle_qty | Float |  | 最少搭售數量 |
| min_bundle_amount | Monetary |  | 最少搭售金額 |
| min_bundle_products | Integer |  | 最少搭售品項數 |

### B. API 參考

#### 折扣計算 API
```python
# 計算訂單可用的折扣方案
applicable_schemes = order._get_applicable_discount_schemes()

# 套用特定折扣方案
scheme.apply_to_order(order)

# 計算折扣金額
discount_amount = tier.calculate_discount_rate(price, discount_type, discount_value)
```

#### 事件觸發
```python
# 折扣方案套用事件
@api.model  
def _discount_scheme_applied(self, order, scheme):
    """折扣方案套用後的回調函數"""
    pass

# 價格檔更新事件
@api.model
def _pricelist_items_updated(self, pricelist, scheme):
    """價格檔項目更新後的回調函數"""  
    pass
```

### C. 設定檔範例

#### 環境變數設定
```bash
# .env 檔案
DISCOUNT_CALCULATION_TIMEOUT=30
DISCOUNT_CACHE_EXPIRY=3600
DISCOUNT_MAX_CONCURRENT_ORDERS=10
```

#### 系統參數設定
```xml
<!-- data/system_parameters.xml -->
<record id="discount_max_rules_per_scheme" model="ir.config_parameter">
    <field name="key">discount.max_rules_per_scheme</field>
    <field name="value">50</field>
</record>
```

---

**© 2024 Cympotek. All rights reserved.**

*本文檔最後更新：2024年12月24日*