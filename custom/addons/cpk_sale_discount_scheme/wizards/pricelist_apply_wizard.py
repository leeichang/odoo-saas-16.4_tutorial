# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class CpkPricelistApplyWizard(models.TransientModel):
    _name = 'cpk.pricelist.apply.wizard'
    _description = '批次套用價格檔精靈'

    # 基本設定
    scheme_id = fields.Many2one('cpk.discount.scheme', '折扣方案', 
                               required=True, 
                               domain=[('state', '=', 'active')])
    
    # 價格檔選擇
    apply_mode = fields.Selection([
        ('selected', '選定價格檔'),
        ('all', '所有價格檔'),
        ('filtered', '篩選條件'),
    ], string='套用模式', default='selected', required=True)
    
    pricelist_ids = fields.Many2many('product.pricelist', string='選擇價格檔')
    
    # 篩選條件
    company_id = fields.Many2one('res.company', '公司篩選')
    currency_id = fields.Many2one('res.currency', '幣別篩選')
    pricelist_name_filter = fields.Char('價格檔名稱篩選')
    
    # 套用選項
    update_existing = fields.Boolean('更新現有項目', default=False,
                                    help='如果價格檔中已有相同商品的項目，是否更新')
    remove_expired = fields.Boolean('移除過期項目', default=False,
                                   help='移除來自已停用或過期折扣方案的價格項目')
    
    # 結果資訊
    result_log = fields.Text('執行結果', readonly=True)
    pricelist_count = fields.Integer('處理的價格檔數量', readonly=True)
    item_count = fields.Integer('建立的價格項目數量', readonly=True)

    @api.onchange('apply_mode')
    def _onchange_apply_mode(self):
        """套用模式變更時清空價格檔選擇"""
        if self.apply_mode != 'selected':
            self.pricelist_ids = [(5, 0, 0)]

    def action_apply_to_pricelists(self):
        """執行批次套用"""
        self.ensure_one()
        
        # 取得目標價格檔
        target_pricelists = self._get_target_pricelists()
        if not target_pricelists:
            raise UserError('沒有找到符合條件的價格檔！')
        
        # 執行套用
        results = self._execute_apply(target_pricelists)
        
        # 更新結果資訊
        self.write({
            'result_log': results['log'],
            'pricelist_count': results['pricelist_count'],
            'item_count': results['item_count'],
        })
        
        # 返回結果視圖
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_target_pricelists(self):
        """取得目標價格檔"""
        if self.apply_mode == 'selected':
            return self.pricelist_ids
        
        elif self.apply_mode == 'all':
            return self.env['product.pricelist'].search([])
        
        elif self.apply_mode == 'filtered':
            domain = []
            if self.company_id:
                domain.append(('company_id', '=', self.company_id.id))
            if self.currency_id:
                domain.append(('currency_id', '=', self.currency_id.id))
            if self.pricelist_name_filter:
                domain.append(('name', 'ilike', self.pricelist_name_filter))
            
            return self.env['product.pricelist'].search(domain)
        
        return self.env['product.pricelist']

    def _execute_apply(self, pricelists):
        """執行套用邏輯"""
        results = {
            'log': [],
            'pricelist_count': 0,
            'item_count': 0,
        }
        
        for pricelist in pricelists:
            pricelist_result = self._apply_to_single_pricelist(pricelist)
            results['log'].append(
                f'價格檔 "{pricelist.name}": {pricelist_result["message"]}'
            )
            results['item_count'] += pricelist_result['item_count']
        
        results['pricelist_count'] = len(pricelists)
        results['log'] = '\n'.join(results['log'])
        
        return results

    def _apply_to_single_pricelist(self, pricelist):
        """套用到單一價格檔"""
        result = {'item_count': 0, 'message': ''}
        
        try:
            # 移除過期項目
            if self.remove_expired:
                removed_count = self._remove_expired_items(pricelist)
                if removed_count > 0:
                    result['message'] += f'移除 {removed_count} 個過期項目, '
            
            # 建立新項目
            created_count = self._create_pricelist_items(pricelist)
            result['item_count'] = created_count
            result['message'] += f'建立 {created_count} 個價格項目'
            
            # 建立關聯
            if self.scheme_id not in pricelist.discount_scheme_ids:
                pricelist.discount_scheme_ids = [(4, self.scheme_id.id)]
            
        except Exception as e:
            result['message'] = f'錯誤: {str(e)}'
        
        return result

    def _remove_expired_items(self, pricelist):
        """移除過期的價格項目"""
        expired_items = pricelist.item_ids.filtered(
            lambda item: item.is_from_discount_scheme and 
                        item.discount_scheme_id and 
                        (not item.discount_scheme_id.active or 
                         item.discount_scheme_id.state != 'active')
        )
        
        count = len(expired_items)
        expired_items.unlink()
        return count

    def _create_pricelist_items(self, pricelist):
        """為價格檔建立價格項目"""
        created_count = 0
        
        for rule in self.scheme_id.bundle_rule_ids.filtered('active'):
            for tier in rule.tier_ids:
                # 為主商品建立項目
                main_item = self._create_main_product_item(pricelist, rule, tier)
                if main_item:
                    created_count += 1
                
                # 為搭售商品建立項目
                bundle_items = self._create_bundle_product_items(pricelist, rule, tier)
                created_count += len(bundle_items)
        
        return created_count

    def _create_main_product_item(self, pricelist, rule, tier):
        """建立主商品價格項目"""
        # 檢查是否已存在
        existing = pricelist.item_ids.filtered(
            lambda item: item.product_id == rule.main_product_id and 
                        item.min_quantity == tier.min_main_qty and
                        item.is_from_discount_scheme
        )
        
        if existing and not self.update_existing:
            return None
        
        if existing and self.update_existing:
            existing.unlink()
        
        # 計算折扣參數
        compute_price, price_discount = self._get_price_params(
            tier.main_discount_type, tier.main_discount_value
        )
        
        return self.env['product.pricelist.item'].create({
            'pricelist_id': pricelist.id,
            'applied_on': '0_product_variant',
            'product_id': rule.main_product_id.id,
            'min_quantity': tier.min_main_qty,
            'compute_price': compute_price,
            'percent_price': price_discount if compute_price == 'percentage' else 0,
            'fixed_price': tier.main_discount_value if compute_price == 'fixed' else 0,
            'discount_scheme_id': self.scheme_id.id,
            'discount_rule_id': rule.id,
            'discount_tier_id': tier.id,
            'is_from_discount_scheme': True,
        })

    def _create_bundle_product_items(self, pricelist, rule, tier):
        """建立搭售商品價格項目"""
        items = []
        
        for bundle_product in rule.bundle_product_ids:
            # 檢查是否已存在
            existing = pricelist.item_ids.filtered(
                lambda item: item.product_id == bundle_product.product_id and 
                            item.is_from_discount_scheme
            )
            
            if existing and not self.update_existing:
                continue
            
            if existing and self.update_existing:
                existing.unlink()
            
            # 計算折扣參數
            compute_price, price_discount = self._get_price_params(
                tier.bundle_discount_type, tier.bundle_discount_value
            )
            
            item = self.env['product.pricelist.item'].create({
                'pricelist_id': pricelist.id,
                'applied_on': '0_product_variant',
                'product_id': bundle_product.product_id.id,
                'min_quantity': bundle_product.min_qty,
                'compute_price': compute_price,
                'percent_price': price_discount if compute_price == 'percentage' else 0,
                'fixed_price': tier.bundle_discount_value if compute_price == 'fixed' else 0,
                'discount_scheme_id': self.scheme_id.id,
                'discount_rule_id': rule.id,
                'discount_tier_id': tier.id,
                'is_from_discount_scheme': True,
            })
            items.append(item)
        
        return items

    def _get_price_params(self, discount_type, discount_value):
        """取得價格計算參數"""
        if discount_type == 'percentage':
            return 'percentage', discount_value
        elif discount_type == 'fixed_price':
            return 'fixed', discount_value
        else:  # fixed_amount
            # Odoo 價格檔不直接支援固定金額折扣，轉換為百分比
            # 這裡需要根據商品原價計算，暫時使用百分比
            return 'percentage', 10  # 預設 10% 折扣
        
    def action_preview_changes(self):
        """預覽變更"""
        target_pricelists = self._get_target_pricelists()
        
        preview_info = []
        for pricelist in target_pricelists[:5]:  # 限制預覽數量
            info = f'價格檔: {pricelist.name}'
            for rule in self.scheme_id.bundle_rule_ids[:2]:  # 限制規則數量
                info += f'\n  - 主商品: {rule.main_product_id.name}'
                info += f'\n  - 搭售商品: {len(rule.bundle_product_ids)} 個'
                info += f'\n  - 級距: {len(rule.tier_ids)} 個'
            preview_info.append(info)
        
        if len(target_pricelists) > 5:
            preview_info.append(f'... 還有 {len(target_pricelists) - 5} 個價格檔')
        
        self.result_log = '\n\n'.join(preview_info)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }