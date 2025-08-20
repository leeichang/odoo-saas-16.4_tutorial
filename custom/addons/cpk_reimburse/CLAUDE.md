# 費用請款單模組 (cpk_reimburse) 開發文檔

## 專案概述

費用請款單管理系統是一個完整的 Odoo 16.4 模組，專為企業費用報銷流程設計。本模組提供從員工提交費用請款到財務審核付款的完整工作流程。

## 需求分析

### 業務需求
- **請款人員**：員工可以提交自己的費用請款申請
- **憑證管理**：支援發票和收據的上傳與分類
- **費用分類**：兩階層費用類別管理（大分類/小分類）
- **權限控制**：員工只能查看自己的資料，財務人員可查看全部
- **審核流程**：完整的狀態流程管理
- **金額計算**：自動計算含稅/未稅/稅額

### 技術需求
- 基於 Odoo 16.4 框架
- 使用 Monetary 欄位處理金額
- 支援多幣別處理
- 自動編號機制
- 檔案上傳功能

## 資料模型設計

### 1. 主要模型

#### cpk.reimburse (請款單頭)
```python
_name = 'cpk.reimburse'
_description = '費用請款單'
```

**關鍵欄位：**
- `name`: 請款單號（自動編號：RE + 年月 + 流水號）
- `employee_id`: 請款人員 → hr.employee
- `reimburse_date`: 請款日期
- `partner_id`: 付款對象 → res.partner
- `bank_id`: 銀行 → res.bank（從聯絡人帶出）
- `payment_method_id`: 付款方式 → account.payment.method
- `due_date`: 帳款到期日
- `currency_id`: 付款幣別 → res.currency
- `state`: 狀態（draft/confirmed/submitted/approved/paid/closed）
- `total_amount`: 總金額（計算欄位）
- `total_tax`: 總稅額（計算欄位）

**特殊功能：**
- 自動從聯絡人帶出銀行資訊
- 根據請款明細自動計算總額
- 狀態追蹤機制

#### cpk.voucher (憑證資料)
```python
_name = 'cpk.voucher'
_description = '憑證資料'
```

**關鍵欄位：**
- `reimburse_id`: 請款單 → cpk.reimburse
- `voucher_type`: 憑證類型（invoice=發票/receipt=收據）
- `invoice_date`: 發票日期
- `tax_code_id`: 稅碼 → cpk.tax.code
- `tax_id`: 統一編號
- `invoice_number`: 發票號碼
- `attachment_ids`: 上傳憑證 → ir.attachment
- `currency_id`: 交易幣別
- `amount_total`: 交易金額(含稅)
- `amount_untaxed`: 交易金額(未稅)
- `tax_amount`: 稅額

#### cpk.expense.line (請款明細)
```python
_name = 'cpk.expense.line'
_description = '請款明細'
```

**關鍵欄位：**
- `reimburse_id`: 請款單 → cpk.reimburse
- `voucher_id`: 憑證 → cpk.voucher
- `sequence`: 項次
- `expense_category_id`: 費用類別 → cpk.expense.category
- `cost_center_id`: 成本中心 → hr.department
- `amount_total`: 金額含稅
- `amount_untaxed`: 金額未稅
- `tax_amount`: 稅額
- `analytic_account_id`: 專案代號 → account.analytic.account
- `description`: 費用說明

### 2. 設定模型

#### cpk.expense.category (費用類別)
```python
_name = 'cpk.expense.category'
_description = '費用類別'
_parent_store = True  # 支援樹狀結構
```

**關鍵欄位：**
- `code`: 代碼
- `name`: 名稱
- `parent_id`: 父類別 → cpk.expense.category
- `child_ids`: 子類別
- `account_id`: 會計科目 → account.account
- `is_leaf`: 是否為明細（計算欄位）
- `complete_name`: 完整名稱（計算欄位）

**樹狀結構範例：**
```
01 交通費(公出)
├── 0101 過路費
├── 0102 計程車車資
└── 0103 停車費
02 差旅費
├── 0201 機票款
└── 0202 住宿費
```

#### cpk.tax.code (稅別)
```python
_name = 'cpk.tax.code'
_description = '稅別'
```

**關鍵欄位：**
- `code`: 代碼
- `name`: 說明

**預設稅別：**
- VN: 與稅無關
- VB: 進項三聯式收銀機統一發票
- VA: 進項二聯式發票
- V1-V4: 各種進項稅類型

## 視圖設計

### 1. Tree View (列表檢視)
顯示欄位：
- 請款單號
- 請款人員
- 付款對象
- 付款方式
- 帳款到期日
- 幣別
- 總金額
- 總稅額
- 狀態

### 2. Form View (表單檢視)
**頁籤設計：**
- **基本資料頁籤**：
  - 單頭資訊（請款人、付款對象、銀行資訊等）
  - 請款明細（可新增/編輯的一對多清單）
  
- **憑證明細頁籤**：
  - 憑證資料（唯讀顯示）
  - 顯示關聯的所有憑證

### 3. Dialog Form (對話框表單)
**費用報銷明細新增對話框：**
- **上半部**：憑證資料（可新增與編輯）
- **下半部**：請款明細編輯區

## 選單結構

```
費用請款 (主選單)
├── 費用請款 (主功能)
└── 設定
    ├── 費用類別 (系統管理員限定)
    └── 稅別設定 (系統管理員限定)
```

## 權限設計

