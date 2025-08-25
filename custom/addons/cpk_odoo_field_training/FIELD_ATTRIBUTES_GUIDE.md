# Odoo 欄位屬性完整指南

## 功能概述

我已經為 `cpk_odoo_field_training` 模組新增了完整的欄位屬性展示功能，透過 `cpk.field.attribute.demo` 模型展示所有 Odoo 欄位屬性的實際使用方式。

## 新增的模型和視圖

### 🎯 **新模型：cpk.field.attribute.demo**
專門用於展示所有 Odoo 欄位屬性的教學模型，包含：
- 繼承 `mail.thread` 和 `mail.activity.mixin`
- 演示所有欄位屬性的實際用法
- 包含驗證約束和計算欄位

### 📋 **完整視圖系統**
- **Tree View**: 展示主要欄位和屬性效果
- **Form View**: 分組展示不同類型的屬性
- **Search View**: 提供過濾和群組功能
- **選單整合**: 新增「欄位屬性展示」選單項目

## 欄位屬性分類展示

### 🔤 **基本屬性 (Basic Attributes)**

| 屬性 | 展示欄位 | 說明 | 程式碼範例 |
|------|----------|------|------------|
| **string** | `name` | 欄位顯示標籤 | `string='名稱 (string 屬性)'` |
| **required** | `required_field` | 必填欄位 | `required=True` |
| **readonly** | `readonly_field` | 唯讀欄位 | `readonly=True` |
| **default** | `default_fixed`, `default_function` | 預設值設定 | `default='預設文字'` or `default=fields.Datetime.now` |
| **help** | `help_demo` | 工具提示說明 | `help='這裡是說明文字'` |
| **index** | `indexed_code` | 資料庫索引 | `index=True` |
| **copy** | `copy_field`, `no_copy_field` | 複製行為控制 | `copy=False` |
| **groups** | `admin_only_field`, `user_field` | 權限群組控制 | `groups='base.group_system'` |

### 🧮 **計算欄位屬性 (Computed Field Attributes)**

| 屬性 | 展示欄位 | 說明 | 程式碼範例 |
|------|----------|------|------------|
| **compute** | `total_amount` | 動態計算 | `compute='_compute_total_amount'` |
| **store** | `stored_total` | 儲存計算結果 | `compute='_compute_total_amount', store=True` |
| **inverse** | `editable_total` | 可編輯計算欄位 | `inverse='_inverse_editable_total'` |
| **depends** | 計算方法裝飾器 | 依賴欄位定義 | `@api.depends('quantity', 'unit_price')` |

### 🔗 **關係欄位屬性 (Relational Field Attributes)**

| 屬性 | 展示欄位 | 說明 | 程式碼範例 |
|------|----------|------|------------|
| **related** | `partner_email`, `partner_phone` | 關聯欄位值 | `related='partner_id.email'` |
| **domain** | `company_partner` | 選擇範圍限制 | `domain=[('is_company', '=', True)]` |
| **context** | `new_partner` | 上下文傳遞 | `context={'default_is_company': True}` |
| **ondelete** | `category_id` | 刪除行為控制 | `ondelete='set null'` |

### ⚙️ **特殊屬性 (Special Attributes)**

| 屬性 | 展示欄位 | 說明 | 程式碼範例 |
|------|----------|------|------------|
| **digits** | `precise_amount` | 浮點數精度 | `digits=(16, 4)` |
| **selection** | `status` | 選項清單 | `[('draft', '草稿'), ('done', '完成')]` |
| **translate** | `translatable_name` | 多語言支援 | `translate=True` |
| **size** | `short_code` | 字符長度限制 | `size=5` |
| **tracking** | `tracked_field`, `status` | 變更追蹤 | `tracking=True` |

### 🎭 **動態屬性 (Dynamic Attributes via attrs)**

展示如何使用 `attrs` 在視圖中實現條件式控制：

```xml
<!-- 動態必填 -->
<field name="dynamic_required" 
       attrs="{'required': [('condition_field', '=', True)]}"/>

<!-- 動態唯讀 -->
<field name="dynamic_readonly" 
       attrs="{'readonly': [('condition_field', '=', True)]}"/>

<!-- 動態隱藏 -->
<field name="dynamic_invisible" 
       attrs="{'invisible': [('condition_field', '=', True)]}"/>
```

## 實際應用範例

### 🔄 **計算欄位完整範例**
```python
@api.depends('quantity', 'unit_price')
def _compute_total_amount(self):
    for record in self:
        record.total_amount = record.quantity * record.unit_price
        record.stored_total = record.quantity * record.unit_price
        record.editable_total = record.quantity * record.unit_price

def _inverse_editable_total(self):
    for record in self:
        if record.quantity and record.editable_total:
            record.unit_price = record.editable_total / record.quantity
```

### 🔐 **權限控制範例**
```python
admin_only_field = fields.Char(
    string='僅管理員可見', 
    groups='base.group_system',
    help='只有系統管理員可以看到這個欄位'
)
```

### 🌐 **關聯欄位範例**
```python
partner_email = fields.Char(
    string='客戶信箱', 
    related='partner_id.email',
    readonly=True,
    help='自動從客戶記錄中取得信箱地址'
)
```

## 選單結構

更新後的選單結構：
```
欄位類型訓練 (主選單)
├── 欄位類型演示 (原有功能)
├── 欄位屬性展示 (新功能) ⭐
└── 設定
    └── 欄位類型說明
```

## 教學價值

### 📚 **學習目標**
- 理解所有 Odoo 欄位屬性的用途和用法
- 掌握計算欄位的完整實作方式
- 學會使用 attrs 實現動態視圖控制
- 了解關係欄位的進階屬性設定

### 🎯 **實用功能**
- **互動學習**：每個屬性都可以實際操作體驗
- **即時反饋**：修改值立即看到效果
- **完整註解**：每個欄位都有詳細的 help 說明
- **實際案例**：展示真實開發中的使用場景

### 🔍 **測試功能**
- 修改「條件控制欄位」觀察動態屬性變化
- 編輯數量和單價查看計算欄位更新
- 選擇客戶觀察 related 欄位自動帶入
- 複製記錄測試 copy 屬性行為

## 檔案更新清單

### 📁 **模型檔案**
- `models/training_model.py`: 新增 `FieldAttributeDemo` 類別

### 📋 **視圖檔案** 
- `views/training_views.xml`: 新增 Tree, Form, Search Views 和 Action
- `views/menus.xml`: 新增「欄位屬性展示」選單項目

### 🔐 **權限檔案**
- `security/ir.model.access.csv`: 新增模型存取權限

## 使用方式

1. **安裝/更新模組**: 更新 `cpk_odoo_field_training` 模組
2. **進入選單**: 「欄位類型訓練」→「欄位屬性展示」
3. **建立測試資料**: 點選「建立」新增記錄
4. **體驗屬性**: 填寫不同欄位觀察各種屬性效果
5. **學習原理**: 查看模型程式碼了解實作方式

## 進階學習

這個功能模組提供了完整的欄位屬性學習環境，建議按以下順序學習：

1. **基本屬性**: 從 string, required, readonly 開始
2. **預設值**: 學習不同類型的 default 設定
3. **計算欄位**: 理解 compute, store, inverse 的關係
4. **關係屬性**: 掌握 related, domain, context 用法
5. **動態控制**: 練習 attrs 的條件式設定
6. **進階功能**: 探索 tracking, translate, groups 等特殊屬性

---

**這個欄位屬性展示功能讓 Odoo 開發學習變得更加直觀和實用！** 🚀