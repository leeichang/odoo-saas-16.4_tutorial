# 對話框表單新增功能

## 新增功能說明

我已經為 `cpk_odoo_field_training` 模組新增了「表單新增」按鈕功能，讓使用者可以透過對話框表單來新增記錄，而不是使用 inline edit 方式。

## 實作內容

### 1. 移除 Tree View 的 Inline Edit
- 移除了 `<tree editable="top">` 中的 `editable="top"` 屬性
- 取消了在列表中直接編輯的功能

### 2. 新增「表單新增」按鈕
在 Tree View 中新增了表頭按鈕：
```xml
<header>
    <button name="action_open_form_dialog" 
            string="表單新增" 
            type="object" 
            class="btn-primary" 
            icon="fa-plus"/>
</header>
```

### 3. 新增對話框專用表單視圖
建立了專門用於對話框的簡化表單視圖 `view_field_training_dialog_form`：

**包含的欄位：**
- **基本資料組**：姓名、代碼、狀態、是否啟用、優先度
- **數值與日期組**：數量、價格、開始日期、生日
- **關係欄位組**：聯絡人、負責人、公司
- **其他設定組**：年齡、性別、是否完成
- **說明內容**：描述欄位

**特色功能：**
- 標題區域突出顯示姓名欄位
- 使用合適的 widgets（如 boolean_toggle、priority、radio）
- 分組顯示相關欄位
- 包含自訂按鈕列

### 4. 新增模型方法
在 `FieldTraining` 模型中新增了 `action_open_form_dialog` 方法：

```python
def action_open_form_dialog(self):
    """開啟表單對話框新增記錄"""
    return {
        'name': '新增欄位類型訓練',
        'type': 'ir.actions.act_window',
        'res_model': 'cpk.field.training',
        'view_mode': 'form',
        'views': [(self.env.ref('cpk_odoo_field_training.view_field_training_dialog_form').id, 'form')],
        'target': 'new',  # 開啟對話框
        'context': {
            'default_status': 'draft',
            'default_is_active': True,
            'default_start_date': fields.Date.today(),
            'default_user_id': self.env.user.id,
        }
    }
```

### 5. 自訂按鈕列
對話框底部包含三個按鈕：
- **建立**：建立記錄並關閉對話框
- **建立並繼續**：建立記錄但保持對話框開啟以繼續新增
- **取消**：關閉對話框不儲存

## 使用方式

1. 進入「欄位類型訓練」→「欄位類型演示」頁面
2. 在 Tree View 上方會看到藍色的「表單新增」按鈕
3. 點選按鈕會開啟對話框表單
4. 在對話框中填寫必要資料
5. 點選「建立」完成新增並關閉對話框
6. 或點選「建立並繼續」來持續新增多筆記錄

## 優點

### 👍 **使用者體驗改善：**
- 更清楚的新增流程
- 避免誤觸 inline edit
- 集中的欄位配置
- 更好的視覺提示

### 🎯 **功能優勢：**
- 專用的簡化表單
- 預設值自動設定
- 多種新增方式選擇
- 保持主列表的乾淨性

### 📱 **視覺設計：**
- 現代化的對話框界面
- 分組顯示相關欄位
- 適當的 widget 使用
- 清楚的按鈕標示

## 技術細節

- 使用 `target: 'new'` 開啟對話框
- 透過 `views` 參數指定專用表單視圖
- 使用 `context` 設定預設值
- 保持原有的完整表單視圖不變

這個功能讓教育訓練模組更加實用，提供了更好的使用者體驗，同時展示了 Odoo 中對話框表單的實作方式。