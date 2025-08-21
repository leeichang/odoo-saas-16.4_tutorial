# -*- coding: utf-8 -*-

from odoo import models, fields, tools


class CpkReimburseReport(models.Model):
    _name = 'cpk.reimburse.report'
    _description = '費用請款單報表'
    _auto = False
    _rec_name = 'reimburse_name'

    # 請款單頭資訊
    reimburse_id = fields.Many2one('cpk.reimburse', '請款單', readonly=True)
    reimburse_name = fields.Char('請款單號', readonly=True)
    reimburse_date = fields.Date('請款日期', readonly=True)
    partner_id = fields.Many2one('res.partner', '付款對象', readonly=True)
    payment_base_date = fields.Date('付款基準日', readonly=True)
    due_date = fields.Date('帳款到期日', readonly=True)
    currency_id = fields.Many2one('res.currency', '付款幣別', readonly=True)
    exchange_rate = fields.Float('匯率', readonly=True)
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('submitted', '送簽核'),
        ('approved', '審核'),
        ('paid', '付款'),
        ('closed', '結案')
    ], '狀態', readonly=True)
    
    # 請款明細資訊
    expense_category_id = fields.Many2one('cpk.expense.category', '費用類別', readonly=True)
    cost_center_id = fields.Many2one('hr.department', '成本中心', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', '專案代號', readonly=True)
    
    # 金額資訊
    amount_total = fields.Monetary('金額含稅', currency_field='currency_id', readonly=True)
    amount_untaxed = fields.Monetary('金額未稅', currency_field='currency_id', readonly=True)
    tax_amount = fields.Monetary('稅額', currency_field='currency_id', readonly=True)
    
    # 額外維度欄位
    employee_id = fields.Many2one('hr.employee', '請款人員', readonly=True)
    year = fields.Char('年度', readonly=True)
    month = fields.Char('月份', readonly=True)
    quarter = fields.Char('季度', readonly=True)
    
    def init(self):
        """初始化報表SQL視圖"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    
                    -- 請款單頭資訊
                    r.id AS reimburse_id,
                    r.name AS reimburse_name,
                    r.reimburse_date,
                    r.partner_id,
                    r.payment_base_date,
                    r.due_date,
                    r.currency_id,
                    r.exchange_rate,
                    r.state,
                    r.employee_id,
                    
                    -- 請款明細資訊
                    el.expense_category_id,
                    el.cost_center_id,
                    el.analytic_account_id,
                    
                    -- 金額資訊
                    el.amount_total,
                    el.amount_untaxed,
                    el.tax_amount,
                    
                    -- 時間維度
                    EXTRACT(year FROM r.reimburse_date) AS year,
                    EXTRACT(month FROM r.reimburse_date) AS month,
                    CASE 
                        WHEN EXTRACT(month FROM r.reimburse_date) <= 3 THEN 'Q1'
                        WHEN EXTRACT(month FROM r.reimburse_date) <= 6 THEN 'Q2'
                        WHEN EXTRACT(month FROM r.reimburse_date) <= 9 THEN 'Q3'
                        ELSE 'Q4'
                    END AS quarter
                    
                FROM cpk_reimburse r
                LEFT JOIN cpk_expense_line el ON r.id = el.reimburse_id
                WHERE el.id IS NOT NULL
            )
        """ % self._table)