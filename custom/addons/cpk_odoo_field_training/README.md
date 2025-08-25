# Odoo 欄位類型教育訓練模組

## 模組介紹

這是一個專門為 Odoo 16 開發的教育訓練模組，展示了所有支援的欄位類型及其在 Tree View 和 Form View 中的呈現方式。

## 欄位類型完整展示

### 🔤 基本欄位類型 (Basic Field Types)

| 欄位類型 | 範例欄位 | Widget 展示 | 說明 |
|---------|---------|------------|-----|
| **Char** | `name`, `code` | text, char | 短文字字符串，支援長度限制 |
| **Text** | `description` | text | 多行長文字內容 |
| **Integer** | `quantity`, `age` | integer | 整數數值 |
| **Float** | `price`, `weight`, `percentage` | float, percentage | 浮點數，可設定小數位數 |
| **Boolean** | `is_active`, `is_completed` | boolean_toggle, checkbox | 布林值 True/False |
| **Date** | `birth_date`, `start_date` | date | 日期選擇器 |
| **Datetime** | `order_datetime`, `last_update` | datetime | 日期時間選擇器 |
| **Selection** | `status`, `priority`, `gender` | selection, badge, radio | 預定義選項清單 |
| **Binary** | `attachment`, `document` | binary | 二進位檔案上傳 |
| **Image** | `image`, `avatar` | image | 圖片預覽與上傳 |

### 🔗 關係欄位類型 (Relational Field Types)

| 欄位類型 | 範例欄位 | Widget 展示 | 說明 |
|---------|---------|------------|-----|
| **Many2one** | `partner_id`, `user_id`, `company_id` | many2one, many2one_avatar | 多對一關聯 |
| **One2many** | `line_ids` | one2many | 一對多關聯，顯示為內嵌表格 |
| **Many2many** | `tag_ids`, `project_ids` | many2many_tags, many2many | 多對多關聯 |

### 🚀 進階欄位類型 (Advanced Field Types)

| 欄位類型 | 範例欄位 | Widget 展示 | 說明 |
|---------|---------|------------|-----|
| **Monetary** | `amount_total`, `unit_price` | monetary | 貨幣金額，支援多幣別 |
| **Html** | `html_content`, `email_template` | html | HTML 富文字編輯器 |
| **Related** | `partner_email`, `partner_phone` | 依相關欄位類型 | 關聯欄位自動帶入 |
| **Reference** | `reference_field` | reference | 動態模型參考 |
| **Json** | `json_data`, `api_config` | ace, json | JSON 結構化資料 |
| **Properties** | `properties` | properties | 動態屬性欄位 |

### 📊 特殊欄位 (Special Fields)

| 欄位類型 | 範例欄位 | 說明 |
|---------|---------|-----|
| **Computed** | `total_lines`, `full_name` | 計算欄位，根據其他欄位自動計算 |
| **Constraint** | `age`, `percentage` | 欄位驗證約束 |

## 視圖設計特色

### Tree View 特色
- 🎯 展示主要欄位的簡潔列表
- 🎨 使用多種 widget：`boolean_toggle`, `badge`, `monetary`, `many2one_avatar_user`
- 🎪 支援狀態裝飾色彩標示
- 📊 可編輯列表支援

### Form View 特色
- 📋 分頁展示不同類型欄位
- 📈 統計按鈕和狀態列展示
- 🎛️ 每種欄位適合的 widget 展示
- ⚡ 支援內嵌編輯、拖拉排序等互動功能
- 💬 整合 Chatter 功能（訊息追蹤）

## 模組結構

```
cpk_odoo_field_training/
├── __init__.py                 # 模組初始化
├── __manifest__.py            # 模組配置檔案
├── models/
│   ├── __init__.py
│   └── training_model.py      # 主要模型定義
├── views/
│   ├── training_views.xml     # Tree & Form 視圖
│   └── menus.xml             # 選單結構
├── security/
│   └── ir.model.access.csv   # 存取權限設定
└── README.md                 # 說明文檔
```

## 安裝與使用

### 安裝步驟
1. 將模組放置於 Odoo 的 addons 目錄中
2. 更新應用程式列表
3. 搜尋「Odoo 欄位類型教育訓練」並安裝
4. 安裝完成後會出現「欄位類型訓練」主選單

### 使用方式
1. 點選「欄位類型訓練」→「欄位類型演示」
2. 建立新記錄，嘗試填寫各種類型的欄位
3. 在 Tree View 和 Form View 之間切換，觀察不同的呈現效果
4. 測試不同 Widget 的互動功能

## 教學重點

### 基本欄位操作
- 了解各種基本資料類型的使用場景
- 學習 widget 參數設定對視覺呈現的影響
- 掌握欄位驗證和約束的使用

### 關係欄位設計
- 理解一對多、多對一、多對多關係
- 學習如何設計合適的關聯模型
- 掌握關聯欄位的視圖呈現技巧

### 進階功能應用
- 學習貨幣欄位的多幣別處理
- 掌握 HTML 編輯器的使用
- 了解 JSON 資料欄位的應用場景

### 視圖設計技巧
- 學習如何選擇合適的 widget
- 掌握分頁、分組、裝飾等視圖技巧
- 理解響應式設計原則

## 技術特點

- ✅ 支援 Odoo 16 所有欄位類型
- ✅ 包含完整的 widget 展示範例
- ✅ 整合郵件追蹤功能
- ✅ 支援欄位驗證約束
- ✅ 包含計算欄位範例
- ✅ 支援多語言介面
- ✅ 符合 Odoo 開發規範

## 適用對象

- 🎓 Odoo 初學者 - 了解基礎欄位類型
- 👨‍💻 開發人員 - 學習進階欄位應用
- 🏢 顧問師 - 參考視圖設計技巧
- 📚 培訓講師 - 作為教學演示工具

---

**版本資訊**
- Odoo 版本：16.4
- 模組版本：1.0
- 開發者：Cympotek
- 授權：LGPL-3