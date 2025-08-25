# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FieldTraining(models.Model):
    _name = 'cpk.field.training'
    _description = 'Odoo 欄位類型教育訓練'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # ===========================================
    # 基本欄位類型 (Basic Field Types)
    # ===========================================
    
    # Char - 短文字字符串
    name = fields.Char(
        string='姓名 (Char)', 
        required=True, 
        help='短文字字符串，如姓名、代碼等'
    )
    
    code = fields.Char(
        string='代碼 (Char)', 
        size=10, 
        help='有長度限制的短文字'
    )
    
    # Text - 長文字內容
    description = fields.Text(
        string='描述 (Text)', 
        help='多行長文字，如描述、備註等'
    )
    
    # Integer - 整數
    quantity = fields.Integer(
        string='數量 (Integer)', 
        default=1, 
        help='整數數值，如數量、年齡等'
    )
    
    age = fields.Integer(
        string='年齡 (Integer)', 
        help='整數範例：年齡'
    )
    
    # Float - 浮點數
    price = fields.Float(
        string='價格 (Float)', 
        digits=(10, 2), 
        help='浮點數，指定小數位數 (10,2)'
    )
    
    weight = fields.Float(
        string='重量 (Float)', 
        help='浮點數範例：重量'
    )
    
    percentage = fields.Float(
        string='百分比 (Float)', 
        help='浮點數範例：百分比'
    )
    
    # Boolean - 布林值
    is_active = fields.Boolean(
        string='啟用 (Boolean)', 
        default=True, 
        help='布林值：True/False'
    )
    
    is_completed = fields.Boolean(
        string='已完成 (Boolean)', 
        help='布林值範例：完成狀態'
    )
    
    # Date - 日期
    birth_date = fields.Date(
        string='生日 (Date)', 
        help='日期欄位，格式：YYYY-MM-DD'
    )
    
    start_date = fields.Date(
        string='開始日期 (Date)', 
        default=fields.Date.today, 
        help='日期範例：開始日期'
    )
    
    # Datetime - 日期時間
    order_datetime = fields.Datetime(
        string='訂單時間 (Datetime)', 
        default=fields.Datetime.now, 
        help='日期時間欄位，包含時分秒'
    )
    
    last_update = fields.Datetime(
        string='最後更新 (Datetime)', 
        help='日期時間範例：最後更新時間'
    )
    
    # Selection - 選項清單
    status = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '確認'),
        ('done', '完成'),
        ('cancelled', '取消')
    ], string='狀態 (Selection)', default='draft', help='從預定義選項中選擇', tracking=True)
    
    priority = fields.Selection([
        ('0', '低'),
        ('1', '中'),
        ('2', '高'),
        ('3', '急')
    ], string='優先度 (Selection)', help='選項清單範例：優先度')
    
    gender = fields.Selection([
        ('male', '男性'),
        ('female', '女性'),
        ('other', '其他')
    ], string='性別 (Selection)', help='選項清單範例：性別')
    
    # Binary - 二進位檔案
    attachment = fields.Binary(
        string='附件 (Binary)', 
        help='二進位檔案上傳'
    )
    
    document = fields.Binary(
        string='文件 (Binary)', 
        help='二進位檔案範例：文件'
    )
    
    # Image - 圖片
    image = fields.Image(
        string='照片 (Image)', 
        help='圖片檔案，基於 Binary 的特殊類型'
    )
    
    avatar = fields.Image(
        string='頭像 (Image)', 
        max_width=128, 
        max_height=128, 
        help='限制尺寸的圖片'
    )

    # ===========================================
    # 關係欄位類型 (Relational Field Types)
    # ===========================================
    
    # Many2one - 多對一關聯
    partner_id = fields.Many2one(
        'res.partner', 
        string='聯絡人 (Many2one)', 
        help='多對一關聯，連結到聯絡人模型'
    )
    
    user_id = fields.Many2one(
        'res.users', 
        string='負責人 (Many2one)', 
        default=lambda self: self.env.user,
        help='多對一關聯範例：負責人'
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='公司 (Many2one)', 
        default=lambda self: self.env.company,
        help='多對一關聯範例：公司'
    )
    
    # One2many - 一對多關聯 (需要對應的明細模型)
    line_ids = fields.One2many(
        'cpk.field.training.line', 
        'training_id', 
        string='明細行 (One2many)', 
        help='一對多關聯，連結到明細模型'
    )
    
    # Many2many - 多對多關聯
    tag_ids = fields.Many2many(
        'res.partner.category', 
        string='標籤 (Many2many)', 
        help='多對多關聯，可選擇多個標籤'
    )
    
    project_ids = fields.Many2many(
        'project.project',
        'training_project_rel',
        'training_id',
        'project_id',
        string='專案 (Many2many)',
        help='多對多關聯範例：專案'
    )

    # ===========================================
    # 進階欄位類型 (Advanced Field Types)
    # ===========================================
    
    # Monetary - 貨幣金額
    amount_total = fields.Monetary(
        string='總金額 (Monetary)', 
        currency_field='currency_id', 
        help='貨幣欄位，支援多幣別'
    )
    
    unit_price = fields.Monetary(
        string='單價 (Monetary)', 
        currency_field='currency_id', 
        help='貨幣範例：單價'
    )
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='幣別', 
        default=lambda self: self.env.company.currency_id,
        help='貨幣欄位必須搭配的幣別欄位'
    )
    
    # Html - HTML 內容
    html_content = fields.Html(
        string='HTML 內容 (Html)', 
        help='支援富文字格式的 HTML 編輯器'
    )
    
    email_template = fields.Html(
        string='郵件範本 (Html)', 
        help='HTML 範例：郵件範本'
    )
    
    # Related - 關聯欄位
    partner_email = fields.Char(
        related='partner_id.email', 
        string='聯絡人信箱 (Related)', 
        readonly=True,
        help='關聯欄位，自動取得聯絡人的信箱'
    )
    
    partner_phone = fields.Char(
        related='partner_id.phone', 
        string='聯絡人電話 (Related)', 
        readonly=True,
        help='關聯欄位範例：聯絡人電話'
    )
    
    # Reference - 動態參考
    reference_field = fields.Reference([
        ('res.partner', '聯絡人'),
        ('res.users', '使用者'),
        ('project.project', '專案')
    ], string='參考 (Reference)', help='可動態參考不同模型的記錄')
    
    # Json - JSON 資料
    json_data = fields.Json(
        string='JSON 資料 (Json)', 
        help='儲存 JSON 結構化資料'
    )
    
    api_config = fields.Json(
        string='API 設定 (Json)', 
        help='JSON 範例：API 設定資料'
    )
    
    # Properties - 屬性欄位 (Odoo 16 新功能) - 暫時移除以避免錯誤
    # properties = fields.Properties(
    #     string='屬性 (Properties)', 
    #     help='動態屬性欄位，可自訂屬性定義'
    # )

    # ===========================================
    # 計算欄位 (Computed Fields)
    # ===========================================
    
    total_lines = fields.Integer(
        string='明細總數', 
        compute='_compute_total_lines', 
        help='計算欄位：明細行總數'
    )
    
    full_name = fields.Char(
        string='全名', 
        compute='_compute_full_name', 
        help='計算欄位：組合全名'
    )
    
    @api.depends('line_ids')
    def _compute_total_lines(self):
        for record in self:
            record.total_lines = len(record.line_ids)
    
    @api.depends('name', 'code')
    def _compute_full_name(self):
        for record in self:
            if record.name and record.code:
                record.full_name = f"[{record.code}] {record.name}"
            else:
                record.full_name = record.name or ''

    # ===========================================
    # 約束和驗證
    # ===========================================
    
    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age and record.age < 0:
                raise ValidationError('年齡不能為負數！')
    
    @api.constrains('percentage')
    def _check_percentage(self):
        for record in self:
            if record.percentage and (record.percentage < 0 or record.percentage > 100):
                raise ValidationError('百分比必須在 0-100 之間！')

    # ===========================================
    # 動作方法 (Action Methods)
    # ===========================================
    
    def action_open_form_dialog(self):
        """開啟表單對話框新增記錄"""
        return {
            'name': '新增欄位類型訓練 - 完整欄位展示',
            'type': 'ir.actions.act_window',
            'res_model': 'cpk.field.training',
            'view_mode': 'form',
            'views': [(self.env.ref('cpk_odoo_field_training.view_field_training_dialog_form').id, 'form')],
            'target': 'new',  # 開啟對話框
            'context': {
                'default_status': 'draft',
                'default_is_active': True,
                'default_start_date': fields.Date.today(),
                'default_order_datetime': fields.Datetime.now(),
                'default_user_id': self.env.user.id,
                'dialog_size': 'large',  # 設定對話框為大尺寸
            }
        }


