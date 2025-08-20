# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CpkTaxCode(models.Model):
    _name = 'cpk.tax.code'
    _description = '稅別'
    _order = 'code'

    name = fields.Char('說明', required=True)
    code = fields.Char('代碼', required=True)
    active = fields.Boolean('有效', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', '稅別代碼必須唯一！'),
    ]

    def name_get(self):
        result = []
        for tax_code in self:
            name = '[%s] %s' % (tax_code.code, tax_code.name)
            result.append((tax_code.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        tax_codes = self.search(domain + args, limit=limit)
        return tax_codes.name_get()