### 1. 群組設定
- **base.group_user (員工)**：基本員工權限
- **group_cpk_finance_cashier (財務出納)**：財務人員權限
- **base.group_system (系統管理員)**：系統管理權限

### 2. 存取控制
- **員工**：只能查看/編輯自己的請款單
- **財務出納**：可查看/編輯所有請款單
- **系統管理員**：完整權限 + 設定功能

### 3. 記錄規則 (Record Rules)
```xml
<!-- 員工只能看自己的資料 -->
<field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>

<!-- 財務人員和系統管理員可看全部 -->
<field name="domain_force">[(1, '=', 1)]</field>
```

## 特殊功能實現

### 1. 自動編號機制
```xml
<record id="seq_cpk_reimburse" model="ir.sequence">
    <field name="code">cpk.reimburse</field>
    <field name="prefix">RE</field>
    <field name="suffix">%(year)s%(month)s</field>
    <field name="padding">4</field>
</record>
```
產生格式：RE202501001

### 2. 銀行資訊自動帶入
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id and self.partner_id.bank_ids:
        bank_account = self.partner_id.bank_ids[0]
        self.bank_id = bank_account.bank_id.id
        self.bank_account = bank_account.acc_number
        self.account_holder = self.partner_id.name
```

### 3. 金額自動計算
```python
@api.depends('expense_line_ids.amount_total', 'expense_line_ids.tax_amount')
def _compute_amounts(self):
    for record in self:
        record.total_amount = sum(record.expense_line_ids.mapped('amount_total'))
        record.total_tax = sum(record.expense_line_ids.mapped('tax_amount'))
```

### 4. 金額驗證
```python
@api.constrains('amount_total', 'amount_untaxed', 'tax_amount')
def _check_amounts(self):
    for record in self:
        if record.amount_total and record.amount_untaxed and record.tax_amount:
            if abs(record.amount_total - record.amount_untaxed - record.tax_amount) > 0.01:
                raise ValidationError('金額計算錯誤：含稅金額 = 未稅金額 + 稅額')
```

## 檔案結構

```
cpk_reimburse/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── models.py          # 主要模型
│   ├── expense_category.py # 費用類別模型
│   └── tax_code.py        # 稅別模型
├── views/
│   ├── reimburse_views.xml        # 主要視圖
│   ├── expense_category_views.xml # 費用類別視圖
│   ├── tax_code_views.xml        # 稅別視圖
│   └── menus.xml                 # 選單定義
├── security/
│   ├── security.xml              # 群組和記錄規則
│   └── ir.model.access.csv       # 模型存取權限
├── data/
│   ├── sequence.xml              # 序號設定
│   └── expense_category_data.xml # 初始資料
└── CLAUDE.md                     # 本文檔
```

## 初始資料

### 費用類別預設資料
系統預設建立 6 大類共 34 筆費用類別：

1. **交通費(公出)**：過路費、計程車車資、停車費、油資等 9 項
2. **差旅費**：機票款、住宿費、出差津貼 3 項
3. **膳宿費**：餐費、住宿費（內部/外部）4 項
4. **辦公用品**：文具用品、印刷費、電腦耗材 3 項
5. **通訊費**：電話費、網路費、郵寄費 3 項
6. **教育訓練**：外部訓練費、教材費、證照考試費 3 項

### 稅別預設資料
提供台灣常用的稅別代碼：
- VN: 與稅無關
- VB: 進項三聯式收銀機統一發票
- VA: 進項二聯式發票
- V1-V4: 各種進項稅 5% 類型

## 安裝與測試

### 1. 模組依賴
```python
'depends': ['base', 'hr', 'account', 'hr_expense']
```

### 2. 安裝步驟
1. 將模組放置於 `custom/addons/cpk_reimburse/` 目錄
2. 更新應用程式列表
3. 搜尋「費用請款單」並安裝
4. 系統會自動載入初始資料

### 3. 測試檢查項目
- [ ] 模組安裝無錯誤
- [ ] 選單顯示正常
- [ ] 費用類別資料已載入
- [ ] 稅別資料已載入
- [ ] 可建立請款單
- [ ] 權限控制正常
- [ ] 序號產生正常
- [ ] 金額計算正確

## 開發歷程

### 規劃階段
1. 需求分析與資料模型設計
2. 視圖與選單結構規劃
3. 權限設計與安全控制
4. 初始資料準備

### 實作階段
1. ✅ 更新模組清單與依賴
2. ✅ 建立主要模型（請款單頭、憑證、明細）
3. ✅ 建立設定模型（費用類別、稅別）
4. ✅ 建立所有視圖檔案
5. ✅ 建立選單結構
6. ✅ 設定權限控制
7. ✅ 建立自動編號機制
8. ✅ 建立初始資料

### 驗證階段
- **下一步**：模組啟動測試
- **下一步**：功能驗證測試
- **下一步**：權限控制測試
- **下一步**：效能與穩定性測試

## 維護與擴展

### 未來可能的擴展功能
1. **工作流程**：加入簽核流程
2. **報表功能**：費用分析報表
3. **預算控制**：與預算模組整合
4. **行動支援**：手機 APP 整合
5. **API 介面**：外部系統整合

### 維護注意事項
1. 定期備份費用類別和稅別設定
2. 監控序號產生機制
3. 檢查權限設定的完整性
4. 留意 Odoo 版本升級的相容性

---

**模組資訊**
- 版本：16.4.1.0
- 開發者：Cympotek
- 授權：專案授權
- 最後更新：2025-08-19
