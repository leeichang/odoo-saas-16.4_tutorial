# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkReimburse(models.Model):
    _name = 'cpk.reimburse'
    _description = '費用請款單'
    _order = 'name desc'

    name = fields.Char('請款單號', required=True, copy=False, readonly=True, default='新建')
    employee_id = fields.Many2one('hr.employee', '請款人員', required=True, default=lambda self: self.env.user.employee_id)
    reimburse_date = fields.Date('請款日期', required=True, default=fields.Date.context_today)
    is_printed = fields.Boolean('是否列印', default=False)
    partner_id = fields.Many2one('res.partner', '付款對象', required=True)
    alternative_payee = fields.Char('替代受款人')
    bank_id = fields.Many2one('res.bank', '銀行')
    payment_method_id = fields.Many2one('account.payment.method', '付款方式', required=True)
    payment_base_date = fields.Date('付款基準日')
    due_date = fields.Date('帳款到期日', required=True)
    account_holder = fields.Char('戶名')
    bank_account = fields.Char('銀行帳號')
    advance_balance = fields.Monetary('預付款餘額', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', '付款幣別', required=True, default=lambda self: self.env.company.currency_id)
    exchange_rate = fields.Float('匯率', default=1.0, digits=(12, 6))
    notes = fields.Text('備註')
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('submitted', '送簽核'),
        ('approved', '審核'),
        ('paid', '付款'),
        ('closed', '結案')
    ], '狀態', default='draft', tracking=True)
    
    # 關聯欄位
    voucher_ids = fields.One2many('cpk.voucher', 'reimburse_id', '憑證資料')
    expense_line_ids = fields.One2many('cpk.expense.line', 'reimburse_id', '請款明細')
    
    # 計算欄位
    total_amount = fields.Monetary('總金額', compute='_compute_amounts', store=True, currency_field='currency_id')
    total_tax = fields.Monetary('總稅額', compute='_compute_amounts', store=True, currency_field='currency_id')

    @api.model
    def create(self, vals):
        if vals.get('name', '新建') == '新建':
            vals['name'] = self.env['ir.sequence'].next_by_code('cpk.reimburse') or '新建'
        return super(CpkReimburse, self).create(vals)

    @api.depends('expense_line_ids.amount_total', 'expense_line_ids.tax_amount')
    def _compute_amounts(self):
        for record in self:
            record.total_amount = sum(record.expense_line_ids.mapped('amount_total'))
            record.total_tax = sum(record.expense_line_ids.mapped('tax_amount'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # 設定戶名為聯絡人名稱
            self.account_holder = self.partner_id.name
            
            # 如果聯絡人有銀行帳戶資料，自動帶入
            if self.partner_id.bank_ids:
                bank_account = self.partner_id.bank_ids[0]  # 取第一個銀行帳戶
                self.bank_id = bank_account.bank_id.id if bank_account.bank_id else False
                self.bank_account = bank_account.acc_number or ''
            else:
                # 如果沒有銀行資料，清空相關欄位
                self.bank_id = False
                self.bank_account = ''
        else:
            # 如果沒有選擇聯絡人，清空所有相關欄位
            self.account_holder = ''
            self.bank_id = False
            self.bank_account = ''

    def action_create_voucher(self):
        """開啟新增憑證的對話框"""
        return {
            'name': '新增憑證',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.voucher',
            'view_mode': 'form',
            'view_id': self.env.ref('cpk_reimburse.view_cpk_voucher_form').id,
            'target': 'new',
            'context': {
                'default_reimburse_id': self.id,
            }
        }


class CpkVoucher(models.Model):
    _name = 'cpk.voucher'
    _description = '憑證資料'
    _order = 'reimburse_id, id'

    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', required=True, ondelete='cascade')
    voucher_type = fields.Selection([
        ('invoice', '發票'),
        ('receipt', '收據')
    ], '憑證類型', required=True)
    invoice_date = fields.Date('發票日期')
    tax_code_id = fields.Many2one('cpk.tax.code', '稅碼')
    tax_id = fields.Char('統一編號')
    invoice_number = fields.Char('發票號碼')
    attachment_ids = fields.Many2many('ir.attachment', string='上傳憑證')
    currency_id = fields.Many2one('res.currency', '交易幣別', related='reimburse_id.currency_id', store=True, readonly=True)
    amount_total = fields.Monetary('交易金額(含稅)', currency_field='currency_id')
    amount_untaxed = fields.Monetary('交易金額(未稅)', currency_field='currency_id')
    tax_amount = fields.Monetary('稅額', currency_field='currency_id')
    is_consolidated = fields.Boolean('是否彙加註記', default=False)
    
    # 關聯欄位
    expense_line_ids = fields.One2many('cpk.expense.line', 'voucher_id', '請款明細')

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        if self.amount_total:
            # 計算未稅金額 = 含稅金額 / 1.05，四捨五入到整數
            self.amount_untaxed = round(self.amount_total / 1.05)
            # 計算稅額 = 含稅金額 - 未稅金額
            self.tax_amount = self.amount_total - self.amount_untaxed

    @api.onchange('amount_untaxed')
    def _onchange_amount_untaxed(self):
        if self.amount_untaxed and not self.amount_total:
            # 如果只輸入未稅金額，計算含稅金額
            self.amount_total = round(self.amount_untaxed * 1.05)
            self.tax_amount = self.amount_total - self.amount_untaxed

    @api.model
    def create(self, vals):
        voucher = super(CpkVoucher, self).create(vals)
        # 確保所有關聯的請款明細都設定正確的 reimburse_id
        if voucher.reimburse_id and voucher.expense_line_ids:
            voucher.expense_line_ids.write({'reimburse_id': voucher.reimburse_id.id})
        return voucher

    def write(self, vals):
        result = super(CpkVoucher, self).write(vals)
        # 如果更改了 reimburse_id，同步更新所有關聯的請款明細
        if 'reimburse_id' in vals:
            for voucher in self:
                if voucher.expense_line_ids:
                    voucher.expense_line_ids.write({'reimburse_id': voucher.reimburse_id.id})
        return result

    def name_get(self):
        """自訂顯示名稱：顯示憑證類型 + 發票號碼"""
        result = []
        for record in self:
            voucher_type_dict = dict(record._fields['voucher_type'].selection)
            voucher_type_name = voucher_type_dict.get(record.voucher_type, '')
            
            if record.invoice_number:
                name = f"{voucher_type_name} - {record.invoice_number}"
            else:
                name = f"{voucher_type_name} (未設定發票號碼)"
            
            result.append((record.id, name))
        return result


class CpkExpenseLine(models.Model):
    _name = 'cpk.expense.line'
    _description = '請款明細'
    _order = 'reimburse_id, sequence, id'

    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', required=True, ondelete='cascade')
    voucher_id = fields.Many2one('cpk.voucher', '憑證', required=True, ondelete='cascade')
    sequence = fields.Integer('項次', default=10)
    expense_category_id = fields.Many2one('cpk.expense.category', '費用類別', required=True, domain=[('is_leaf', '=', True)])
    cost_center_id = fields.Many2one('hr.department', '成本中心')
    amount_total = fields.Monetary('金額含稅', currency_field='currency_id', required=True)
    amount_untaxed = fields.Monetary('金額未稅', currency_field='currency_id')
    tax_amount = fields.Monetary('稅額', currency_field='currency_id')
    analytic_account_id = fields.Many2one('account.analytic.account', '專案代號')
    description = fields.Text('費用說明')
    currency_id = fields.Many2one('res.currency', '幣別', related='reimburse_id.currency_id', store=True)
    invoice_number = fields.Char('發票號碼', related='voucher_id.invoice_number', store=True, readonly=True)

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        if self.amount_total:
            # 計算未稅金額 = 含稅金額 / 1.05，四捨五入到整數
            self.amount_untaxed = round(self.amount_total / 1.05)
            # 計算稅額 = 含稅金額 - 未稅金額
            self.tax_amount = self.amount_total - self.amount_untaxed

    @api.onchange('amount_untaxed')
    def _onchange_amount_untaxed(self):
        if self.amount_untaxed and not self.amount_total:
            # 如果只輸入未稅金額，計算含稅金額
            self.amount_total = round(self.amount_untaxed * 1.05)
            self.tax_amount = self.amount_total - self.amount_untaxed

    @api.constrains('amount_total', 'amount_untaxed', 'tax_amount')
    def _check_amounts(self):
        for record in self:
            if record.amount_total and record.amount_untaxed and record.tax_amount:
                if abs(record.amount_total - record.amount_untaxed - record.tax_amount) > 0.01:
                    raise ValidationError('金額計算錯誤：含稅金額 = 未稅金額 + 稅額')

