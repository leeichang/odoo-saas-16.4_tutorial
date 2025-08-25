# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FieldTrainingReportWizard(models.TransientModel):
    _name = 'cpk.field.training.report.wizard'
    _description = '欄位類型訓練報表產生器'

    # 篩選模式選項
    filter_mode = fields.Selection([
        ('all', '顯示全部資料'),
        ('name', '依姓名篩選'),
        ('date', '依日期範圍篩選'),
        ('both', '依姓名和日期篩選')
    ], string='篩選模式', default='all', required=True)

    # 過濾條件欄位
    name_filter = fields.Char(
        string='姓名過濾',
        help='輸入姓名關鍵字進行篩選（支援部分符合）'
    )
    
    date_from = fields.Date(
        string='開始日期',
        help='選擇報表資料的起始日期'
    )
    
    date_to = fields.Date(
        string='結束日期', 
        help='選擇報表資料的結束日期'
    )
    
    # 報表格式選項
    report_format = fields.Selection([
        ('pdf', 'PDF 標準報表'),
        ('html', 'HTML 網頁預覽'),
        ('detailed_pdf', 'PDF 詳細報表')
    ], string='報表格式', default='pdf', required=True)
    
    # 統計資訊
    record_count = fields.Integer(
        string='符合條件記錄數',
        compute='_compute_record_count',
        help='根據當前篩選條件計算的記錄數量'
    )

    @api.depends('filter_mode', 'name_filter', 'date_from', 'date_to')
    def _compute_record_count(self):
        """計算符合條件的記錄數量"""
        for wizard in self:
            domain = wizard._build_domain()
            wizard.record_count = self.env['cpk.field.training'].search_count(domain)

    def _build_domain(self):
        """建立篩選條件 domain"""
        domain = []
        
        # 根據篩選模式決定要套用哪些條件
        if self.filter_mode in ['name', 'both']:
            # 姓名過濾
            if self.name_filter:
                domain.append(('name', 'ilike', self.name_filter))
        
        if self.filter_mode in ['date', 'both']:
            # 日期範圍過濾（使用 start_date 欄位）
            if self.date_from:
                domain.append(('start_date', '>=', self.date_from))
            
            if self.date_to:
                domain.append(('start_date', '<=', self.date_to))
        
        return domain

    def _validate_filter_conditions(self):
        """驗證篩選條件的有效性"""
        if self.filter_mode == 'name' and not self.name_filter:
            raise UserError(_('請輸入姓名關鍵字進行篩選。'))
        
        if self.filter_mode == 'both' and not self.name_filter:
            raise UserError(_('請輸入姓名關鍵字進行篩選。'))
        
        if self.filter_mode == 'date' and not (self.date_from or self.date_to):
            raise UserError(_('請至少設定開始日期或結束日期。'))
        
        if self.filter_mode == 'both' and not (self.date_from or self.date_to):
            raise UserError(_('請至少設定開始日期或結束日期。'))

    def _debug_filter_conditions(self):
        """除錯用：顯示當前篩選條件和資料庫內容"""
        # 顯示所有記錄的姓名
        all_records = self.env['cpk.field.training'].search([])
        record_names = [r.name for r in all_records if r.name]
        
        # 顯示篩選條件
        filter_description = self._get_filter_description()
        domain = self._build_domain()
        
        # 記錄除錯資訊到日誌
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f"=== 報表篩選除錯資訊 ===")
        _logger.info(f"資料庫中的所有姓名: {record_names}")
        _logger.info(f"篩選條件: {filter_description}")
        _logger.info(f"Domain: {domain}")
        _logger.info(f"篩選模式: {self.filter_mode}")
        _logger.info(f"姓名關鍵字: '{self.name_filter}'")
        
        return {
            'all_names': record_names,
            'filter_description': filter_description,
            'domain': domain
        }

    def _get_filter_description(self):
        """取得篩選條件描述"""
        descriptions = []
        
        if self.filter_mode == 'all':
            return '顯示全部資料'
        
        if self.filter_mode in ['name', 'both'] and self.name_filter:
            descriptions.append(f'姓名包含「{self.name_filter}」')
        
        if self.filter_mode in ['date', 'both']:
            if self.date_from and self.date_to:
                descriptions.append(f'日期範圍：{self.date_from} 至 {self.date_to}')
            elif self.date_from:
                descriptions.append(f'開始日期：{self.date_from} 之後')
            elif self.date_to:
                descriptions.append(f'結束日期：{self.date_to} 之前')
        
        return '、'.join(descriptions) if descriptions else '無特定條件'

    def action_generate_report(self):
        """產生報表動作"""
        # 驗證篩選條件
        self._validate_filter_conditions()
        
        # 除錯資訊
        debug_info = self._debug_filter_conditions()
        
        # 取得符合條件的記錄
        domain = self._build_domain()
        records = self.env['cpk.field.training'].search(domain)
        
        if not records:
            filter_msg = self._get_filter_description()
            all_names_msg = '、'.join(debug_info['all_names'][:10])  # 只顯示前10個
            if len(debug_info['all_names']) > 10:
                all_names_msg += f'... (共{len(debug_info["all_names"])}筆)'
            
            error_msg = _('沒有找到符合條件的記錄，請調整篩選條件。\n\n'
                         '當前篩選條件：%s\n\n'
                         '資料庫現有的姓名：%s\n\n'
                         '提示：姓名過濾支援部分符合，例如輸入「張」可以找到「張三」') % (
                filter_msg, all_names_msg or '(目前資料庫中沒有任何記錄)')
            
            raise UserError(error_msg)
        
        # 根據選擇的格式決定報表名稱
        report_mapping = {
            'pdf': 'cpk_odoo_field_training.report_field_training_document',
            'html': 'cpk_odoo_field_training.report_field_training_document', 
            'detailed_pdf': 'cpk_odoo_field_training.report_field_training_detailed'
        }
        
        report_name = report_mapping.get(self.report_format)
        if not report_name:
            raise UserError(_('無效的報表格式選擇。'))
        
        # 決定報表類型
        report_type = 'qweb-html' if self.report_format == 'html' else 'qweb-pdf'
        
        # 使用正常報表動作
        action_external_ids = {
            'pdf': 'cpk_odoo_field_training.action_report_field_training',
            'html': 'cpk_odoo_field_training.action_report_field_training_html',
            'detailed_pdf': 'cpk_odoo_field_training.action_report_field_training_detailed'
        }
        
        action_external_id = action_external_ids.get(self.report_format)
        if not action_external_id:
            raise UserError(_('無效的報表格式：%s') % self.report_format)
        
        try:
            # 透過external ID取得報表動作
            report_action = self.env.ref(action_external_id)
        except ValueError:
            raise UserError(_('找不到報表動作：%s') % action_external_id)
        
        # 設定context來傳遞篩選的記錄IDs
        context = dict(self.env.context)
        context.update({
            'active_ids': records.ids,
            'active_model': 'cpk.field.training',
        })
        
        # 使用report物件的report_action方法
        return report_action.with_context(context).report_action(records)

    def action_preview_data(self):
        """預覽資料動作 - 開啟符合條件的記錄列表"""
        # 驗證篩選條件
        self._validate_filter_conditions()
        
        # 除錯資訊
        debug_info = self._debug_filter_conditions()
        
        domain = self._build_domain()
        filter_description = self._get_filter_description()
        
        # 檢查是否有符合條件的記錄
        records = self.env['cpk.field.training'].search(domain)
        if not records:
            all_names_msg = '、'.join(debug_info['all_names'][:10])  # 只顯示前10個
            if len(debug_info['all_names']) > 10:
                all_names_msg += f'... (共{len(debug_info["all_names"])}筆)'
            
            error_msg = _('沒有找到符合條件的記錄。\n\n'
                         '當前篩選條件：%s\n\n'
                         '資料庫現有的姓名：%s\n\n'
                         '提示：姓名過濾支援部分符合，請嘗試輸入部分姓名關鍵字') % (
                filter_description, all_names_msg or '(目前資料庫中沒有任何記錄)')
            
            raise UserError(error_msg)
        
        return {
            'name': _('報表預覽資料 - %s (共%d筆)') % (filter_description, len(records)),
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.field.training',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'search_default_group_status': 1,
            },
            'target': 'current'
        }

    def action_create_test_data(self):
        """建立測試資料"""
        test_data = [
            {'name': '張三', 'code': 'TEST001', 'start_date': '2024-01-15'},
            {'name': '李四', 'code': 'TEST002', 'start_date': '2024-02-10'},
            {'name': '王五', 'code': 'TEST003', 'start_date': '2024-03-05'},
            {'name': '趙六', 'code': 'TEST004', 'start_date': '2024-04-20'},
            {'name': '陳七', 'code': 'TEST005', 'start_date': '2024-05-12'},
        ]
        
        created_records = []
        for data in test_data:
            # 檢查是否已存在相同代碼的記錄
            existing = self.env['cpk.field.training'].search([('code', '=', data['code'])])
            if not existing:
                record = self.env['cpk.field.training'].create(data)
                created_records.append(record.name)
        
        if created_records:
            message = _('成功建立測試資料：\n%s\n\n現在您可以使用姓名篩選功能了！') % '\n'.join(created_records)
        else:
            message = _('測試資料已存在，無需重複建立。')
        
        # 重新計算記錄數量
        self._compute_record_count()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('測試資料建立'),
                'message': message,
                'sticky': False,
                'type': 'success'
            }
        }