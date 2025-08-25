# Odoo 16 ERP 客製開發教育訓練

**講師：李奕璋**  
**版本：v1r2**  
**日期：2024.12.24**  
**©Cympotek. All rights reserved.**

---

## 目錄

1. [Odoo 系統架構概述](#1-odoo-系統架構概述)
2. [開發環境安裝設定](#2-開發環境安裝設定)
3. [Odoo 模組結構](#3-odoo-模組結構)
4. [cpk_reimburse 費用請款模組完整開發](#4-cpk_reimburse-費用請款模組完整開發)
5. [樞紐分析報表開發](#5-樞紐分析報表開發)
6. [Qweb 報表設計與實作](#6-qweb-報表設計與實作)
7. [Wizard 精靈開發](#7-wizard-精靈開發)
8. [Excel 匯入功能開發](#8-excel-匯入功能開發)
9. [One2many/Many2many Dialog 機制](#9-one2manymany2many-dialog-機制)
10. [實務開發技巧](#10-實務開發技巧)
11. [除錯與測試](#11-除錯與測試)

---

## 1. Odoo 系統架構概述

### 1.1 Odoo 簡介

Odoo 是一個**模組化的 ERP 系統**，每個功能都是獨立的模組！

```
┌─────────────────────────────────────────────────────────┐
│                    Odoo ERP 系統                        │
├─────────────┬─────────────┬─────────────┬─────────────┤
│   銷售模組   │   採購模組   │   庫存模組   │   會計模組   │
├─────────────┼─────────────┼─────────────┼─────────────┤
│   製造模組   │   人資模組   │   專案模組   │  客製模組   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### 1.2 簡易業務流程圖

```
客戶 → 銷售訂單 → MRP → 製造工單 → 採購單 → 收貨
  ↑                                          ↓
出貨 ← 生產入庫 ← 倉庫 ← 原物料發料 ←─────────────┘
  ↓
應收帳款
  ↓
應付帳款
```

### 1.3 技術架構

- **後端**：Python (Odoo Framework)
- **資料庫**：PostgreSQL
- **前端**：JavaScript + XML Views
- **報表**：QWeb Template Engine
- **API**：XML-RPC, JSON-RPC, REST API

---

## 2. 開發環境安裝設定

### 2.1 系統需求

```bash
# 檢查 Python 版本
python3 --version
# 輸出：Python 3.9.6 或更高版本
```

### 2.2 安裝 PostgreSQL 14

```bash
# macOS 使用 Homebrew
brew install postgresql@14
brew services start postgresql@14
```

### 2.3 建立 Python 虛擬環境

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 提示符變化
(.venv) liyizhang@MacBook-Pro odoo-16.0 %
```

### 2.4 安裝 Odoo 依賴

```bash
pip install -r requirements.txt
```

> **注意**：如果遇到安裝錯誤，請將錯誤訊息提供給 Claude 協助解決！

### 2.5 資料庫設定

```sql
-- 建立 Odoo 用戶
CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo';
ALTER ROLE odoo CREATEDB;
```

### 2.6 設定 Odoo 配置檔

編輯 `debian/odoo.conf`：

```ini
[options]
admin_passwd = odoo27855600
db_user = odoo
db_password = odoo
db_host = localhost
db_port = 5432
addons_path = addons,custom/addons
```

### 2.7 VS Code 設定

請 Claude 協助設定 `launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo: Run Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/odoo-bin",
            "args": [
                "-c", "${workspaceFolder}/debian/odoo.conf",
                "--dev=all"
            ],
            "console": "integratedTerminal"
        },
        {
            "name": "Odoo: Update Module",
            "type": "python", 
            "request": "launch",
            "program": "${workspaceFolder}/odoo-bin",
            "args": [
                "-c", "${workspaceFolder}/debian/odoo.conf",
                "-d", "odoo16",
                "-u", "cpk_reimburse",
                "--stop-after-init"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### 2.8 資料庫管理

```sql
-- 查看活動連接
SELECT pid, usename, datname, client_addr, state 
FROM pg_stat_activity WHERE datname = 'odoo16';

-- 終止所有連接
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity WHERE datname = 'odoo16';

-- 刪除資料庫
DROP DATABASE odoo16;
```

### 2.9 首次啟動設定

1. **啟動 Odoo 服務**
2. **建立資料庫**
3. **安裝基礎模組**：銷售、CRM、採購、庫存、會計、製造
4. **啟動開發者模式**
5. **設定使用者權限**

---

## 3. Odoo 模組結構

### 3.1 標準 Addon 專案結構

```
my_addon/
├── __init__.py                 # Python 模組初始化
├── __manifest__.py            # 模組元資料定義
├── models/                    # 資料模型
│   ├── __init__.py
│   └── my_model.py
├── views/                     # 使用者介面
│   ├── my_model_views.xml
│   └── menus.xml
├── data/                      # 初始資料
│   └── my_data.xml
├── security/                  # 權限控制
│   ├── ir.model.access.csv
│   └── security.xml
├── static/                    # 靜態資源
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       └── css/
├── reports/                   # 報表模板
│   └── report_templates.xml
└── wizard/                    # 精靈對話框
    ├── __init__.py
    └── my_wizard.py
```

### 3.2 __manifest__.py 詳解

```python
{
    'name': 'Library Management',           # 模組名稱
    'version': '16.0.1.0.0',              # 版本號
    'summary': 'Manage books in library',  # 簡短描述
    'description': """
        詳細說明模組功能和特色
    """,
    'author': 'Your Company',              # 作者
    'category': 'Services',                # 分類
    'depends': ['base', 'hr'],             # 依賴模組
    'data': [                              # 資料檔案載入順序
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/library_data.xml',
        'views/library_views.xml',
        'views/menus.xml',
    ],
    'assets': {                            # 前端資源
        'web.assets_backend': [
            'library/static/src/js/library.js',
        ],
    },
    'application': True,                   # 是否為應用程式
    'installable': True,                   # 是否可安裝
    'auto_install': False,                 # 是否自動安裝
    'license': 'LGPL-3',                   # 授權協議
}
```

### 3.3 快速產生 Addon

```bash
# 使用 scaffold 指令快速建立模組骨架
python odoo-bin scaffold module_name addons_path/

# 範例：建立費用請款模組
python odoo-bin scaffold cpk_reimburse custom/addons/
```

---

## 4. cpk_reimburse 費用請款模組完整開發

### 4.1 需求分析

**業務需求**：
- 員工提交費用請款申請
- 支援發票和收據上傳
- 兩階層費用分類管理
- 權限控制（員工只能看自己的資料）
- 完整的審核流程
- 自動金額計算和驗證

**技術需求**：
- 基於 Odoo 16.4 框架
- 支援多幣別處理
- 自動編號機制
- 檔案上傳功能
- 樞紐分析和報表

### 4.2 資料模型設計

#### 4.2.1 主要模型關係圖

```
cpk.reimburse (請款單頭)
    ├── cpk.voucher (憑證資料) [One2many]
    └── cpk.expense.line (請款明細) [One2many]
            └── cpk.voucher (憑證關聯) [Many2one]

cpk.expense.category (費用類別) [樹狀結構]
cpk.tax.code (稅別)
```

#### 4.2.2 cpk.reimburse (請款單頭) 模型

```python
# models/models.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CpkReimburse(models.Model):
    _name = 'cpk.reimburse'
    _description = '費用請款單'
    _order = 'name desc'

    # 基本資訊
    name = fields.Char('請款單號', required=True, copy=False, 
                      readonly=True, default='新建')
    employee_id = fields.Many2one('hr.employee', '請款人員', 
                                 required=True, 
                                 default=lambda self: self.env.user.employee_id)
    reimburse_date = fields.Date('請款日期', required=True, 
                                default=fields.Date.context_today)
    
    # 付款資訊
    partner_id = fields.Many2one('res.partner', '付款對象', required=True)
    alternative_payee = fields.Char('替代受款人')
    bank_id = fields.Many2one('res.bank', '銀行')
    payment_method_id = fields.Many2one('account.payment.method', 
                                       '付款方式', required=True)
    due_date = fields.Date('帳款到期日', required=True)
    account_holder = fields.Char('戶名')
    bank_account = fields.Char('銀行帳號')
    
    # 金額資訊
    currency_id = fields.Many2one('res.currency', '付款幣別', 
                                 required=True, 
                                 default=lambda self: self.env.company.currency_id)
    exchange_rate = fields.Float('匯率', default=1.0, digits=(12, 6))
    advance_balance = fields.Monetary('預付款餘額', 
                                     currency_field='currency_id')
    
    # 計算欄位
    total_amount = fields.Monetary('總金額', currency_field='currency_id',
                                  compute='_compute_amounts', store=True)
    total_tax = fields.Monetary('總稅額', currency_field='currency_id',
                               compute='_compute_amounts', store=True)
    
    # 狀態管理
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('submitted', '送簽核'),
        ('approved', '審核'),
        ('paid', '付款'),
        ('closed', '結案'),
    ], default='draft', string='狀態', tracking=True)
    
    # 關聯欄位
    expense_line_ids = fields.One2many('cpk.expense.line', 'reimburse_id', 
                                      '請款明細')
    voucher_ids = fields.One2many('cpk.voucher', 'reimburse_id', 
                                 '憑證資料')
    
    notes = fields.Text('備註')

    @api.model
    def create(self, vals):
        """建立記錄時自動產生編號"""
        if vals.get('name', '新建') == '新建':
            vals['name'] = self.env['ir.sequence'].next_by_code('cpk.reimburse')
        return super().create(vals)

    @api.depends('expense_line_ids.amount_total', 'expense_line_ids.tax_amount')
    def _compute_amounts(self):
        """計算總金額和總稅額"""
        for record in self:
            record.total_amount = sum(record.expense_line_ids.mapped('amount_total'))
            record.total_tax = sum(record.expense_line_ids.mapped('tax_amount'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """付款對象變更時自動帶入銀行資訊"""
        if self.partner_id and self.partner_id.bank_ids:
            bank_account = self.partner_id.bank_ids[0]
            self.bank_id = bank_account.bank_id.id
            self.bank_account = bank_account.acc_number
            self.account_holder = self.partner_id.name
```

#### 4.2.3 cpk.voucher (憑證資料) 模型

```python
class CpkVoucher(models.Model):
    _name = 'cpk.voucher'
    _description = '憑證資料'

    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', 
                                  required=True, ondelete='cascade')
    voucher_type = fields.Selection([
        ('invoice', '發票'),
        ('receipt', '收據'),
    ], string='憑證類型', required=True)
    
    # 發票資訊
    invoice_date = fields.Date('發票日期')
    tax_code_id = fields.Many2one('cpk.tax.code', '稅碼')
    tax_id = fields.Char('統一編號')
    invoice_number = fields.Char('發票號碼')
    
    # 金額資訊
    currency_id = fields.Many2one('res.currency', '交易幣別', required=True)
    amount_total = fields.Monetary('交易金額(含稅)', currency_field='currency_id')
    amount_untaxed = fields.Monetary('交易金額(未稅)', currency_field='currency_id')
    tax_amount = fields.Monetary('稅額', currency_field='currency_id')
    
    # 附件
    attachment_ids = fields.Many2many('ir.attachment', string='上傳憑證')
    
    # 關聯明細
    expense_line_ids = fields.One2many('cpk.expense.line', 'voucher_id', 
                                      '請款明細')

    @api.constrains('amount_total', 'amount_untaxed', 'tax_amount')
    def _check_amounts(self):
        """驗證金額計算正確性"""
        for record in self:
            if (record.amount_total and record.amount_untaxed and 
                record.tax_amount):
                calculated_total = record.amount_untaxed + record.tax_amount
                if abs(record.amount_total - calculated_total) > 0.01:
                    raise ValidationError(
                        '金額計算錯誤：含稅金額 = 未稅金額 + 稅額'
                    )
```

#### 4.2.4 cpk.expense.line (請款明細) 模型

```python
class CpkExpenseLine(models.Model):
    _name = 'cpk.expense.line'
    _description = '請款明細'

    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', 
                                  required=True, ondelete='cascade')
    voucher_id = fields.Many2one('cpk.voucher', '憑證')
    sequence = fields.Integer('項次', default=10)
    
    # 分類資訊
    expense_category_id = fields.Many2one('cpk.expense.category', 
                                         '費用類別', required=True)
    cost_center_id = fields.Many2one('hr.department', '成本中心')
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                         '專案代號')
    
    # 金額資訊
    currency_id = fields.Related('reimburse_id.currency_id', 
                                string='幣別', readonly=True)
    amount_total = fields.Monetary('金額含稅', currency_field='currency_id')
    amount_untaxed = fields.Monetary('金額未稅', currency_field='currency_id')
    tax_amount = fields.Monetary('稅額', currency_field='currency_id')
    
    description = fields.Text('費用說明')

    @api.onchange('amount_untaxed', 'tax_amount')
    def _onchange_amounts(self):
        """未稅金額或稅額變更時自動計算含稅金額"""
        self.amount_total = self.amount_untaxed + self.tax_amount
```

#### 4.2.5 cpk.expense.category (費用類別) 模型

```python
# models/expense_category.py
class CpkExpenseCategory(models.Model):
    _name = 'cpk.expense.category'
    _description = '費用類別'
    _parent_store = True  # 啟用樹狀結構快速查詢
    _order = 'complete_name'

    name = fields.Char('名稱', required=True)
    code = fields.Char('代碼', required=True)
    complete_name = fields.Char('完整名稱', compute='_compute_complete_name',
                               recursive=True, store=True)
    
    # 樹狀結構
    parent_id = fields.Many2one('cpk.expense.category', '父類別', 
                               ondelete='cascade')
    child_ids = fields.One2many('cpk.expense.category', 'parent_id', 
                               '子類別')
    parent_path = fields.Char(index=True)
    
    # 會計關聯
    account_id = fields.Many2one('account.account', '會計科目')
    
    # 計算欄位
    is_leaf = fields.Boolean('是否為明細', compute='_compute_is_leaf')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        """計算完整名稱"""
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    @api.depends('child_ids')
    def _compute_is_leaf(self):
        """判斷是否為明細類別（沒有子類別）"""
        for category in self:
            category.is_leaf = not bool(category.child_ids)

    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        """檢查是否有循環參照"""
        if not self._check_recursion():
            raise ValidationError('費用類別不能有循環參照！')
```

#### 4.2.6 cpk.tax.code (稅別) 模型

```python
# models/tax_code.py
class CpkTaxCode(models.Model):
    _name = 'cpk.tax.code'
    _description = '稅別'

    code = fields.Char('代碼', required=True)
    name = fields.Char('說明', required=True)
    active = fields.Boolean('啟用', default=True)

    def name_get(self):
        """自訂顯示格式：代碼 - 說明"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            result.append((record.id, name))
        return result
```

### 4.3 視圖設計

#### 4.3.1 Tree View (列表檢視)

```xml
<!-- views/reimburse_views.xml -->
<record id="view_cpk_reimburse_tree" model="ir.ui.view">
    <field name="name">cpk.reimburse.tree</field>
    <field name="model">cpk.reimburse</field>
    <field name="arch" type="xml">
        <tree string="費用請款單" 
              decoration-info="state=='draft'" 
              decoration-muted="state=='closed'">
            <field name="name"/>
            <field name="employee_id"/>
            <field name="partner_id"/>
            <field name="payment_method_id"/>
            <field name="due_date"/>
            <field name="currency_id"/>
            <field name="total_amount" sum="總金額"/>
            <field name="total_tax" sum="總稅額"/>
            <field name="state" widget="badge"/>
        </tree>
    </field>
</record>
```

#### 4.3.2 Form View (表單檢視)

```xml
<record id="view_cpk_reimburse_form" model="ir.ui.view">
    <field name="name">cpk.reimburse.form</field>
    <field name="model">cpk.reimburse</field>
    <field name="arch" type="xml">
        <form string="費用請款單">
            <header>
                <button name="%(action_cpk_reimburse_print_wizard)d" 
                        string="列印" type="action" 
                        class="btn-primary"/>
                <field name="state" widget="statusbar" 
                       statusbar_visible="draft,confirmed,submitted,approved,paid,closed"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1>
                        <field name="name" readonly="1"/>
                    </h1>
                </div>
                
                <group>
                    <group name="basic_info">
                        <field name="employee_id"/>
                        <field name="reimburse_date"/>
                        <field name="partner_id"/>
                        <field name="payment_method_id"/>
                        <field name="due_date"/>
                    </group>
                    <group name="payment_info">
                        <field name="bank_id"/>
                        <field name="account_holder"/>
                        <field name="bank_account"/>
                        <field name="currency_id"/>
                        <field name="total_amount"/>
                        <field name="total_tax"/>
                    </group>
                </group>

                <notebook>
                    <!-- 基本資料頁籤 -->
                    <page string="基本資料">
                        <field name="expense_line_ids">
                            <tree editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="expense_category_id"/>
                                <field name="cost_center_id"/>
                                <field name="amount_untaxed"/>
                                <field name="tax_amount"/>
                                <field name="amount_total"/>
                                <field name="description"/>
                            </tree>
                        </field>
                    </page>
                    
                    <!-- 憑證明細頁籤 -->
                    <page string="憑證明細">
                        <field name="voucher_ids" readonly="1">
                            <tree>
                                <field name="voucher_type"/>
                                <field name="invoice_date"/>
                                <field name="invoice_number"/>
                                <field name="amount_total"/>
                                <field name="currency_id"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
                
                <group>
                    <field name="notes" placeholder="請填寫備註資訊..."/>
                </group>
            </sheet>
            
            <!-- Chatter -->
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

#### 4.3.3 Search View (搜尋檢視)

```xml
<record id="view_cpk_reimburse_search" model="ir.ui.view">
    <field name="name">cpk.reimburse.search</field>
    <field name="model">cpk.reimburse</field>
    <field name="arch" type="xml">
        <search>
            <field name="name"/>
            <field name="employee_id"/>
            <field name="partner_id"/>
            
            <filter name="my_requests" string="我的請款單"
                    domain="[('employee_id.user_id', '=', uid)]"/>
            <filter name="draft" string="草稿狀態"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="this_month" string="本月"
                    domain="[('reimburse_date', '>=', context_today().strftime('%Y-%m-01'))]"/>
            
            <group expand="0" string="分組">
                <filter string="請款人員" name="group_employee" 
                        context="{'group_by': 'employee_id'}"/>
                <filter string="狀態" name="group_state" 
                        context="{'group_by': 'state'}"/>
                <filter string="請款月份" name="group_month" 
                        context="{'group_by': 'reimburse_date:month'}"/>
            </group>
        </search>
    </field>
</record>
```

### 4.4 選單結構

```xml
<!-- views/menus.xml -->
<odoo>
    <!-- 主選單 -->
    <menuitem id="menu_cpk_reimburse_root" 
              name="費用請款" 
              sequence="10"/>
    
    <!-- 費用請款功能選單 -->
    <menuitem id="menu_cpk_reimburse_main" 
              name="費用請款" 
              parent="menu_cpk_reimburse_root"
              action="action_cpk_reimburse" 
              sequence="10"/>
    
    <!-- 設定選單 -->
    <menuitem id="menu_cpk_reimburse_config" 
              name="設定" 
              parent="menu_cpk_reimburse_root" 
              sequence="90"
              groups="base.group_system"/>
    
    <!-- 費用類別設定 -->
    <menuitem id="menu_expense_category" 
              name="費用類別" 
              parent="menu_cpk_reimburse_config"
              action="action_expense_category" 
              sequence="10"/>
    
    <!-- 稅別設定 -->
    <menuitem id="menu_tax_code" 
              name="稅別設定" 
              parent="menu_cpk_reimburse_config"
              action="action_tax_code" 
              sequence="20"/>

    <!-- 動作定義 -->
    <record id="action_cpk_reimburse" model="ir.actions.act_window">
        <field name="name">費用請款單</field>
        <field name="res_model">cpk.reimburse</field>
        <field name="view_mode">tree,form,pivot,graph</field>
        <field name="context">{
            'search_default_my_requests': 1,
            'search_default_this_month': 1
        }</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                建立您的第一張費用請款單！
            </p>
            <p>
                點擊建立按鈕開始新增費用請款單。
            </p>
        </field>
    </record>
</odoo>
```

### 4.5 權限控制

#### 4.5.1 安全群組定義

```xml
<!-- security/security.xml -->
<odoo>
    <data noupdate="1">
        <!-- 財務出納群組 -->
        <record id="group_cpk_finance_cashier" model="res.groups">
            <field name="name">財務出納</field>
            <field name="category_id" ref="base.module_category_accounting"/>
        </record>
    </data>

    <!-- 記錄規則 -->
    <data noupdate="1">
        <!-- 員工只能看自己的請款單 -->
        <record id="rule_cpk_reimburse_employee" model="ir.rule">
            <field name="name">員工請款單存取規則</field>
            <field name="model_id" ref="model_cpk_reimburse"/>
            <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <!-- 財務人員可看全部 -->
        <record id="rule_cpk_reimburse_finance" model="ir.rule">
            <field name="name">財務人員請款單存取規則</field>
            <field name="model_id" ref="model_cpk_reimburse"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('group_cpk_finance_cashier')), 
                                       (4, ref('base.group_system'))]"/>
        </record>
    </data>
</odoo>
```

#### 4.5.2 模型存取權限

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_cpk_reimburse_user,cpk.reimburse.user,model_cpk_reimburse,base.group_user,1,1,1,1
access_cpk_reimburse_finance,cpk.reimburse.finance,model_cpk_reimburse,group_cpk_finance_cashier,1,1,1,1
access_cpk_voucher_user,cpk.voucher.user,model_cpk_voucher,base.group_user,1,1,1,1
access_cpk_expense_line_user,cpk.expense.line.user,model_cpk_expense_line,base.group_user,1,1,1,1
access_cpk_expense_category_user,cpk.expense.category.user,model_cpk_expense_category,base.group_user,1,0,0,0
access_cpk_expense_category_system,cpk.expense.category.system,model_cpk_expense_category,base.group_system,1,1,1,1
access_cpk_tax_code_user,cpk.tax.code.user,model_cpk_tax_code,base.group_user,1,0,0,0
access_cpk_tax_code_system,cpk.tax.code.system,model_cpk_tax_code,base.group_system,1,1,1,1
```

### 4.6 自動編號設定

```xml
<!-- data/sequence.xml -->
<odoo>
    <data noupdate="1">
        <record id="seq_cpk_reimburse" model="ir.sequence">
            <field name="name">費用請款單編號</field>
            <field name="code">cpk.reimburse</field>
            <field name="prefix">RE</field>
            <field name="suffix">%(year)s%(month)s</field>
            <field name="padding">4</field>
            <field name="number_next">1</field>
            <field name="number_increment">1</field>
            <field name="company_id" eval="False"/>
        </record>
    </data>
</odoo>
```

編號格式範例：`RE2024120001`、`RE2024120002`

---

## 5. 樞紐分析報表開發

### 5.1 樞紐分析概述

樞紐分析表是 Odoo 內建的強大資料分析工具，可以快速產生各種統計報表。

**主要特色**：
- 即時資料分析
- 互動式操作介面
- 支援分組和篩選
- 可匯出為 Excel
- 支援圖表顯示

### 5.2 建立樞紐分析檢視

```xml
<!-- views/reimburse_views.xml -->
<record id="view_cpk_reimburse_pivot" model="ir.ui.view">
    <field name="name">cpk.reimburse.pivot</field>
    <field name="model">cpk.reimburse</field>
    <field name="arch" type="xml">
        <pivot string="費用請款分析" sample="1">
            <!-- 列分組 -->
            <field name="employee_id" type="row"/>
            <field name="reimburse_date" type="row" interval="month"/>
            
            <!-- 欄分組 -->
            <field name="state" type="col"/>
            
            <!-- 度量 -->
            <field name="total_amount" type="measure"/>
            <field name="total_tax" type="measure"/>
            <field name="id" string="單據筆數" type="measure"/>
        </pivot>
    </field>
</record>
```

### 5.3 進階樞紐分析設定

#### 5.3.1 費用類別分析

```xml
<record id="view_expense_line_pivot" model="ir.ui.view">
    <field name="name">cpk.expense.line.pivot</field>
    <field name="model">cpk.expense.line</field>
    <field name="arch" type="xml">
        <pivot string="費用分類分析">
            <!-- 多階層分組 -->
            <field name="expense_category_id" type="row"/>
            <field name="cost_center_id" type="row"/>
            
            <!-- 時間分組 -->
            <field name="reimburse_id" invisible="1"/>
            <field name="create_date" type="col" interval="quarter"/>
            
            <!-- 度量欄位 -->
            <field name="amount_total" type="measure" string="含稅金額"/>
            <field name="amount_untaxed" type="measure" string="未稅金額"/>
            <field name="tax_amount" type="measure" string="稅額"/>
            
            <!-- 預設顯示設定 -->
            <field name="currency_id" invisible="1"/>
        </pivot>
    </field>
</record>
```

#### 5.3.2 樞紐分析客製化欄位

為了提供更好的分析體驗，可以加入計算欄位：

```python
# models/models.py (在 CpkExpenseLine 中新增)
class CpkExpenseLine(models.Model):
    # ... 其他欄位 ...
    
    # 分析用計算欄位
    year_month = fields.Char('年月', compute='_compute_year_month', store=True)
    expense_category_name = fields.Char('費用類別名稱', 
                                       related='expense_category_id.name', 
                                       store=True)
    department_name = fields.Char('部門名稱', 
                                 related='cost_center_id.name', 
                                 store=True)

    @api.depends('create_date')
    def _compute_year_month(self):
        for line in self:
            if line.create_date:
                line.year_month = line.create_date.strftime('%Y-%m')
            else:
                line.year_month = ''
```

### 5.4 圖表檢視整合

```xml
<record id="view_cpk_reimburse_graph" model="ir.ui.view">
    <field name="name">cpk.reimburse.graph</field>
    <field name="model">cpk.reimburse</field>
    <field name="arch" type="xml">
        <graph string="費用請款趨勢" type="line" sample="1">
            <field name="reimburse_date" interval="month"/>
            <field name="total_amount" type="measure"/>
            <field name="state" invisible="context.get('graph_groupbys', []) != ['state']"/>
        </graph>
    </field>
</record>
```

### 5.5 動作整合

```xml
<record id="action_cpk_reimburse_analysis" model="ir.actions.act_window">
    <field name="name">費用請款分析</field>
    <field name="res_model">cpk.reimburse</field>
    <field name="view_mode">pivot,graph</field>
    <field name="context">{
        'search_default_this_year': 1,
        'group_by': ['employee_id', 'reimburse_date:month']
    }</field>
</record>

<menuitem id="menu_cpk_reimburse_analysis" 
          name="費用分析" 
          parent="menu_cpk_reimburse_root"
          action="action_cpk_reimburse_analysis" 
          sequence="20"/>
```

---

## 6. Qweb 報表設計與實作

### 6.1 Qweb 報表概述

QWeb 是 Odoo 的模板引擎，用於產生 HTML 格式的報表，可輸出為 PDF 或網頁。

**特色**：
- 基於 XML 模板
- 支援 Python 表達式
- 內建 CSS 樣式
- 支援頁首頁尾
- 可嵌入圖片和表格

### 6.2 報表動作定義

```xml
<!-- reports/reimburse_report_template.xml -->
<odoo>
    <!-- 報表動作 -->
    <record id="action_report_cpk_reimburse" model="ir.actions.report">
        <field name="name">費用請款單</field>
        <field name="model">cpk.reimburse</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">cpk_reimburse.report_reimburse_document</field>
        <field name="report_file">cpk_reimburse.report_reimburse_document</field>
        <field name="print_report_name">'費用請款單 - %s' % object.name</field>
        <field name="binding_model_id" ref="model_cpk_reimburse"/>
        <field name="binding_type">report</field>
    </record>
```

### 6.3 主報表模板

```xml
<!-- 主報表模板 -->
<template id="report_reimburse_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <t t-call="web.external_layout">
                <div class="page">
                    <div class="oe_structure"/>
                    
                    <!-- 報表標題 -->
                    <div class="row">
                        <div class="col-12 text-center">
                            <h2>費用請款單</h2>
                        </div>
                    </div>
                    
                    <!-- 基本資訊 -->
                    <div class="row mt32">
                        <div class="col-6">
                            <strong>請款單號：</strong>
                            <span t-field="o.name"/>
                        </div>
                        <div class="col-6">
                            <strong>請款日期：</strong>
                            <span t-field="o.reimburse_date"/>
                        </div>
                    </div>
                    
                    <div class="row mt8">
                        <div class="col-6">
                            <strong>請款人員：</strong>
                            <span t-field="o.employee_id.name"/>
                        </div>
                        <div class="col-6">
                            <strong>付款對象：</strong>
                            <span t-field="o.partner_id.name"/>
                        </div>
                    </div>
                    
                    <div class="row mt8">
                        <div class="col-6">
                            <strong>付款方式：</strong>
                            <span t-field="o.payment_method_id.name"/>
                        </div>
                        <div class="col-6">
                            <strong>到期日：</strong>
                            <span t-field="o.due_date"/>
                        </div>
                    </div>

                    <!-- 請款明細表格 -->
                    <div class="row mt32">
                        <div class="col-12">
                            <h4>請款明細</h4>
                            <table class="table table-sm table-bordered">
                                <thead>
                                    <tr class="table-active">
                                        <th>項次</th>
                                        <th>費用類別</th>
                                        <th>成本中心</th>
                                        <th>未稅金額</th>
                                        <th>稅額</th>
                                        <th>含稅金額</th>
                                        <th>說明</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <t t-foreach="o.expense_line_ids" t-as="line">
                                        <tr>
                                            <td><span t-esc="line_index + 1"/></td>
                                            <td><span t-field="line.expense_category_id.name"/></td>
                                            <td><span t-field="line.cost_center_id.name"/></td>
                                            <td class="text-right">
                                                <span t-field="line.amount_untaxed" 
                                                      t-options="{'widget': 'monetary', 'display_currency': o.currency_id}"/>
                                            </td>
                                            <td class="text-right">
                                                <span t-field="line.tax_amount" 
                                                      t-options="{'widget': 'monetary', 'display_currency': o.currency_id}"/>
                                            </td>
                                            <td class="text-right">
                                                <span t-field="line.amount_total" 
                                                      t-options="{'widget': 'monetary', 'display_currency': o.currency_id}"/>
                                            </td>
                                            <td><span t-field="line.description"/></td>
                                        </tr>
                                    </t>
                                </tbody>
                                <tfoot>
                                    <tr class="table-active">
                                        <th colspan="5" class="text-right">合計：</th>
                                        <th class="text-right">
                                            <span t-field="o.total_amount" 
                                                  t-options="{'widget': 'monetary', 'display_currency': o.currency_id}"/>
                                        </th>
                                        <th></th>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>

                    <!-- 憑證資訊 -->
                    <div class="row mt32" t-if="o.voucher_ids">
                        <div class="col-12">
                            <h4>憑證資訊</h4>
                            <table class="table table-sm table-bordered">
                                <thead>
                                    <tr class="table-active">
                                        <th>憑證類型</th>
                                        <th>發票日期</th>
                                        <th>發票號碼</th>
                                        <th>統一編號</th>
                                        <th>含稅金額</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <t t-foreach="o.voucher_ids" t-as="voucher">
                                        <tr>
                                            <td>
                                                <span t-if="voucher.voucher_type == 'invoice'">發票</span>
                                                <span t-else="">收據</span>
                                            </td>
                                            <td><span t-field="voucher.invoice_date"/></td>
                                            <td><span t-field="voucher.invoice_number"/></td>
                                            <td><span t-field="voucher.tax_id"/></td>
                                            <td class="text-right">
                                                <span t-field="voucher.amount_total" 
                                                      t-options="{'widget': 'monetary', 'display_currency': voucher.currency_id}"/>
                                            </td>
                                        </tr>
                                    </t>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- 簽核欄 -->
                    <div class="row mt32">
                        <div class="col-3 text-center">
                            <div style="border: 1px solid black; height: 80px; padding: 10px;">
                                <strong>申請人</strong><br/>
                                <span t-field="o.employee_id.name"/>
                            </div>
                        </div>
                        <div class="col-3 text-center">
                            <div style="border: 1px solid black; height: 80px; padding: 10px;">
                                <strong>單位主管</strong><br/>
                                <br/>
                            </div>
                        </div>
                        <div class="col-3 text-center">
                            <div style="border: 1px solid black; height: 80px; padding: 10px;">
                                <strong>財務主管</strong><br/>
                                <br/>
                            </div>
                        </div>
                        <div class="col-3 text-center">
                            <div style="border: 1px solid black; height: 80px; padding: 10px;">
                                <strong>總經理</strong><br/>
                                <br/>
                            </div>
                        </div>
                    </div>

                    <!-- 備註 -->
                    <div class="row mt16" t-if="o.notes">
                        <div class="col-12">
                            <strong>備註：</strong><br/>
                            <span t-field="o.notes"/>
                        </div>
                    </div>
                    
                    <div class="oe_structure"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 6.4 自訂樣式

```xml
<template id="report_reimburse_style" inherit_id="web.report_assets_common">
    <xpath expr="." position="inside">
        <style type="text/css">
            .reimburse-header {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            
            .signature-box {
                border: 2px solid #333;
                height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 5px;
            }
            
            .amount-highlight {
                background-color: #fff3cd;
                font-weight: bold;
            }
            
            @media print {
                .page-break {
                    page-break-after: always;
                }
            }
        </style>
    </xpath>
</template>
```

### 6.5 條件式報表內容

```xml
<!-- 條件顯示範例 -->
<div class="row" t-if="o.state in ['approved', 'paid']">
    <div class="col-12 alert alert-success">
        <strong>審核通過</strong> - 此請款單已獲得審核通過
    </div>
</div>

<div class="row" t-if="o.state == 'draft'">
    <div class="col-12 alert alert-warning">
        <strong>草稿狀態</strong> - 此為草稿列印，非正式單據
    </div>
</div>

<!-- 迴圈與計算 -->
<t t-set="total_lines" t-value="len(o.expense_line_ids)"/>
<p>本單共 <span t-esc="total_lines"/> 筆明細</p>

<!-- 格式化選項 -->
<span t-field="o.total_amount" 
      t-options="{'widget': 'monetary', 
                  'display_currency': o.currency_id,
                  'precision': 2}"/>
```

### 6.6 多頁報表處理

```xml
<!-- 分頁處理 -->
<t t-foreach="docs" t-as="o">
    <t t-call="web.external_layout">
        <div class="page">
            <!-- 第一頁內容 -->
            <div class="page-content">
                <!-- 基本資訊和摘要 -->
            </div>
        </div>
        
        <!-- 詳細明細（可能跨頁） -->
        <t t-if="len(o.expense_line_ids) > 10">
            <div class="page page-break">
                <div class="page-content">
                    <!-- 明細表格 -->
                </div>
            </div>
        </t>
    </t>
</t>
```

---

## 7. Wizard 精靈開發

### 7.1 Wizard 概述

Wizard（精靈）是 Odoo 中用於處理複雜業務邏輯的暫時性視窗，通常用於：
- 批次操作
- 報表參數設定
- 資料匯入匯出
- 複雜的業務流程

### 7.2 建立列印精靈模型

```python
# models/reimburse_print_wizard.py
from odoo import models, fields, api

class ReimbursePrintWizard(models.TransientModel):
    _name = 'cpk.reimburse.print.wizard'
    _description = '費用請款單列印精靈'

    # 選取的請款單
    reimburse_ids = fields.Many2many('cpk.reimburse', string='請款單')
    
    # 列印選項
    print_mode = fields.Selection([
        ('single', '單張列印'),
        ('batch', '批次列印'),
        ('summary', '彙總報表'),
    ], string='列印模式', default='single', required=True)
    
    # 報表格式選項
    include_voucher = fields.Boolean('包含憑證明細', default=True)
    include_signature = fields.Boolean('包含簽核欄', default=True)
    print_draft = fields.Boolean('允許列印草稿', default=False)
    
    # 日期範圍（用於批次列印）
    date_from = fields.Date('開始日期')
    date_to = fields.Date('結束日期')
    
    # 其他篩選條件
    employee_ids = fields.Many2many('hr.employee', string='請款人員')
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('approved', '已審核'),
    ], string='狀態')

    @api.model
    def default_get(self, fields_list):
        """預設值設定"""
        res = super().default_get(fields_list)
        
        # 從 context 取得選取的記錄
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['reimburse_ids'] = [(6, 0, active_ids)]
            
        return res

    def action_print_report(self):
        """執行列印動作"""
        self.ensure_one()
        
        # 根據列印模式決定要列印的記錄
        if self.print_mode == 'single':
            records = self.reimburse_ids
        elif self.print_mode == 'batch':
            records = self._get_batch_records()
        else:  # summary
            return self._print_summary_report()
        
        # 狀態檢查
        if not self.print_draft:
            draft_records = records.filtered(lambda r: r.state == 'draft')
            if draft_records:
                raise ValidationError(
                    f'以下請款單為草稿狀態，無法列印：\n'
                    f'{", ".join(draft_records.mapped("name"))}'
                )
        
        # 更新列印狀態
        records.write({'is_printed': True})
        
        # 產生報表
        return self.env.ref('cpk_reimburse.action_report_cpk_reimburse').report_action(records)

    def _get_batch_records(self):
        """取得批次列印的記錄"""
        domain = []
        
        # 日期範圍
        if self.date_from:
            domain.append(('reimburse_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('reimburse_date', '<=', self.date_to))
            
        # 請款人員
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
            
        # 狀態
        if self.state:
            domain.append(('state', '=', self.state))
            
        return self.env['cpk.reimburse'].search(domain)

    def _print_summary_report(self):
        """列印彙總報表"""
        # 建立彙總報表的邏輯
        return {
            'type': 'ir.actions.report',
            'report_name': 'cpk_reimburse.report_reimburse_summary',
            'report_type': 'qweb-pdf',
            'data': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_ids': self.employee_ids.ids,
            },
            'context': self.env.context,
        }

    def action_preview_report(self):
        """預覽報表（HTML 格式）"""
        records = self.reimburse_ids
        return self.env.ref('cpk_reimburse.action_report_cpk_reimburse').report_action(
            records, config={'print_mode': 'preview'}
        )
```

### 7.3 Wizard 視圖設計

```xml
<!-- views/reimburse_print_wizard_views.xml -->
<record id="view_reimburse_print_wizard_form" model="ir.ui.view">
    <field name="name">cpk.reimburse.print.wizard.form</field>
    <field name="model">cpk.reimburse.print.wizard</field>
    <field name="arch" type="xml">
        <form string="費用請款單列印設定">
            <group>
                <group name="print_options">
                    <field name="print_mode" widget="radio"/>
                    <field name="include_voucher"/>
                    <field name="include_signature"/>
                    <field name="print_draft"/>
                </group>
                <group name="selection">
                    <field name="reimburse_ids" widget="many2many_tags" 
                           attrs="{'invisible': [('print_mode', '!=', 'single')]}"/>
                    
                    <!-- 批次列印條件 -->
                    <div attrs="{'invisible': [('print_mode', '!=', 'batch')]}">
                        <field name="date_from"/>
                        <field name="date_to"/>
                        <field name="employee_ids" widget="many2many_tags"/>
                        <field name="state"/>
                    </div>
                </group>
            </group>
            
            <!-- 預覽區域 -->
            <group string="預覽資訊" 
                   attrs="{'invisible': [('print_mode', '==', 'summary')]}">
                <field name="reimburse_ids" readonly="1" nolabel="1">
                    <tree>
                        <field name="name"/>
                        <field name="employee_id"/>
                        <field name="total_amount"/>
                        <field name="state" widget="badge"/>
                    </tree>
                </field>
            </group>
            
            <footer>
                <button name="action_print_report" string="列印" 
                        type="object" class="btn-primary"/>
                <button name="action_preview_report" string="預覽" 
                        type="object" class="btn-secondary"/>
                <button string="取消" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

### 7.4 Wizard 動作定義

```xml
<!-- Wizard 動作 -->
<record id="action_cpk_reimburse_print_wizard" model="ir.actions.act_window">
    <field name="name">列印費用請款單</field>
    <field name="res_model">cpk.reimburse.print.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="binding_model_id" ref="model_cpk_reimburse"/>
    <field name="binding_view_types">list,form</field>
</record>
```

### 7.5 進階 Wizard 功能

#### 7.5.1 多步驟 Wizard

```python
class ReimburseMultiStepWizard(models.TransientModel):
    _name = 'cpk.reimburse.multi.wizard'
    _description = '多步驟處理精靈'

    step = fields.Selection([
        ('step1', '選擇條件'),
        ('step2', '確認資料'),
        ('step3', '處理結果'),
    ], default='step1')
    
    # 步驟 1 欄位
    selection_criteria = fields.Text('選擇條件')
    
    # 步驟 2 欄位
    preview_data = fields.Text('預覽資料')
    
    # 步驟 3 欄位
    result_summary = fields.Text('處理結果')

    def action_next_step(self):
        """下一步"""
        if self.step == 'step1':
            self.step = 'step2'
            self._prepare_step2_data()
        elif self.step == 'step2':
            self.step = 'step3'
            self._execute_process()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous_step(self):
        """上一步"""
        if self.step == 'step2':
            self.step = 'step1'
        elif self.step == 'step3':
            self.step = 'step2'
        
        return self.action_next_step()
```

#### 7.5.2 檔案匯出 Wizard

```python
import base64
import io
from odoo.tools import pycompat

class ReimburseExportWizard(models.TransientModel):
    _name = 'cpk.reimburse.export.wizard'
    _description = '費用請款匯出精靈'

    export_format = fields.Selection([
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ], string='匯出格式', required=True)
    
    include_fields = fields.Many2many(
        'ir.model.fields',
        domain="[('model', '=', 'cpk.reimburse')]",
        string='包含欄位'
    )
    
    export_file = fields.Binary('匯出檔案', readonly=True)
    export_filename = fields.Char('檔案名稱', readonly=True)

    def action_export(self):
        """執行匯出"""
        records = self.env['cpk.reimburse'].browse(
            self.env.context.get('active_ids', [])
        )
        
        if self.export_format == 'excel':
            return self._export_excel(records)
        elif self.export_format == 'csv':
            return self._export_csv(records)
        else:
            return self._export_pdf(records)

    def _export_excel(self, records):
        """匯出為 Excel"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError('請安裝 xlsxwriter 套件：pip install xlsxwriter')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('費用請款單')
        
        # 寫入標題列
        headers = ['請款單號', '請款人員', '請款日期', '總金額', '狀態']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # 寫入資料
        for row, record in enumerate(records, 1):
            worksheet.write(row, 0, record.name)
            worksheet.write(row, 1, record.employee_id.name)
            worksheet.write(row, 2, record.reimburse_date.strftime('%Y-%m-%d') if record.reimburse_date else '')
            worksheet.write(row, 3, record.total_amount)
            worksheet.write(row, 4, dict(record._fields['state'].selection)[record.state])
        
        workbook.close()
        output.seek(0)
        
        self.export_file = base64.b64encode(output.read())
        self.export_filename = f'費用請款單_{fields.Date.today().strftime("%Y%m%d")}.xlsx'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
```

---

## 8. Excel 匯入功能開發

### 8.1 Excel 匯入功能概述

Excel 匯入功能是企業級 ERP 系統的重要功能，可以大幅提升資料輸入效率。在 cpk_reimburse 模組中，我們實作了同時匯入憑證資料和請款明細的功能。

**主要特色**：
- 支援 Excel (.xlsx) 檔案格式
- 一個 Excel 檔案包含兩個工作表（憑證資料、請款明細）
- 提供範例檔案下載功能
- 完整的資料驗證和錯誤處理
- 支援替換或附加匯入模式

### 8.2 TransientModel 設計

Excel 匯入使用 TransientModel（暫時性模型）來處理匯入邏輯：

```python
# wizard/excel_import_wizard.py
class ExcelImportWizard(models.TransientModel):
    _name = 'cpk.reimburse.excel.import.wizard'
    _description = 'Excel 匯入憑證與請款明細精靈'

    # 基本欄位
    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', required=True)
    import_file = fields.Binary('Excel 檔案', required=True)
    import_filename = fields.Char('檔案名稱')
    
    # 匯入選項
    import_mode = fields.Selection([
        ('replace', '替換現有資料'),
        ('append', '附加到現有資料'),
    ], string='匯入模式', default='append', required=True)
    
    # 範例檔案
    template_file = fields.Binary('範例檔案', readonly=True)
    template_filename = fields.Char('範例檔案名稱', readonly=True)
    
    # 匯入結果
    import_log = fields.Text('匯入結果', readonly=True)
    voucher_count = fields.Integer('憑證數量', readonly=True)
    expense_line_count = fields.Integer('請款明細數量', readonly=True)
```

### 8.3 範例檔案產生功能

使用 xlsxwriter 套件產生專業的 Excel 範例檔案：

```python
def _generate_template_file(self):
    """產生範例 Excel 檔案"""
    if not xlsxwriter:
        raise UserError(_('請安裝 xlsxwriter 套件：pip install xlsxwriter'))

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # 定義樣式
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4CAF50',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    required_format = workbook.add_format({
        'bold': True,
        'bg_color': '#FFC107',
        'font_color': 'black',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    example_format = workbook.add_format({
        'bg_color': '#E8F5E8',
        'border': 1
    })

    # Sheet 1: 憑證資料
    voucher_sheet = workbook.add_worksheet('憑證資料')
    
    # 憑證表頭（* 表示必填）
    voucher_headers = [
        '憑證類型*', '發票日期', '發票號碼', '統一編號', 
        '稅碼', '交易幣別*', '含稅金額*', '未稅金額', '稅額'
    ]
    
    for col, header in enumerate(voucher_headers):
        if '*' in header:
            voucher_sheet.write(0, col, header, required_format)
        else:
            voucher_sheet.write(0, col, header, header_format)
    
    # 憑證範例資料
    voucher_examples = [
        ['invoice', '2024-01-15', 'AB12345678', '12345678', 'VA', 'TWD', 1050, 1000, 50],
        ['receipt', '2024-01-16', 'RC001', '', 'VN', 'TWD', 500, 500, 0],
    ]
    
    for row, example in enumerate(voucher_examples, 1):
        for col, value in enumerate(example):
            voucher_sheet.write(row, col, value, example_format)
    
    # Sheet 2: 請款明細
    expense_sheet = workbook.add_worksheet('請款明細')
    
    expense_headers = [
        '憑證序號*', '費用類別代碼*', '成本中心', '專案代號', 
        '含稅金額*', '未稅金額', '稅額', '費用說明'
    ]
    
    # 請款明細範例資料
    expense_examples = [
        [1, '0101', '資訊部', 'PRJ001', 525, 500, 25, '計程車車資'],
        [1, '0102', '資訊部', 'PRJ001', 525, 500, 25, '停車費'],
        [2, '0201', '業務部', '', 500, 500, 0, '餐費'],
    ]
    
    workbook.close()
    output.seek(0)
    
    template_file = base64.b64encode(output.read())
    template_filename = f'憑證匯入範例_{fields.Date.today().strftime("%Y%m%d")}.xlsx'
    
    return template_file, template_filename
```

### 8.4 Excel 檔案讀取和驗證

使用 openpyxl 套件讀取 Excel 檔案並進行資料驗證：

```python
def action_import_excel(self):
    """執行 Excel 匯入"""
    if not openpyxl:
        raise UserError(_('請安裝 openpyxl 套件：pip install openpyxl'))
    
    try:
        # 解碼並讀取 Excel 檔案
        excel_data = base64.b64decode(self.import_file)
        workbook = openpyxl.load_workbook(io.BytesIO(excel_data), data_only=True)
        
        # 檢查工作表
        if '憑證資料' not in workbook.sheetnames:
            raise ValidationError(_('Excel 檔案中找不到「憑證資料」工作表'))
        if '請款明細' not in workbook.sheetnames:
            raise ValidationError(_('Excel 檔案中找不到「請款明細」工作表'))
        
        # 匯入前清理（如果選擇替換模式）
        if self.import_mode == 'replace':
            self.reimburse_id.voucher_ids.unlink()
            self.reimburse_id.expense_line_ids.unlink()
        
        # 匯入憑證資料
        voucher_sheet = workbook['憑證資料']
        vouchers = self._import_vouchers(voucher_sheet)
        
        # 匯入請款明細
        expense_sheet = workbook['請款明細']
        expense_lines = self._import_expense_lines(expense_sheet, vouchers)
        
        # 產生匯入報告
        self._generate_import_report(vouchers, expense_lines)
        
    except Exception as e:
        _logger.error(f'Excel 匯入錯誤: {str(e)}')
        raise UserError(_('匯入失敗：%s') % str(e))
```

### 8.5 憑證資料匯入邏輯

```python
def _import_vouchers(self, sheet):
    """匯入憑證資料"""
    vouchers = []
    errors = []
    
    # 取得系統中的參考資料
    tax_codes = {tc.code: tc.id for tc in self.env['cpk.tax.code'].search([])}
    currencies = {c.name: c.id for c in self.env['res.currency'].search([])}
    
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
        if not any(row):  # 跳過空行
            continue
        
        try:
            voucher_type, invoice_date, invoice_number, tax_id, tax_code, \
            currency, amount_total, amount_untaxed, tax_amount = row[:9]
            
            # 驗證必填欄位
            if not voucher_type:
                errors.append(f'行 {row_num}：憑證類型為必填')
                continue
            
            if voucher_type not in ['invoice', 'receipt']:
                errors.append(f'行 {row_num}：憑證類型必須是 invoice 或 receipt')
                continue
            
            # 建立憑證資料
            voucher_vals = {
                'reimburse_id': self.reimburse_id.id,
                'voucher_type': voucher_type,
                'amount_total': float(amount_total) if amount_total else 0,
                # ... 其他欄位處理
            }
            
            voucher = self.env['cpk.voucher'].create(voucher_vals)
            vouchers.append((row_num, voucher))
            
        except Exception as e:
            errors.append(f'行 {row_num}：{str(e)}')
            continue
    
    if errors:
        raise ValidationError(_('憑證資料匯入錯誤：\n%s') % '\n'.join(errors))
    
    return vouchers
```

### 8.6 請款明細匯入邏輯

```python
def _import_expense_lines(self, sheet, vouchers):
    """匯入請款明細"""
    expense_lines = []
    errors = []
    
    # 建立憑證索引對照
    voucher_map = {row_num: voucher for row_num, voucher in vouchers}
    
    # 取得系統參考資料
    expense_categories = {ec.code: ec.id for ec in self.env['cpk.expense.category'].search([])}
    departments = {dept.name: dept.id for dept in self.env['hr.department'].search([])}
    
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
        if not any(row):
            continue
        
        try:
            voucher_seq, category_code, cost_center, project_code, \
            amount_total, amount_untaxed, tax_amount, description = row[:8]
            
            # 驗證憑證序號對應
            voucher_row_num = int(voucher_seq) + 1  # Excel 行號轉換
            if voucher_row_num not in voucher_map:
                errors.append(f'行 {row_num}：找不到憑證序號 {voucher_seq} 對應的憑證')
                continue
            
            # 驗證費用類別
            if category_code not in expense_categories:
                errors.append(f'行 {row_num}：找不到費用類別代碼 {category_code}')
                continue
            
            # 建立請款明細
            expense_vals = {
                'reimburse_id': self.reimburse_id.id,
                'voucher_id': voucher_map[voucher_row_num].id,
                'expense_category_id': expense_categories[category_code],
                'amount_total': float(amount_total) if amount_total else 0,
                # ... 其他欄位處理
            }
            
            expense_line = self.env['cpk.expense.line'].create(expense_vals)
            expense_lines.append(expense_line)
            
        except Exception as e:
            errors.append(f'行 {row_num}：{str(e)}')
            continue
    
    return expense_lines
```

### 8.7 Wizard 視圖設計

```xml
<!-- wizard/excel_import_wizard_views.xml -->
<record id="view_excel_import_wizard_form" model="ir.ui.view">
    <field name="name">cpk.reimburse.excel.import.wizard.form</field>
    <field name="model">cpk.reimburse.excel.import.wizard</field>
    <field name="arch" type="xml">
        <form string="Excel 匯入憑證與請款明細">
            <!-- 說明區域 -->
            <div class="alert alert-info" role="alert" 
                 attrs="{'invisible': [('import_log', '!=', False)]}">
                <p><strong>Excel 匯入功能說明：</strong></p>
                <ul>
                    <li>支援一次匯入憑證資料和請款明細</li>
                    <li>Excel 檔案需包含「憑證資料」和「請款明細」兩個工作表</li>
                    <li>建議先下載範例檔案了解正確格式</li>
                    <li>憑證資料和請款明細會根據行號自動關聯</li>
                </ul>
            </div>

            <!-- 匯入成功訊息 -->
            <div class="alert alert-success" role="alert" 
                 attrs="{'invisible': [('import_log', '=', False)]}">
                <p><strong><i class="fa fa-check-circle"/> 匯入成功！</strong></p>
                <p>憑證數量：<field name="voucher_count"/> 筆</p>
                <p>請款明細：<field name="expense_line_count"/> 筆</p>
            </div>

            <!-- 匯入設定 -->
            <group attrs="{'invisible': [('import_log', '!=', False)]}">
                <group name="basic_info">
                    <field name="reimburse_id" readonly="1"/>
                    <field name="import_mode" widget="radio"/>
                </group>
                <group name="file_info">
                    <field name="import_file" filename="import_filename"/>
                    <field name="import_filename" invisible="1"/>
                </group>
            </group>

            <!-- 範例檔案下載 -->
            <group string="範例檔案下載" 
                   attrs="{'invisible': [('import_log', '!=', False)]}">
                <div class="alert alert-warning" role="alert">
                    <p><i class="fa fa-download"/> 建議先下載範例檔案，了解正確的匯入格式</p>
                </div>
                
                <div class="row" attrs="{'invisible': [('template_file', '=', False)]}">
                    <div class="col-12">
                        <field name="template_file" filename="template_filename" readonly="1"/>
                        <field name="template_filename" invisible="1"/>
                    </div>
                </div>
            </group>

            <!-- 匯入結果詳細資訊 -->
            <group string="匯入結果" attrs="{'invisible': [('import_log', '=', False)]}">
                <field name="import_log" nolabel="1" readonly="1" 
                       widget="text" style="height: 200px;"/>
            </group>

            <footer>
                <!-- 匯入前按鈕 -->
                <div attrs="{'invisible': [('import_log', '!=', False)]}">
                    <button name="action_download_template" string="下載範例檔案" 
                            type="object" class="btn-info"/>
                    <button name="action_import_excel" string="開始匯入" 
                            type="object" class="btn-primary"
                            attrs="{'invisible': [('import_file', '=', False)]}"/>
                    <button string="取消" class="btn-secondary" special="cancel"/>
                </div>
                
                <!-- 匯入後按鈕 -->
                <div attrs="{'invisible': [('import_log', '=', False)]}">
                    <button name="action_close" string="完成" 
                            type="object" class="btn-primary"/>
                </div>
            </footer>
        </form>
    </field>
</record>
```

### 8.8 整合到主要功能

在請款單的表單視圖中加入 Excel 匯入按鈕：

```xml
<header>
    <button name="%(action_cpk_reimburse_print_wizard)d" 
            string="列印" type="action" class="btn-primary"/>
    <button name="%(action_excel_import_wizard)d" 
            string="Excel匯入" type="action" class="btn-secondary" 
            attrs="{'invisible': [('state', 'not in', ['draft'])]}"/>
    <field name="state" widget="statusbar" 
           statusbar_visible="draft,confirmed,submitted,approved,paid,closed"/>
</header>
```

### 8.9 錯誤處理和驗證

Excel 匯入功能包含完整的錯誤處理機制：

**資料驗證**：
- 必填欄位檢查
- 資料型別驗證
- 外鍵關聯檢查
- 業務邏輯驗證

**錯誤回報**：
- 詳細的錯誤訊息（包含行號）
- 批次驗證（一次顯示所有錯誤）
- 友善的使用者介面提示

**範例錯誤處理**：
```python
errors = []

# 驗證必填欄位
if not voucher_type:
    errors.append(f'行 {row_num}：憑證類型為必填')

# 驗證選項值
if voucher_type not in ['invoice', 'receipt']:
    errors.append(f'行 {row_num}：憑證類型必須是 invoice 或 receipt')

# 驗證金額邏輯
if amount_total and amount_untaxed and tax_amount:
    if abs(amount_total - amount_untaxed - tax_amount) > 0.01:
        errors.append(f'行 {row_num}：金額計算錯誤，含稅金額 ≠ 未稅金額 + 稅額')

# 統一回報錯誤
if errors:
    raise ValidationError(_('匯入錯誤：\n%s') % '\n'.join(errors))
```

### 8.10 依賴套件安裝

Excel 匯入功能需要安裝額外的 Python 套件：

```bash
# 安裝 Excel 讀取套件
pip install openpyxl

# 安裝 Excel 寫入套件  
pip install xlsxwriter
```

**套件說明**：
- **openpyxl**：用於讀取 Excel 檔案
- **xlsxwriter**：用於產生範例 Excel 檔案

### 8.11 使用流程

1. **開啟請款單** → 點擊「Excel匯入」按鈕
2. **下載範例檔案** → 了解正確的資料格式
3. **準備資料** → 填入憑證資料和請款明細
4. **選擇匯入模式** → 替換或附加現有資料
5. **上傳檔案** → 選擇準備好的 Excel 檔案
6. **執行匯入** → 系統自動處理和驗證資料
7. **查看結果** → 確認匯入的憑證和明細資料

這個 Excel 匯入功能大幅提升了資料輸入效率，特別適用於批次處理大量費用請款資料的場景。

---

## 9. One2many/Many2many Dialog 機制

### 9.1 Dialog 顯示原理

當在 One2many 欄位的 tree view 中點擊「加入資料行」時，Odoo 會自動尋找該關聯模型的 form view 作為對話框內容。

**搜尋優先順序**：
1. **內嵌 form** > 具名 form > 預設 form
2. **form_view_ref 指定的 form** > 預設 form  
3. **系統預設的 form view**

### 9.2 三種 Dialog 定義方式

#### 9.2.1 方式 1：內嵌 form（推薦用於簡單對話框）

```xml
<field name="expense_line_ids">
    <tree editable="bottom">
        <field name="expense_category_id"/>
        <field name="amount_total"/>
        <field name="description"/>
    </tree>
    <form>
        <!-- 這就是對話框的內容 -->
        <group>
            <field name="expense_category_id"/>
            <field name="cost_center_id"/>
            <field name="amount_untaxed"/>
            <field name="tax_amount"/>
            <field name="amount_total"/>
            <field name="description"/>
        </group>
    </form>
</field>
```

#### 9.2.2 方式 2：引用具名 form

```xml
<!-- 先定義具名 form view -->
<record id="view_expense_line_dialog_form" model="ir.ui.view">
    <field name="name">cpk.expense.line.dialog.form</field>
    <field name="model">cpk.expense.line</field>
    <field name="arch" type="xml">
        <form string="請款明細">
            <group>
                <group>
                    <field name="expense_category_id"/>
                    <field name="cost_center_id"/>
                    <field name="analytic_account_id"/>
                </group>
                <group>
                    <field name="amount_untaxed"/>
                    <field name="tax_amount"/>
                    <field name="amount_total"/>
                </group>
            </group>
            <field name="description"/>
            <!-- 隱藏不需要用戶輸入的欄位 -->
            <field name="reimburse_id" invisible="1"/>
        </form>
    </field>
</record>

<!-- 然後在 One2many 中引用 -->
<field name="expense_line_ids" form_view_ref="view_expense_line_dialog_form">
    <tree editable="bottom">
        <field name="expense_category_id"/>
        <field name="amount_total"/>
        <field name="description"/>
    </tree>
</field>
```

#### 9.2.3 方式 3：使用系統預設 form

```xml
<!-- 不指定 form，系統會自動使用預設的 form view -->
<field name="expense_line_ids">
    <tree editable="bottom">
        <field name="expense_category_id"/>
        <field name="amount_total"/>
        <field name="description"/>
    </tree>
</field>

<!-- 系統會自動使用這個預設的 form view -->
<record id="view_expense_line_form" model="ir.ui.view">
    <field name="name">cpk.expense.line.form</field>
    <field name="model">cpk.expense.line</field>
    <!-- ... form 內容 ... -->
</record>
```

### 9.3 Context 參數傳遞

```xml
<!-- 傳遞預設值到對話框 -->
<field name="expense_line_ids" context="{'default_reimburse_id': id}">
    <tree>
        <field name="expense_category_id"/>
        <field name="amount_total"/>
    </tree>
    <form>
        <group>
            <field name="expense_category_id"/>
            <field name="amount_total"/>
            <!-- 這個欄位會自動帶入父記錄的 id -->
            <field name="reimburse_id" invisible="1"/>
        </group>
    </form>
</field>
```

### 9.4 憑證與明細的複雜 Dialog 範例

```xml
<!-- 複雜的憑證明細對話框 -->
<record id="view_voucher_with_lines_dialog_form" model="ir.ui.view">
    <field name="name">cpk.voucher.dialog.form</field>
    <field name="model">cpk.voucher</field>
    <field name="arch" type="xml">
        <form string="新增費用明細">
            <!-- 憑證資料（上半部） -->
            <group string="憑證資料">
                <group>
                    <field name="voucher_type"/>
                    <field name="invoice_date"/>
                    <field name="invoice_number"/>
                    <field name="tax_code_id"/>
                </group>
                <group>
                    <field name="currency_id"/>
                    <field name="amount_untaxed"/>
                    <field name="tax_amount"/>
                    <field name="amount_total"/>
                </group>
            </group>
            
            <!-- 憑證上傳 -->
            <group string="憑證上傳">
                <field name="attachment_ids" widget="many2many_binary"/>
            </group>
            
            <!-- 請款明細（下半部） -->
            <group string="請款明細">
                <field name="expense_line_ids" nolabel="1">
                    <tree editable="bottom">
                        <field name="sequence" widget="handle"/>
                        <field name="expense_category_id"/>
                        <field name="cost_center_id"/>
                        <field name="amount_untaxed"/>
                        <field name="tax_amount"/>
                        <field name="amount_total"/>
                        <field name="description"/>
                    </tree>
                </field>
            </group>
            
            <!-- 隱藏欄位 -->
            <field name="reimburse_id" invisible="1"/>
        </form>
    </field>
</record>
```

### 9.5 動態 Context 和條件顯示

```xml
<field name="voucher_ids" 
       context="{
           'default_reimburse_id': id,
           'default_currency_id': currency_id,
           'default_voucher_type': 'invoice',
           'tree_view_ref': 'cpk_reimburse.view_voucher_simple_tree'
       }">
    <tree>
        <field name="voucher_type"/>
        <field name="invoice_date"/>
        <field name="amount_total"/>
        <field name="currency_id" invisible="1"/>
    </tree>
    <form>
        <group>
            <field name="voucher_type"/>
            <field name="invoice_date" 
                   attrs="{'required': [('voucher_type', '=', 'invoice')]}"/>
            <field name="invoice_number" 
                   attrs="{'invisible': [('voucher_type', '=', 'receipt')]}"/>
        </group>
    </form>
</field>
```

### 9.6 JavaScript 客製化 Dialog

```javascript
// static/src/js/cpk_attachment_preview.js
odoo.define('cpk_reimburse.AttachmentPreview', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var AttachmentPreviewWidget = AbstractField.extend({
        template: 'CpkAttachmentPreview',
        
        events: {
            'click .o_attachment_preview': '_onPreviewAttachment',
            'click .o_attachment_download': '_onDownloadAttachment',
        },

        _render: function () {
            var attachments = this.value && this.value.data || [];
            this.$el.empty();
            
            attachments.forEach(function (attachment) {
                var $item = $(QWeb.render('CpkAttachmentPreviewItem', {
                    attachment: attachment,
                }));
                this.$el.append($item);
            }.bind(this));
        },

        _onPreviewAttachment: function (event) {
            event.preventDefault();
            var attachmentId = $(event.currentTarget).data('attachment-id');
            
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'ir.attachment',
                res_id: attachmentId,
                views: [[false, 'form']],
                target: 'new',
            });
        },

        _onDownloadAttachment: function (event) {
            event.preventDefault();
            var attachmentId = $(event.currentTarget).data('attachment-id');
            window.location = '/web/content/' + attachmentId + '?download=true';
        },
    });

    field_registry.add('cpk_attachment_preview', AttachmentPreviewWidget);

    return AttachmentPreviewWidget;
});
```

### 9.7 XML 模板

```xml
<!-- static/src/xml/cpk_attachment_preview.xml -->
<templates>
    <t t-name="CpkAttachmentPreview">
        <div class="o_attachment_preview_container">
            <t t-if="!widget.value || !widget.value.data.length">
                <div class="text-muted">尚未上傳憑證</div>
            </t>
        </div>
    </t>

    <t t-name="CpkAttachmentPreviewItem">
        <div class="o_attachment_item d-flex align-items-center mb-2">
            <div class="o_attachment_info flex-grow-1">
                <strong t-esc="attachment.name"/>
                <small class="text-muted d-block">
                    <t t-esc="attachment.file_size"/> bytes
                </small>
            </div>
            <div class="o_attachment_actions">
                <button type="button" 
                        class="btn btn-sm btn-outline-primary o_attachment_preview"
                        t-att-data-attachment-id="attachment.id">
                    預覽
                </button>
                <button type="button" 
                        class="btn btn-sm btn-outline-secondary o_attachment_download"
                        t-att-data-attachment-id="attachment.id">
                    下載
                </button>
            </div>
        </div>
    </t>
</templates>
```

---

## 10. 實務開發技巧

### 10.1 PyCharm 環境設定

#### 10.1.1 專案設定

PyCharm 會自動識別 Python 環境與依賴：

```bash
# 啟動指令設定
/Volumes/Mac/Cympotek/odoo教育訓練/odoo-saas-16.4/odoo-bin \
-c /Volumes/Mac/Cympotek/odoo教育訓練/odoo-saas-16.4/debian/odoo.conf
```

#### 9.1.2 程式碼品質工具

```python
# 使用 flake8 檢查程式碼品質
pip install flake8

# 使用 black 自動格式化
pip install black

# .flake8 設定檔
[flake8]
max-line-length = 88
exclude = .git,__pycache__,build,dist,migrations
ignore = E203,W503
```

### 9.2 模型設計最佳實務

#### 9.2.1 欄位命名規範

```python
class CpkReimburse(models.Model):
    # 正確：使用描述性名稱
    reimburse_date = fields.Date('請款日期')
    employee_id = fields.Many2one('hr.employee', '請款人員')
    
    # 避免：模糊不清的名稱
    # date = fields.Date('日期')  # 太模糊
    # user = fields.Many2one('res.users')  # 不明確
```

#### 9.2.2 計算欄位效能優化

```python
class CpkReimburse(models.Model):
    # 好的做法：使用 store=True 儲存計算結果
    total_amount = fields.Monetary(
        compute='_compute_amounts', 
        store=True,  # 儲存到資料庫
        currency_field='currency_id'
    )
    
    @api.depends('expense_line_ids.amount_total')
    def _compute_amounts(self):
        # 批次處理，避免 N+1 查詢問題
        for record in self:
            record.total_amount = sum(
                record.expense_line_ids.mapped('amount_total')
            )
    
    # 避免的做法：每次都重新計算
    # total_amount = fields.Monetary(compute='_compute_amounts')
```

#### 9.2.3 約束條件設計

```python
@api.constrains('due_date', 'reimburse_date')
def _check_due_date(self):
    """到期日不能早於請款日期"""
    for record in self:
        if record.due_date and record.reimburse_date:
            if record.due_date < record.reimburse_date:
                raise ValidationError(
                    f'到期日 ({record.due_date}) 不能早於請款日期 ({record.reimburse_date})'
                )

@api.constrains('total_amount')
def _check_amount_positive(self):
    """金額必須為正數"""
    for record in self:
        if record.total_amount <= 0:
            raise ValidationError('請款金額必須大於零')
```

### 9.3 視圖設計技巧

#### 9.3.1 響應式布局

```xml
<group>
    <group name="left_group" col="2">
        <field name="employee_id"/>
        <field name="reimburse_date"/>
    </group>
    <group name="right_group" col="2">
        <field name="currency_id"/>
        <field name="total_amount"/>
    </group>
</group>
```

#### 9.3.2 條件式欄位顯示

```xml
<field name="invoice_number" 
       attrs="{'invisible': [('voucher_type', '!=', 'invoice')],
               'required': [('voucher_type', '=', 'invoice')]}"/>

<field name="tax_code_id" 
       attrs="{'readonly': [('state', 'in', ['approved', 'paid'])]}"/>
```

#### 9.3.3 進階 Widget 使用

```xml
<!-- 金額顯示 -->
<field name="total_amount" widget="monetary" 
       options="{'currency_field': 'currency_id'}"/>

<!-- 多選標籤 -->
<field name="tag_ids" widget="many2many_tags" 
       options="{'color_field': 'color'}"/>

<!-- 進度條 -->
<field name="completion_rate" widget="progressbar"/>

<!-- 星級評分 -->
<field name="rating" widget="priority"/>

<!-- HTML 編輯器 -->
<field name="description" widget="html"/>
```

### 9.4 資料庫優化技巧

#### 9.4.1 索引設定

```python
class CpkReimburse(models.Model):
    _name = 'cpk.reimburse'
    
    # 在常用搜尋欄位上建立索引
    employee_id = fields.Many2one('hr.employee', index=True)
    reimburse_date = fields.Date(index=True)
    state = fields.Selection([...], index=True)
    
    # 複合索引
    _sql_constraints = [
        ('unique_employee_date', 
         'UNIQUE(employee_id, reimburse_date)',
         '同一員工不能在同一天建立多筆請款單'),
    ]
```

#### 9.4.2 批次操作

```python
# 好的做法：批次更新
def approve_multiple(self):
    """批次審核多筆請款單"""
    self.write({'state': 'approved', 'approved_date': fields.Datetime.now()})
    
    # 發送通知
    self.message_post(body='請款單已批次審核通過')

# 避免的做法：逐一處理
# for record in self:
#     record.state = 'approved'  # N 次資料庫寫入
```

### 9.5 安全性最佳實務

#### 9.5.1 SQL 注入防護

```python
# 正確：使用參數化查詢
def search_by_name(self, name):
    self.env.cr.execute("""
        SELECT id, name FROM cpk_reimburse 
        WHERE name ILIKE %s
    """, (f'%{name}%',))
    return self.env.cr.fetchall()

# 錯誤：直接字串拼接
# self.env.cr.execute(f"SELECT * FROM cpk_reimburse WHERE name='{name}'")
```

#### 9.5.2 權限檢查

```python
@api.model
def create(self, vals):
    """建立時檢查權限"""
    # 檢查是否為自己的員工記錄
    if vals.get('employee_id'):
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        if employee.user_id != self.env.user:
            raise AccessError('您只能為自己建立請款單')
    
    return super().create(vals)

def unlink(self):
    """刪除時檢查狀態"""
    if any(record.state != 'draft' for record in self):
        raise UserError('只能刪除草稿狀態的請款單')
    return super().unlink()
```

### 9.6 國際化支援

#### 9.6.1 多語言設定

```python
# models/models.py
from odoo import _, models, fields

class CpkReimburse(models.Model):
    name = fields.Char(_('Reimburse Number'))
    notes = fields.Text(_('Notes'))
    
    def action_confirm(self):
        self.message_post(body=_('Reimburse request has been confirmed.'))
```

#### 9.6.2 翻譯檔案

```po
# i18n/zh_TW.po
#: model:ir.model.fields,field_description:cpk_reimburse.field_cpk_reimburse__name
msgid "Reimburse Number"
msgstr "請款單號"

#: model:ir.model.fields,field_description:cpk_reimburse.field_cpk_reimburse__notes
msgid "Notes"
msgstr "備註"
```

### 9.7 測試撰寫

```python
# tests/test_reimburse.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCpkReimburse(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.employee = self.env['hr.employee'].create({
            'name': '測試員工',
            'user_id': self.env.user.id,
        })
        self.partner = self.env['res.partner'].create({
            'name': '測試供應商',
        })
    
    def test_create_reimburse(self):
        """測試建立請款單"""
        reimburse = self.env['cpk.reimburse'].create({
            'employee_id': self.employee.id,
            'partner_id': self.partner.id,
            'reimburse_date': '2024-01-01',
            'due_date': '2024-01-31',
        })
        
        self.assertEqual(reimburse.state, 'draft')
        self.assertTrue(reimburse.name.startswith('RE'))
    
    def test_amount_validation(self):
        """測試金額驗證"""
        with self.assertRaises(ValidationError):
            self.env['cpk.voucher'].create({
                'reimburse_id': 1,
                'amount_total': 100,
                'amount_untaxed': 200,  # 錯誤：未稅金額大於含稅金額
                'tax_amount': 10,
            })
```

---

## 11. 除錯與測試

### 10.1 Odoo 除錯技巧

#### 10.1.1 開發者模式功能

啟動開發者模式後可使用：
- **編輯檢視**：直接修改 XML 檢視
- **管理篩選器**：建立自訂搜尋條件
- **技術資訊**：查看模型、欄位資訊
- **執行程式碼**：直接執行 Python 程式碼

#### 10.1.2 日誌設定

```ini
# debian/odoo.conf
[logger_root]
level = INFO
handlers = console

[logger_werkzeug]
level = WARNING
handlers = console
qualname = werkzeug

[handler_console]
class = StreamHandler
args = (sys.stdout,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(pid)s %(levelname)s %(name)s: %(message)s
```

#### 10.1.3 Python 除錯

```python
# 在程式碼中加入除錯點
import pdb; pdb.set_trace()

# 或使用 Odoo 的除錯工具
import logging
_logger = logging.getLogger(__name__)

def _compute_amounts(self):
    _logger.info(f'Computing amounts for {self.name}')
    for record in self:
        _logger.debug(f'Processing record: {record.id}')
        # ... 業務邏輯 ...
```

### 10.2 單元測試

#### 10.2.1 基本測試結構

```python
# tests/__init__.py
from . import test_reimburse

# tests/test_reimburse.py
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError, AccessError

class TestReimburse(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        
        # 建立測試資料
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'user_id': cls.env.ref('base.user_admin').id,
        })
        
        cls.expense_category = cls.env['cpk.expense.category'].create({
            'name': '測試費用類別',
            'code': '0001',
        })

    def test_reimburse_creation(self):
        """測試請款單建立"""
        reimburse_form = Form(self.env['cpk.reimburse'])
        reimburse_form.employee_id = self.employee
        reimburse_form.reimburse_date = '2024-01-01'
        reimburse_form.due_date = '2024-01-31'
        
        reimburse = reimburse_form.save()
        
        self.assertEqual(reimburse.state, 'draft')
        self.assertTrue(reimburse.name.startswith('RE'))
        self.assertEqual(reimburse.employee_id, self.employee)

    def test_amount_calculation(self):
        """測試金額計算"""
        reimburse = self.env['cpk.reimburse'].create({
            'employee_id': self.employee.id,
            'reimburse_date': '2024-01-01',
            'due_date': '2024-01-31',
        })
        
        # 新增明細
        self.env['cpk.expense.line'].create([
            {
                'reimburse_id': reimburse.id,
                'expense_category_id': self.expense_category.id,
                'amount_total': 100,
                'tax_amount': 5,
            },
            {
                'reimburse_id': reimburse.id,
                'expense_category_id': self.expense_category.id,
                'amount_total': 200,
                'tax_amount': 10,
            }
        ])
        
        # 測試計算結果
        self.assertEqual(reimburse.total_amount, 300)
        self.assertEqual(reimburse.total_tax, 15)

    def test_validation_constraints(self):
        """測試資料驗證"""
        with self.assertRaises(ValidationError):
            self.env['cpk.voucher'].create({
                'reimburse_id': 1,
                'amount_total': 100,
                'amount_untaxed': 120,  # 錯誤：未稅 > 含稅
                'tax_amount': 10,
            })
```

#### 10.2.2 表單測試

```python
def test_form_interaction(self):
    """測試表單互動"""
    with Form(self.env['cpk.reimburse']) as reimburse_form:
        reimburse_form.employee_id = self.employee
        reimburse_form.reimburse_date = '2024-01-01'
        
        # 測試 onchange 方法
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'bank_ids': [(0, 0, {
                'bank_id': self.env['res.bank'].create({'name': 'Test Bank'}).id,
                'acc_number': '123456789',
            })]
        })
        
        reimburse_form.partner_id = partner
        # 檢查是否自動帶入銀行資訊
        self.assertTrue(reimburse_form.bank_id)
        self.assertEqual(reimburse_form.bank_account, '123456789')
        
        reimburse = reimburse_form.save()
        self.assertEqual(reimburse.partner_id, partner)