class FieldTrainingLine(models.Model):
    _name = 'cpk.field.training.line'
    _description = 'Odoo 欄位訓練明細'
    _order = 'sequence, id'

    training_id = fields.Many2one(
        'cpk.field.training', 
        string='訓練主檔', 
        required=True, 
        ondelete='cascade'
    )
    
    sequence = fields.Integer(string='序號', default=10)
    
    name = fields.Char(string='項目名稱', required=True)
    
    description = fields.Text(string='說明')
    
    quantity = fields.Float(string='數量', default=1.0)
    
    price = fields.Float(string='單價', digits=(10, 2))
    
    subtotal = fields.Float(
        string='小計', 
        compute='_compute_subtotal', 
        store=True
    )
    
    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price


class FieldAttributeDemo(models.Model):
    """欄位屬性展示模型 - 演示所有欄位屬性的使用方式"""
    _name = 'cpk.field.attribute.demo'
    _description = 'Odoo 欄位屬性展示'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ===========================================
    # 基本屬性展示欄位 (Basic Attributes)
    # ===========================================
    
    sequence = fields.Integer(
        string='序號', 
        default=10, 
        help='用於排序的序號',
        index=True
    )
    
    # string 屬性展示
    name = fields.Char(
        string='名稱 (string 屬性)', 
        help='string 屬性：欄位的顯示標籤',
        required=True,
        tracking=True
    )
    
    # required 屬性展示
    required_field = fields.Char(
        string='必填欄位 (required=True)', 
        required=True,
        help='required 屬性：設置欄位為必填'
    )
    
    # readonly 屬性展示
    readonly_field = fields.Char(
        string='唯讀欄位 (readonly=True)', 
        readonly=True,
        default='這是唯讀欄位',
        help='readonly 屬性：欄位無法編輯'
    )
    
    # default 屬性展示 - 固定值
    default_fixed = fields.Char(
        string='預設值-固定 (default)', 
        default='預設文字',
        help='default 屬性：固定預設值'
    )
    
    # default 屬性展示 - 函數
    default_function = fields.Datetime(
        string='預設值-函數 (default)', 
        default=fields.Datetime.now,
        help='default 屬性：使用函數設定預設值'
    )
    
    current_user = fields.Many2one(
        'res.users',
        string='當前使用者 (default lambda)', 
        default=lambda self: self.env.user,
        help='default 屬性：使用 lambda 函數設定預設值'
    )
    
    # help 屬性展示
    help_demo = fields.Char(
        string='說明文字展示', 
        help='help 屬性：這裡是工具提示說明文字，在視圖中懸停時顯示'
    )
    
    # index 屬性展示
    indexed_code = fields.Char(
        string='索引代碼 (index=True)', 
        index=True,
        help='index 屬性：在資料庫中建立索引，提升查詢效能'
    )
    
    # copy 屬性展示
    no_copy_field = fields.Text(
        string='不複製欄位 (copy=False)', 
        copy=False,
        help='copy 屬性：記錄複製時不複製此欄位值'
    )
    
    copy_field = fields.Text(
        string='會複製欄位 (copy=True)', 
        copy=True,
        help='copy 屬性：記錄複製時會複製此欄位值（預設行為）'
    )
    
    # groups 屬性展示
    admin_only_field = fields.Char(
        string='僅管理員可見 (groups)', 
        groups='base.group_system',
        help='groups 屬性：僅特定群組使用者可見'
    )
    
    user_field = fields.Char(
        string='一般使用者可見 (groups)', 
        groups='base.group_user',
        help='groups 屬性：一般使用者群組可見'
    )

    # ===========================================
    # 計算欄位屬性展示 (Computed Field Attributes)
    # ===========================================
    
    quantity = fields.Float(
        string='數量', 
        default=1.0,
        help='用於計算的基礎數量'
    )
    
    unit_price = fields.Float(
        string='單價', 
        digits=(10, 2),
        help='用於計算的單價'
    )
    
    # compute 屬性展示
    total_amount = fields.Float(
        string='總金額 (compute)', 
        compute='_compute_total_amount',
        help='compute 屬性：動態計算欄位值'
    )
    
    # compute + store 屬性展示
    stored_total = fields.Float(
        string='儲存的總金額 (compute + store)', 
        compute='_compute_total_amount',
        store=True,
        help='compute + store 屬性：計算並儲存到資料庫'
    )
    
    # compute + inverse 屬性展示
    editable_total = fields.Float(
        string='可編輯總金額 (compute + inverse)', 
        compute='_compute_total_amount',
        inverse='_inverse_editable_total',
        store=True,
        help='compute + inverse 屬性：可編輯的計算欄位'
    )
    
    @api.depends('quantity', 'unit_price')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.quantity * record.unit_price
            record.stored_total = record.quantity * record.unit_price
            record.editable_total = record.quantity * record.unit_price
    
    def _inverse_editable_total(self):
        for record in self:
            if record.quantity and record.editable_total:
                record.unit_price = record.editable_total / record.quantity

    # ===========================================
    # 關係欄位屬性展示 (Relational Field Attributes)  
    # ===========================================
    
    # related 屬性展示
    partner_id = fields.Many2one(
        'res.partner',
        string='客戶',
        help='用於 related 屬性展示的客戶欄位'
    )
    
    partner_email = fields.Char(
        string='客戶信箱 (related)', 
        related='partner_id.email',
        readonly=True,
        help='related 屬性：引用相關模型的欄位值'
    )
    
    partner_phone = fields.Char(
        string='客戶電話 (related + store)', 
        related='partner_id.phone',
        store=True,
        help='related + store 屬性：引用並儲存相關欄位值'
    )
    
    # domain 屬性展示
    company_partner = fields.Many2one(
        'res.partner',
        string='公司客戶 (domain)',
        domain=[('is_company', '=', True)],
        help='domain 屬性：限制選擇範圍為公司'
    )
    
    # context 屬性展示
    new_partner = fields.Many2one(
        'res.partner',
        string='新客戶 (context)',
        context={'default_is_company': True, 'default_customer_rank': 1},
        help='context 屬性：新建時預設為公司和客戶'
    )
    
    # ondelete 屬性展示
    category_id = fields.Many2one(
        'res.partner.category',
        string='分類 (ondelete=set null)',
        ondelete='set null',
        help='ondelete 屬性：關聯記錄刪除時設為空值'
    )

    # ===========================================
    # 特殊屬性展示 (Special Attributes)
    # ===========================================
    
    # digits 屬性展示
    precise_amount = fields.Float(
        string='精確金額 (digits)',
        digits=(16, 4),
        help='digits 屬性：設定浮點數精度 (總位數, 小數位數)'
    )
    
    # selection 屬性展示
    status = fields.Selection([
        ('draft', '草稿'),
        ('progress', '進行中'), 
        ('done', '完成'),
        ('cancelled', '取消')
    ], string='狀態 (selection)', 
       default='draft',
       tracking=True,
       help='selection 屬性：預定義選項清單')
    
    # translate 屬性展示
    translatable_name = fields.Char(
        string='多語言名稱 (translate)',
        translate=True,
        help='translate 屬性：支援多語言翻譯，右側會出現翻譯圖示，可針對不同語言設定不同的值'
    )
    
    # size 屬性展示
    short_code = fields.Char(
        string='短代碼 (size=5)',
        size=5,
        help='size 屬性：限制字符長度最多5個字符'
    )
    
    # tracking 屬性展示
    tracked_field = fields.Char(
        string='追蹤欄位 (tracking=True)',
        tracking=True,
        help='tracking 屬性：變更時記錄到聊天記錄（Chatter），修改此欄位值時會在記錄下方的對話框中顯示變更歷史'
    )

    # ===========================================
    # 動態屬性展示 (Dynamic Attributes via attrs)
    # ===========================================
    
    condition_field = fields.Boolean(
        string='條件控制欄位',
        default=False,
        help='用於控制其他欄位顯示/隱藏的條件欄位'
    )
    
    dynamic_required = fields.Char(
        string='動態必填欄位 (attrs)',
        help='當條件欄位為 True 時變為必填'
    )
    
    dynamic_readonly = fields.Char(
        string='動態唯讀欄位 (attrs)',
        help='當條件欄位為 True 時變為唯讀'
    )
    
    dynamic_invisible = fields.Char(
        string='動態隱藏欄位 (attrs)',
        help='當條件欄位為 True 時隱藏'
    )

    # ===========================================
    # 約束驗證
    # ===========================================
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError('數量不能為負數！')
    
    @api.constrains('short_code')
    def _check_short_code(self):
        for record in self:
            if record.short_code and len(record.short_code) > 5:
                raise ValidationError('短代碼長度不能超過5個字符！')