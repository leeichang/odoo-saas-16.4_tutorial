# -*- coding: utf-8 -*-

import uuid
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # 折扣方案相關
    applied_discount_schemes = fields.Text('套用的折扣方案', readonly=True)
    discount_calculation_log = fields.Text('折扣計算記錄', readonly=True)
    
    def action_confirm(self):
        """確認訂單時套用折扣方案"""
        for order in self:
            order._apply_discount_schemes()
        return super().action_confirm()

    def _apply_discount_schemes(self):
        """套用適用的折扣方案"""
        applicable_schemes = self._get_applicable_discount_schemes()
        applied_schemes = []
        calculation_logs = []
        
        for scheme in applicable_schemes:
            if scheme.scheme_type_id.code == 'bundle_discount':
                result = self._apply_bundle_discount(scheme)
                if result['applied']:
                    applied_schemes.append(scheme.display_name)
                    calculation_logs.append(result['log'])
        
        # 記錄套用的方案
        self.applied_discount_schemes = '\n'.join(applied_schemes)
        self.discount_calculation_log = '\n'.join(calculation_logs)

    def _get_applicable_discount_schemes(self):
        """取得適用的折扣方案"""
        domain = [
            ('active', '=', True),
            ('state', '=', 'active'),
        ]
        
        schemes = self.env['cpk.discount.scheme'].search(domain, order='priority desc')
        return schemes.filtered(lambda s: s.is_applicable(self))

    def _apply_bundle_discount(self, scheme):
        """套用搭售折扣"""
        result = {'applied': False, 'log': f'方案 {scheme.display_name}:'}
        
        for rule in scheme.bundle_rule_ids.filtered('active'):
            bundle_result = self._apply_bundle_rule(rule)
            if bundle_result['applied']:
                result['applied'] = True
                result['log'] += f'\n  - {bundle_result["log"]}'
        
        if not result['applied']:
            result['log'] += '\n  - 無符合條件的商品組合'
        
        return result

    def _apply_bundle_rule(self, rule):
        """套用單一搭售規則"""
        result = {'applied': False, 'log': f'規則 {rule.name}'}
        
        # 尋找主商品
        main_lines = self.order_line.filtered(
            lambda l: l.product_id == rule.main_product_id and 
                     not l.applied_discount_scheme_id
        )
        
        if not main_lines:
            result['log'] += ': 未找到主商品'
            return result
        
        # 尋找搭售商品
        bundle_products = rule.bundle_product_ids.mapped('product_id')
        bundle_lines = self.order_line.filtered(
            lambda l: l.product_id in bundle_products and 
                     not l.applied_discount_scheme_id
        )
        
        if not bundle_lines:
            result['log'] += ': 未找到搭售商品'
            return result
        
        # 檢查搭售條件
        if not rule.check_bundle_conditions(main_lines, bundle_lines):
            result['log'] += ': 不滿足搭售條件'
            return result
        
        # 尋找適用級距
        main_qty = sum(main_lines.mapped('product_uom_qty'))
        tier = rule.find_applicable_tier(main_qty)
        
        if not tier:
            result['log'] += ': 未找到適用級距'
            return result
        
        # 套用折扣
        bundle_group_id = str(uuid.uuid4())
        self._apply_tier_discount(main_lines, bundle_lines, tier, bundle_group_id)
        
        result['applied'] = True
        result['log'] += f': 套用級距 {tier.name}'
        
        return result

    def _apply_tier_discount(self, main_lines, bundle_lines, tier, bundle_group_id):
        """套用級距折扣"""
        # 套用主商品折扣
        for line in main_lines:
            discount_rate = tier.calculate_discount_rate(
                line.price_unit, tier.main_discount_type, tier.main_discount_value
            )
            line.write({
                'discount': discount_rate,
                'applied_discount_scheme_id': tier.rule_id.scheme_id.id,
                'applied_discount_rule_id': tier.rule_id.id,
                'applied_discount_tier_id': tier.id,
                'is_bundle_main_product': True,
                'bundle_group_id': bundle_group_id,
            })
        
        # 套用搭售商品折扣
        for line in bundle_lines:
            discount_rate = tier.calculate_discount_rate(
                line.price_unit, tier.bundle_discount_type, tier.bundle_discount_value
            )
            line.write({
                'discount': discount_rate,
                'applied_discount_scheme_id': tier.rule_id.scheme_id.id,
                'applied_discount_rule_id': tier.rule_id.id,
                'applied_discount_tier_id': tier.id,
                'is_bundle_product': True,
                'bundle_group_id': bundle_group_id,
            })

    def action_reset_discounts(self):
        """重置所有折扣"""
        for line in self.order_line:
            line.write({
                'discount': 0,
                'applied_discount_scheme_id': False,
                'applied_discount_rule_id': False,
                'applied_discount_tier_id': False,
                'is_bundle_main_product': False,
                'is_bundle_product': False,
                'bundle_group_id': False,
            })
        
        self.write({
            'applied_discount_schemes': '',
            'discount_calculation_log': '',
        })

    def action_recalculate_discounts(self):
        """重新計算折扣"""
        self.action_reset_discounts()
        self._apply_discount_schemes()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # 折扣方案追蹤
    applied_discount_scheme_id = fields.Many2one('cpk.discount.scheme', 
                                               '套用的折扣方案', readonly=True)
    applied_discount_rule_id = fields.Many2one('cpk.bundle.discount.rule', 
                                             '套用的折扣規則', readonly=True)
    applied_discount_tier_id = fields.Many2one('cpk.bundle.tier', 
                                             '套用的級距', readonly=True)
    
    # 搭售標記
    is_bundle_main_product = fields.Boolean('是否為搭售主商品', readonly=True)
    is_bundle_product = fields.Boolean('是否為搭售商品', readonly=True)
    bundle_group_id = fields.Char('搭售群組ID', readonly=True,
                                 help='用於關聯同一組搭售商品')
    
    # 計算欄位
    discount_scheme_display = fields.Char('折扣方案', 
                                         compute='_compute_discount_scheme_display')
    bundle_type_display = fields.Char('搭售類型', 
                                     compute='_compute_bundle_type_display')

    @api.depends('applied_discount_scheme_id', 'applied_discount_tier_id')
    def _compute_discount_scheme_display(self):
        """計算折扣方案顯示"""
        for line in self:
            if line.applied_discount_scheme_id and line.applied_discount_tier_id:
                line.discount_scheme_display = (
                    f'{line.applied_discount_scheme_id.display_name} - '
                    f'{line.applied_discount_tier_id.name}'
                )
            elif line.applied_discount_scheme_id:
                line.discount_scheme_display = line.applied_discount_scheme_id.display_name
            else:
                line.discount_scheme_display = ''

    @api.depends('is_bundle_main_product', 'is_bundle_product')
    def _compute_bundle_type_display(self):
        """計算搭售類型顯示"""
        for line in self:
            if line.is_bundle_main_product:
                line.bundle_type_display = '主商品'
            elif line.is_bundle_product:
                line.bundle_type_display = '搭售商品'
            else:
                line.bundle_type_display = ''

    def action_view_bundle_group(self):
        """檢視同組搭售商品"""
        if not self.bundle_group_id:
            raise UserError('此商品不屬於任何搭售群組！')
        
        return {
            'name': '搭售群組商品',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'tree',
            'domain': [
                ('order_id', '=', self.order_id.id),
                ('bundle_group_id', '=', self.bundle_group_id)
            ],
        }