```

#### 10.2.3 權限測試

```python
def test_access_rights(self):
    """測試存取權限"""
    # 建立測試使用者
    test_user = self.env['res.users'].create({
        'name': 'Test User',
        'login': 'testuser',
        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
    })
    
    test_employee = self.env['hr.employee'].create({
        'name': 'Test Employee 2',
        'user_id': test_user.id,
    })
    
    # 建立其他使用者的請款單
    other_reimburse = self.env['cpk.reimburse'].create({
        'employee_id': self.employee.id,
        'reimburse_date': '2024-01-01',
        'due_date': '2024-01-31',
    })
    
    # 切換到測試使用者
    test_env = self.env(user=test_user)
    
    # 測試只能看到自己的資料
    accessible_records = test_env['cpk.reimburse'].search([])
    self.assertNotIn(other_reimburse, accessible_records)
```

### 10.3 整合測試

```python
def test_complete_workflow(self):
    """測試完整工作流程"""
    # 1. 建立請款單
    reimburse = self.env['cpk.reimburse'].create({
        'employee_id': self.employee.id,
        'reimburse_date': '2024-01-01',
        'due_date': '2024-01-31',
    })
    
    # 2. 新增憑證和明細
    voucher = self.env['cpk.voucher'].create({
        'reimburse_id': reimburse.id,
        'voucher_type': 'invoice',
        'amount_total': 1000,
        'amount_untaxed': 952,
        'tax_amount': 48,
    })
    
    expense_line = self.env['cpk.expense.line'].create({
        'reimburse_id': reimburse.id,
        'voucher_id': voucher.id,
        'expense_category_id': self.expense_category.id,
        'amount_total': 1000,
        'amount_untaxed': 952,
        'tax_amount': 48,
    })
    
    # 3. 檢查計算結果
    self.assertEqual(reimburse.total_amount, 1000)
    self.assertEqual(reimburse.total_tax, 48)
    
    # 4. 測試狀態變更
    reimburse.state = 'confirmed'
    self.assertEqual(reimburse.state, 'confirmed')
    
    # 5. 測試報表產生
    report_action = self.env.ref('cpk_reimburse.action_report_cpk_reimburse')
    report_html = report_action.render_qweb_html(reimburse.ids)
    self.assertTrue(report_html[0])
