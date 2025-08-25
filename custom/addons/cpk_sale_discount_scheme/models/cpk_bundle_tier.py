# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkBundleTier(models.Model):
    _name = 'cpk.bundle.tier'
    _description = '搭售數量級距'
    _order = 'rule_id, min_main_qty, sequence'

    # 基本資訊
    rule_id = fields.Many2one('cpk.bundle.discount.rule', '搭售規則', 
                             required=True, ondelete='cascade')
    name = fields.Char('級距名稱', required=True)
    sequence = fields.Integer('順序', default=10)
    
    # 數量範圍
    min_main_qty = fields.Float('主商品最少數量', required=True, default=1.0)
    max_main_qty = fields.Float('主商品最多數量',
                               help='空白表示無上限')
    
    # 主商品折扣設定
    main_discount_type = fields.Selection([
        ('percentage', '百分比折扣'),
        ('fixed_amount', '固定金額折扣'),
        ('fixed_price', '固定價格'),
    ], '主商品折扣類型', default='percentage', required=True)
    main_discount_value = fields.Float('主商品折扣值', required=True)
    
    # 搭售商品折扣設定
    bundle_discount_type = fields.Selection([
        ('percentage', '百分比折扣'),
        ('fixed_amount', '固定金額折扣'),
        ('fixed_price', '固定價格'),
    ], '搭售商品折扣類型', default='percentage', required=True)
    bundle_discount_value = fields.Float('搭售商品折扣值', required=True)
    
    # 幣別
    currency_id = fields.Related('rule_id.currency_id', string='幣別', 
                                readonly=True)
    
    # 說明資訊
    description = fields.Text('說明')
    
    # 計算欄位
    display_name = fields.Char('顯示名稱', compute='_compute_display_name')
    qty_range_display = fields.Char('數量範圍', compute='_compute_qty_range_display')
    main_discount_display = fields.Char('主商品折扣', compute='_compute_discount_display')
    bundle_discount_display = fields.Char('搭售商品折扣', compute='_compute_discount_display')

    @api.depends('name', 'min_main_qty', 'max_main_qty')
    def _compute_display_name(self):
        """計算顯示名稱"""
        for record in self:
            if record.max_main_qty:
                qty_range = f'{record.min_main_qty}-{record.max_main_qty}'
            else:
                qty_range = f'{record.min_main_qty}+'
            record.display_name = f'{record.name} ({qty_range})'

    @api.depends('min_main_qty', 'max_main_qty')
    def _compute_qty_range_display(self):
        """計算數量範圍顯示"""
        for record in self:
            if record.max_main_qty:
                record.qty_range_display = f'{record.min_main_qty} - {record.max_main_qty}'
            else:
                record.qty_range_display = f'{record.min_main_qty} 以上'

    @api.depends('main_discount_type', 'main_discount_value', 
                'bundle_discount_type', 'bundle_discount_value')
    def _compute_discount_display(self):
        """計算折扣顯示"""
        for record in self:
            # 主商品折扣
            if record.main_discount_type == 'percentage':
                record.main_discount_display = f'{record.main_discount_value}% 折扣'
            elif record.main_discount_type == 'fixed_amount':
                record.main_discount_display = f'減 {record.main_discount_value}'
            else:
                record.main_discount_display = f'固定價格 {record.main_discount_value}'
            
            # 搭售商品折扣
            if record.bundle_discount_type == 'percentage':
                record.bundle_discount_display = f'{record.bundle_discount_value}% 折扣'
            elif record.bundle_discount_type == 'fixed_amount':
                record.bundle_discount_display = f'減 {record.bundle_discount_value}'
            else:
                record.bundle_discount_display = f'固定價格 {record.bundle_discount_value}'

    @api.constrains('min_main_qty', 'max_main_qty')
    def _check_quantities(self):
        """檢查數量邏輯"""
        for record in self:
            if record.min_main_qty <= 0:
                raise ValidationError('主商品最少數量必須大於 0！')
            if record.max_main_qty and record.max_main_qty < record.min_main_qty:
                raise ValidationError('主商品最多數量不能小於最少數量！')

    @api.constrains('main_discount_value', 'bundle_discount_value')
    def _check_discount_values(self):
        """檢查折扣值"""
        for record in self:
            if record.main_discount_type == 'percentage':
                if not (0 <= record.main_discount_value <= 100):
                    raise ValidationError('主商品百分比折扣必須在 0-100 之間！')
            elif record.main_discount_type in ('fixed_amount', 'fixed_price'):
                if record.main_discount_value < 0:
                    raise ValidationError('主商品折扣值不能小於 0！')
            
            if record.bundle_discount_type == 'percentage':
                if not (0 <= record.bundle_discount_value <= 100):
                    raise ValidationError('搭售商品百分比折扣必須在 0-100 之間！')
            elif record.bundle_discount_type in ('fixed_amount', 'fixed_price'):
                if record.bundle_discount_value < 0:
                    raise ValidationError('搭售商品折扣值不能小於 0！')

    @api.constrains('rule_id', 'min_main_qty', 'max_main_qty')
    def _check_tier_overlap(self):
        """檢查級距是否重疊"""
        for record in self:
            if not record.rule_id:
                continue
            
            domain = [
                ('rule_id', '=', record.rule_id.id),
                ('id', '!=', record.id)
            ]
            other_tiers = self.search(domain)
            
            for other_tier in other_tiers:
                # 檢查數量範圍是否重疊
                self_min = record.min_main_qty
                self_max = record.max_main_qty or float('inf')
                other_min = other_tier.min_main_qty
                other_max = other_tier.max_main_qty or float('inf')
                
                if not (self_max < other_min or other_max < self_min):
                    raise ValidationError(
                        f'級距 "{record.name}" 與 "{other_tier.name}" 的數量範圍重疊！'
                    )

    def calculate_discount_rate(self, original_price, discount_type, discount_value):
        """計算折扣率"""
        if discount_type == 'percentage':
            return discount_value
        elif discount_type == 'fixed_amount':
            if original_price > 0:
                return min(100, (discount_value / original_price) * 100)
            return 0
        elif discount_type == 'fixed_price':
            if original_price > discount_value:
                return ((original_price - discount_value) / original_price) * 100
            return 0
        return 0

    def calculate_final_price(self, original_price, discount_type, discount_value):
        """計算最終價格"""
        if discount_type == 'percentage':
            return original_price * (1 - discount_value / 100)
        elif discount_type == 'fixed_amount':
            return max(0, original_price - discount_value)
        elif discount_type == 'fixed_price':
            return discount_value
        return original_price

    def name_get(self):
        """自訂顯示格式"""
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result