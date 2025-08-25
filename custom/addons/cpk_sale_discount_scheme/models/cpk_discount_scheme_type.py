# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CpkDiscountSchemeType(models.Model):
    _name = 'cpk.discount.scheme.type'
    _description = '折扣方案類型'
    _order = 'sequence, name'

    name = fields.Char('類型名稱', required=True, translate=True)
    code = fields.Char('代碼', required=True)
    description = fields.Text('說明', translate=True)
    sequence = fields.Integer('順序', default=10)
    active = fields.Boolean('啟用', default=True)

    # 技術欄位
    engine_class = fields.Char('計算引擎類別', 
                              help='用於擴展不同類型折扣的計算邏輯')

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', '折扣方案類型代碼必須唯一！'),
    ]

    def name_get(self):
        """自訂顯示格式"""
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result