```

### 10.4 效能測試

```python
import time
from odoo.tests.common import TransactionCase

class TestPerformance(TransactionCase):
    
    def test_bulk_operations(self):
        """測試批次操作效能"""
        # 建立大量測試資料
        start_time = time.time()
        
        employees = self.env['hr.employee'].create([
            {'name': f'Employee {i}', 'user_id': self.env.user.id}
            for i in range(100)
        ])
        
        reimburses = self.env['cpk.reimburse'].create([
            {
                'employee_id': employees[i].id,
                'reimburse_date': '2024-01-01',
                'due_date': '2024-01-31',
            }
            for i in range(100)
        ])
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 測試搜尋效能
        start_time = time.time()
        found_records = self.env['cpk.reimburse'].search([
            ('reimburse_date', '=', '2024-01-01')
        ])
        end_time = time.time()
        search_time = end_time - start_time
        
        # 效能斷言（根據實際需求調整）
        self.assertLess(creation_time, 5.0, '批次建立時間應少於 5 秒')
        self.assertLess(search_time, 1.0, '搜尋時間應少於 1 秒')
        self.assertEqual(len(found_records), 100)
```

### 10.5 測試執行

```bash
# 執行所有測試
python odoo-bin -c debian/odoo.conf -d test_db --test-enable --stop-after-init

