# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkBundleProductLine(models.Model):
    _name = 'cpk.bundle.product.line'
    _description = '搭售商品明細'
    _order = 'rule_id, sequence, id'

    # 基本資訊
    rule_id = fields.Many2one('cpk.bundle.discount.rule', '搭售規則', 
                             required=True, ondelete='cascade')
    sequence = fields.Integer('順序', default=10)
    
    # 商品資訊
    product_id = fields.Many2one('product.product', '搭售商品', required=True)
    product_category_id = fields.Related('product_id.categ_id', 
                                        string='商品分類', readonly=True)
    product_uom_id = fields.Related('product_id.uom_id', 
                                   string='計量單位', readonly=True)
    
    # 搭售條件
    is_required = fields.Boolean('必選商品', 
                                help='勾選表示此商品為搭售必選商品')
    min_qty = fields.Float('最少數量', default=1.0,
                          help='此商品的最少購買數量')
    max_qty = fields.Float('最多數量',
                          help='此商品的最多購買數量，空白表示不限制')
    
    # 商品組別（用於複雜搭售邏輯）
    product_group = fields.Char('商品組別',
                               help='用於設定 A、B、C、D 等商品組合，例如 A 組、B 組')
    group_min_select = fields.Integer('組內最少選擇',
                                     help='同組商品中最少要選擇的品項數')
    
    # 價格資訊
    list_price = fields.Related('product_id.list_price', string='標準價格', 
                               readonly=True)
    
    # 說明資訊
    description = fields.Text('說明')
    
    # 計算欄位
    display_name = fields.Char('顯示名稱', compute='_compute_display_name')

    @api.depends('product_id', 'min_qty', 'is_required')
    def _compute_display_name(self):
        """計算顯示名稱"""
        for record in self:
            name_parts = []
            if record.product_id:
                name_parts.append(record.product_id.name)
            if record.min_qty > 1:
                name_parts.append(f'(最少 {record.min_qty})')
            if record.is_required:
                name_parts.append('[必選]')
            record.display_name = ' '.join(name_parts)

    @api.constrains('min_qty', 'max_qty')
    def _check_quantities(self):
        """檢查數量設定"""
        for record in self:
            if record.min_qty < 0:
                raise ValidationError('最少數量不能小於 0！')
            if record.max_qty and record.max_qty < record.min_qty:
                raise ValidationError('最多數量不能小於最少數量！')

    @api.constrains('product_id', 'rule_id')
    def _check_product_unique(self):
        """檢查同一規則下商品不能重複"""
        for record in self:
            if record.rule_id and record.product_id:
                domain = [
                    ('rule_id', '=', record.rule_id.id),
                    ('product_id', '=', record.product_id.id),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(f'商品 {record.product_id.name} 已存在於此規則中！')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """商品變更時的處理"""
        if self.product_id and self.rule_id.main_product_id:
            if self.product_id == self.rule_id.main_product_id:
                return {
                    'warning': {
                        'title': '警告',
                        'message': '選擇的商品與主商品相同，請重新選擇！'
                    }
                }

    def name_get(self):
        """自訂顯示格式"""
        result = []
        for record in self:
            name = record.display_name or record.product_id.name or '未設定商品'
            result.append((record.id, name))
        return result