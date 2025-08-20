# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CpkExpenseCategory(models.Model):
    _name = 'cpk.expense.category'
    _description = '費用類別'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'parent_left'

    name = fields.Char('名稱', required=True)
    code = fields.Char('代碼', required=True)
    complete_name = fields.Char('完整名稱', compute='_compute_complete_name', recursive=True, store=True)
    parent_id = fields.Many2one('cpk.expense.category', '父類別', index=True, ondelete='cascade')
    child_ids = fields.One2many('cpk.expense.category', 'parent_id', '子類別')
    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)
    parent_path = fields.Char(index=True)
    account_id = fields.Many2one('account.account', '會計科目')
    is_leaf = fields.Boolean('是否為明細', compute='_compute_is_leaf', store=True)
    active = fields.Boolean('有效', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', '費用類別代碼必須唯一！'),
    ]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.depends('child_ids')
    def _compute_is_leaf(self):
        for category in self:
            category.is_leaf = not bool(category.child_ids)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('不能創建遞迴的費用類別結構！')

    def name_get(self):
        result = []
        for category in self:
            name = '[%s] %s' % (category.code, category.complete_name)
            result.append((category.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
            if operator in ('=', '!='):
                domain = ['|', ('code', operator, name), ('complete_name', operator, name)]
        categories = self.search(domain + args, limit=limit)
        return categories.name_get()