# 執行特定模組測試
python odoo-bin -c debian/odoo.conf -d test_db --test-enable --stop-after-init -i cpk_reimburse

# 執行特定測試類別
python odoo-bin -c debian/odoo.conf -d test_db --test-enable --stop-after-init --test-tags cpk_reimburse
```

---

## 總結

本教育訓練教材涵蓋了 Odoo 16 ERP 客製開發的完整流程，以 `cpk_reimburse` 費用請款模組作為實際範例，從基礎環境設定到進階功能實作都有詳細說明。

**核心學習重點**：
1. **模組化架構**：理解 Odoo 的模組化設計理念
2. **MVC 架構**：掌握 Model-View-Controller 的實作方式
3. **資料關聯**：熟悉 One2many、Many2one、Many2many 關係設計
4. **樞紐分析**：建立互動式資料分析報表
5. **Qweb 報表**：設計專業的 PDF 報表
6. **Wizard 精靈**：實作複雜的業務流程對話框
7. **權限控制**：建立安全的多使用者存取機制

**後續學習建議**：
- 深入研究 Odoo 核心模組的實作方式
- 學習 API 整合和外部系統對接
- 探索行動應用程式開發
- 研究工作流程和審核機制
- 學習效能優化和大數據處理

希望這份教材能幫助您快速掌握 Odoo 開發技能，並成功應用到實際專案中！

**聯絡資訊**：
- 講師：李奕璋
- 公司：Cympotek
- 版本：v1r2
- 最後更新：2024.12.24

---

*感謝您參與 Odoo 16 ERP 客製開發教育訓練！*