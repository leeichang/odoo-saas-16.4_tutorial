# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class CpkReimbursePrintWizard(models.TransientModel):
    _name = 'cpk.reimburse.print.wizard'
    _description = '請款單列印設定'

    print_type = fields.Selection([
        ('single', '單一單號'),
        ('range', '起訖日期')
    ], '列印類型', required=True, default='single')
    
    # 單一單號相關欄位
    reimburse_id = fields.Many2one('cpk.reimburse', '請款單號')
    
    # 起訖日期相關欄位
    date_from = fields.Date('起始日期')
    date_to = fields.Date('結束日期')
    
    # 過濾條件
    state_filter = fields.Selection([
        ('all', '全部狀態'),
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('submitted', '送簽核'),
        ('approved', '審核'),
        ('paid', '付款'),
        ('closed', '結案')
    ], '狀態過濾', default='all')
    
    employee_ids = fields.Many2many('hr.employee', string='請款人員')
    
    @api.model
    def default_get(self, fields_list):
        """設定預設值"""
        res = super().default_get(fields_list)
        
        # 如果從請款單表單進入，預設帶入當前單號
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        if active_model == 'cpk.reimburse' and active_id:
            res['print_type'] = 'single'
            res['reimburse_id'] = active_id
        else:
            res['print_type'] = 'range'
            # 預設今天
            today = fields.Date.context_today(self)
            res['date_from'] = today.replace(day=1)  # 月初
            res['date_to'] = today  # 今天
            
        return res
    
    def action_print_report(self):
        """執行列印"""
        if self.print_type == 'single':
            # 單一單號列印
            if not self.reimburse_id:
                raise UserError('請選擇要列印的請款單')
            
            reimburse_records = self.reimburse_id
        else:
            # 起訖日期列印
            if not self.date_from or not self.date_to:
                raise UserError('請選擇日期區間')
                
            domain = [('reimburse_date', '>=', self.date_from),
                     ('reimburse_date', '<=', self.date_to)]
            
            # 狀態過濾
            if self.state_filter != 'all':
                domain.append(('state', '=', self.state_filter))
            
            # 人員過濾
            if self.employee_ids:
                domain.append(('employee_id', 'in', self.employee_ids.ids))
            
            reimburse_records = self.env['cpk.reimburse'].search(domain)
            
            if not reimburse_records:
                raise UserError('查無符合條件的請款單資料')
        
        # 取得報表記錄
        report = self.env.ref('cpk_reimburse.report_cpk_reimburse')
        
        # 更新請款單的列印狀態
        reimburse_records.write({'is_printed': True})
        
        # 返回列印報表action
        return report.report_action(reimburse_records)