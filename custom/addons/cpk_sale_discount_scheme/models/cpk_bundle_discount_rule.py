# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkBundleDiscountRule(models.Model):
    _name = 'cpk.bundle.discount.rule'
    _description = '搭售折扣規則'
    _order = 'scheme_id, sequence, id'

    # 基本資訊
    scheme_id = fields.Many2one('cpk.discount.scheme', '折扣方案', 
                               required=True, ondelete='cascade')
    name = fields.Char('規則名稱', required=True)
    sequence = fields.Integer('順序', default=10)
    active = fields.Boolean('啟用', default=True)
    
    # 主商品設定
    main_product_id = fields.Many2one('product.product', '主商品', required=True,
                                     help='例如：牡蠣肉')
    main_product_required = fields.Boolean('主商品必選', default=True)
    main_product_category_id = fields.Related('main_product_id.categ_id', 
                                             string='主商品分類', readonly=True)
    
    # 搭售條件設定
    bundle_selection_type = fields.Selection([
        ('all_required', '全部必選'),
        ('min_quantity', '最少選購數量'),
        ('min_amount', '最少選購金額'),
        ('min_products', '最少選購品項數'),
    ], '搭售條件', default='min_quantity', required=True)
    
    min_bundle_qty = fields.Float('最少搭售數量', default=1.0)
    min_bundle_amount = fields.Monetary('最少搭售金額', 
                                       currency_field='currency_id')
    min_bundle_products = fields.Integer('最少搭售品項數', default=1)
    
    # 搭售商品設定
    bundle_product_ids = fields.One2many('cpk.bundle.product.line', 'rule_id', 
                                        '搭售商品清單')
    
    # 數量級距設定
    tier_ids = fields.One2many('cpk.bundle.tier', 'rule_id', '數量級距')
    
    # 其他設定
    currency_id = fields.Many2one('res.currency', '幣別',
                                 default=lambda self: self.env.company.currency_id)
    description = fields.Text('說明')
    
    # 計算欄位
    bundle_product_count = fields.Integer('搭售商品數量', 
                                         compute='_compute_bundle_product_count')
    tier_count = fields.Integer('級距數量', compute='_compute_tier_count')

    @api.depends('bundle_product_ids')
    def _compute_bundle_product_count(self):
        """計算搭售商品數量"""
        for record in self:
            record.bundle_product_count = len(record.bundle_product_ids)

    @api.depends('tier_ids')
    def _compute_tier_count(self):
        """計算級距數量"""
        for record in self:
            record.tier_count = len(record.tier_ids)

    @api.constrains('main_product_id', 'bundle_product_ids')
    def _check_products(self):
        """檢查商品設定"""
        for record in self:
            if not record.bundle_product_ids:
                raise ValidationError('至少需要設定一個搭售商品！')
            
            # 檢查主商品不能出現在搭售商品中
            bundle_products = record.bundle_product_ids.mapped('product_id')
            if record.main_product_id in bundle_products:
                raise ValidationError('主商品不能同時是搭售商品！')

    @api.constrains('min_bundle_qty', 'min_bundle_amount', 'min_bundle_products')
    def _check_minimums(self):
        """檢查最小值設定"""
        for record in self:
            if record.bundle_selection_type == 'min_quantity' and record.min_bundle_qty <= 0:
                raise ValidationError('最少搭售數量必須大於 0！')
            elif record.bundle_selection_type == 'min_amount' and record.min_bundle_amount <= 0:
                raise ValidationError('最少搭售金額必須大於 0！')
            elif record.bundle_selection_type == 'min_products' and record.min_bundle_products <= 0:
                raise ValidationError('最少搭售品項數必須大於 0！')

    def check_bundle_conditions(self, main_lines, bundle_lines):
        """檢查是否滿足搭售條件"""
        if not main_lines:
            return False
        
        if self.bundle_selection_type == 'all_required':
            # 檢查是否所有必選商品都有
            required_products = self.bundle_product_ids.filtered('is_required').mapped('product_id')
            selected_products = bundle_lines.mapped('product_id')
            return all(product in selected_products for product in required_products)
        
        elif self.bundle_selection_type == 'min_quantity':
            total_qty = sum(bundle_lines.mapped('product_uom_qty'))
            return total_qty >= self.min_bundle_qty
        
        elif self.bundle_selection_type == 'min_amount':
            total_amount = sum(bundle_lines.mapped('price_subtotal'))
            return total_amount >= self.min_bundle_amount
        
        elif self.bundle_selection_type == 'min_products':
            unique_products = len(set(bundle_lines.mapped('product_id.id')))
            return unique_products >= self.min_bundle_products
        
        return False

    def find_applicable_tier(self, main_qty):
        """尋找適用的級距"""
        applicable_tiers = self.tier_ids.filtered(
            lambda t: t.min_main_qty <= main_qty and 
                     (not t.max_main_qty or main_qty <= t.max_main_qty)
        )
        
        # 返回折扣最大的級距
        if applicable_tiers:
            return applicable_tiers.sorted('main_discount_value', reverse=True)[0]
        
        return False

    def action_view_bundle_products(self):
        """檢視搭售商品"""
        return {
            'name': '搭售商品清單',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.bundle.product.line',
            'view_mode': 'tree,form',
            'domain': [('rule_id', '=', self.id)],
            'context': {'default_rule_id': self.id},
        }

    def action_view_tiers(self):
        """檢視級距設定"""
        return {
            'name': '數量級距設定',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.bundle.tier',
            'view_mode': 'tree,form',
            'domain': [('rule_id', '=', self.id)],
            'context': {'default_rule_id': self.id},
        }