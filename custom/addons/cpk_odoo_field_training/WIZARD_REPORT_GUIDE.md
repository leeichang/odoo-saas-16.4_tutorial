# 報表產生器 Wizard 功能指南

## 功能概述

新增了一個強大的報表產生器 Wizard，讓使用者可以通過條件篩選來產生客製化的 QWeb 報表。

## 📊 主要功能特色

### 🔍 **篩選條件設定**
- **姓名過濾**：支援部分符合的姓名關鍵字搜尋
- **日期範圍**：根據開始日期設定起迄範圍過濾
- **即時計數**：動態顯示符合條件的記錄數量

### 📋 **報表格式選項**
1. **PDF 標準報表**：完整的 PDF 格式，包含所有基本資訊
2. **HTML 網頁預覽**：在瀏覽器中即時預覽報表內容  
3. **PDF 詳細報表**：包含所有欄位類型的完整展示報表

### 💡 **使用者體驗優化**
- **預覽資料功能**：在產生報表前可先檢視篩選結果
- **條件驗證**：自動檢查是否有符合條件的記錄
- **詳細說明**：內建使用說明和格式說明頁籤

## 🗺️ 選單位置

```
欄位類型訓練 (主選單)
└── 報表與分析
    ├── 資料分析 (樞紐分析)
    └── 報表產生器 ⭐ (新功能)
```

## 🎯 使用流程

### 步驟 1：開啟報表產生器
1. 進入「欄位類型訓練」主選單
2. 點選「報表與分析」
3. 選擇「報表產生器」

### 步驟 2：設定篩選條件
- **姓名過濾**：輸入要搜尋的姓名關鍵字（可留空表示全部）
- **開始日期**：設定資料的起始日期
- **結束日期**：設定資料的結束日期
- 系統會即時顯示符合條件的記錄數量

### 步驟 3：選擇報表格式
- **PDF 標準報表**：適合正式文件和列印
- **HTML 網頁預覽**：適合快速檢視和線上分享
- **PDF 詳細報表**：適合完整資料展示和教學用途

### 步驟 4：產生或預覽
- **產生報表**：直接下載或開啟選定格式的報表
- **預覽資料**：在新視窗中檢視篩選後的資料列表

## 🔧 技術實作細節

### 檔案結構
```
cpk_odoo_field_training/
├── wizard/
│   ├── __init__.py
│   ├── field_training_report_wizard.py ⭐
│   └── field_training_report_wizard_views.xml ⭐
├── views/
│   └── menus.xml (更新)
├── security/
│   └── ir.model.access.csv (更新)
└── __manifest__.py (更新)
```

### Wizard 模型特色
```python
class FieldTrainingReportWizard(models.TransientModel):
    _name = 'cpk.field.training.report.wizard'
    _description = '欄位類型訓練報表產生器'
    
    # 篩選條件欄位
    name_filter = fields.Char(...)
    date_from = fields.Date(...)
    date_to = fields.Date(...)
    report_format = fields.Selection(...)
    
    # 動態計算符合條件記錄數
    record_count = fields.Integer(compute='_compute_record_count')
```

### 核心功能方法
- **`_build_domain()`**：建立 Odoo domain 篩選條件
- **`_compute_record_count()`**：即時計算符合條件記錄數
- **`action_generate_report()`**：產生指定格式的 QWeb 報表
- **`action_preview_data()`**：開啟篩選結果的資料檢視

## 🎨 介面設計特色

### 📱 **響應式表單設計**
- 清楚的區塊劃分（篩選條件 / 報表設定）
- 直觀的 Radio Button 格式選擇
- 即時的記錄數量顯示

### 📚 **內建說明系統**
- **使用說明**頁籤：詳細的操作指導
- **報表格式說明**頁籤：各格式特色和適用場景
- 卡片式格式介紹，美觀易懂

### 🎯 **操作按鈕配置**
- **產生報表**：主要動作按鈕（藍色）
- **預覽資料**：輔助檢視按鈕（灰色）
- **取消**：返回操作

## 💻 程式碼亮點

### 動態 Domain 建立
```python
def _build_domain(self):
    domain = []
    if self.name_filter:
        domain.append(('name', 'ilike', self.name_filter))
    if self.date_from:
        domain.append(('start_date', '>=', self.date_from))
    if self.date_to:
        domain.append(('start_date', '<=', self.date_to))
    return domain
```

### 報表動作產生
```python
def action_generate_report(self):
    # 篩選記錄
    domain = self._build_domain()
    records = self.env['cpk.field.training'].search(domain)
    
    # 決定報表類型和名稱
    report_type = 'qweb-html' if self.report_format == 'html' else 'qweb-pdf'
    
    # 返回報表動作
    return {
        'type': 'ir.actions.report',
        'report_name': report_name,
        'report_type': report_type,
        'model': 'cpk.field.training',
        'context': {'active_ids': records.ids},
        'data': {'ids': records.ids, 'model': 'cpk.field.training'}
    }
```

## 🚀 教學價值

### 學習重點
1. **TransientModel 使用**：了解暫時性模型的應用場景
2. **Domain 動態建立**：學習條件式查詢的實作
3. **Computed Field**：掌握即時計算欄位的使用
4. **Report Action**：理解 QWeb 報表的程式化調用
5. **Wizard 設計模式**：學習引導式操作介面設計

### 實務應用
- **條件式報表**：各種業務場景的篩選報表需求
- **使用者體驗**：直觀的操作流程設計
- **資料驗證**：篩選條件的有效性檢查
- **多格式輸出**：不同使用場景的報表格式選擇

## 🎉 使用範例

### 範例 1：特定期間報表
- 姓名過濾：（留空）
- 開始日期：2024-01-01
- 結束日期：2024-12-31
- 格式：PDF 標準報表
- 結果：產生 2024 年度完整報表

### 範例 2：特定人員分析
- 姓名過濾：張三
- 日期：（不設定）
- 格式：HTML 網頁預覽
- 結果：張三相關的所有記錄網頁報表

### 範例 3：詳細資料匯出
- 姓名過濾：（留空）
- 日期：最近一個月
- 格式：PDF 詳細報表
- 結果：包含所有欄位的完整展示報表

這個 Wizard 功能讓報表系統更加靈活和實用，提供了從條件設定到報表產生的完整使用者體驗！ 🎓