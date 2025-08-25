# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkDiscountScheme(models.Model):
    _name = 'cpk.discount.scheme'
    _description = '折扣方案主檔'
    _order = 'priority desc, create_date desc'
    _rec_name = 'display_name'

    # 基本資訊
    name = fields.Char('方案名稱', required=True)
    code = fields.Char('方案代碼', copy=False)
    scheme_type_id = fields.Many2one('cpk.discount.scheme.type', '方案類型', 
                                    required=True)
    active = fields.Boolean('啟用', default=True)
    priority = fields.Integer('優先順序', default=10, 
                             help='數字越大優先順序越高，相同條件下優先套用')
    
    # 時間控制
    date_start = fields.Date('開始日期')
    date_end = fields.Date('結束日期')
    
    # 適用範圍
    company_id = fields.Many2one('res.company', '公司', 
                                default=lambda self: self.env.company)
    pricelist_ids = fields.Many2many('product.pricelist', 
                                    'cpk_scheme_pricelist_rel',
                                    'scheme_id', 'pricelist_id',
                                    '適用價格檔')
    partner_ids = fields.Many2many('res.partner', 
                                  'cpk_scheme_partner_rel',
                                  'scheme_id', 'partner_id',
                                  '適用客戶')
    
    # 說明資訊
    description = fields.Text('說明')
    notes = fields.Html('備註')
    
    # 關聯資料
    bundle_rule_ids = fields.One2many('cpk.bundle.discount.rule', 'scheme_id', 
                                     '搭售折扣規則')
    
    # 計算欄位
    display_name = fields.Char('顯示名稱', compute='_compute_display_name')
    rule_count = fields.Integer('規則數量', compute='_compute_rule_count')
    
    # 狀態追蹤
    state = fields.Selection([
        ('draft', '草稿'),
        ('active', '啟用'),
        ('inactive', '停用'),
    ], default='draft', string='狀態', tracking=True)

    @api.model
    def create(self, vals):
        """建立時自動產生代碼"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('cpk.discount.scheme')
        return super().create(vals)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        """計算顯示名稱"""
        for record in self:
            if record.code:
                record.display_name = f'[{record.code}] {record.name}'
            else:
                record.display_name = record.name

    @api.depends('bundle_rule_ids')
    def _compute_rule_count(self):
        """計算規則數量"""
        for record in self:
            record.rule_count = len(record.bundle_rule_ids)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """檢查日期邏輯"""
        for record in self:
            if record.date_start and record.date_end:
                if record.date_start > record.date_end:
                    raise ValidationError('開始日期不能晚於結束日期！')

    def action_activate(self):
        """啟用方案"""
        self.write({'state': 'active', 'active': True})

    def action_deactivate(self):
        """停用方案"""
        self.write({'state': 'inactive', 'active': False})

    def action_view_rules(self):
        """檢視規則"""
        return {
            'name': '搭售折扣規則',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.bundle.discount.rule',
            'view_mode': 'tree,form',
            'domain': [('scheme_id', '=', self.id)],
            'context': {'default_scheme_id': self.id},
        }

    def is_applicable(self, order):
        """檢查方案是否適用於訂單"""
        if not self.active or self.state != 'active':
            return False
        
        # 檢查日期範圍
        order_date = order.date_order.date()
        if self.date_start and order_date < self.date_start:
            return False
        if self.date_end and order_date > self.date_end:
            return False
        
        # 檢查價格檔
        if self.pricelist_ids and order.pricelist_id not in self.pricelist_ids:
            return False
        
        # 檢查客戶
        if self.partner_ids and order.partner_id not in self.partner_ids:
            return False
        
        # 檢查公司
        if self.company_id and order.company_id != self.company_id:
            return False
        
        return True