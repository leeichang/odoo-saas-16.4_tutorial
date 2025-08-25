# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    # 關聯的折扣方案
    discount_scheme_ids = fields.Many2many('cpk.discount.scheme',
                                          'cpk_scheme_pricelist_rel',
                                          'pricelist_id', 'scheme_id',
                                          '關聯的折扣方案')
    
    # 計算欄位
    scheme_count = fields.Integer('折扣方案數量', compute='_compute_scheme_count')

    @api.depends('discount_scheme_ids')
    def _compute_scheme_count(self):
        """計算關聯的折扣方案數量"""
        for record in self:
            record.scheme_count = len(record.discount_scheme_ids)

    def action_view_discount_schemes(self):
        """檢視關聯的折扣方案"""
        return {
            'name': '關聯的折扣方案',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.discount.scheme',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.discount_scheme_ids.ids)],
        }


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    # 來源折扣方案追蹤
    discount_scheme_id = fields.Many2one('cpk.discount.scheme', '來源折扣方案')
    discount_rule_id = fields.Many2one('cpk.bundle.discount.rule', '來源折扣規則')
    discount_tier_id = fields.Many2one('cpk.bundle.tier', '來源級距')
    
    # 是否由折扣方案自動建立
    is_from_discount_scheme = fields.Boolean('來自折扣方案', default=False)

    def unlink(self):
        """刪除時的檢查"""
        for record in self:
            if record.is_from_discount_scheme and record.discount_scheme_id:
                # 可以加入額外的檢查邏輯
                pass
        return super().unlink()