# QWeb 報表疑難排解指南

## 問題分析：QWeb 報表不出現在選單中

### 可能原因

1. **模組未完全重新載入**
   - QWeb 報表定義需要模組升級才會生效
   - 瀏覽器快取可能影響選單顯示

2. **報表綁定配置**
   - `binding_model_id` 和 `binding_type` 配置正確
   - 報表應該出現在記錄的「列印」選單中，而非主選單

3. **權限問題**
   - 使用者可能沒有報表存取權限
   - 需要檢查 `ir.model.access.csv` 設定

## ✅ 當前配置檢查

### 報表動作設定 (正確)
```xml
<!-- 標準 PDF 報表 -->
<record id="action_report_field_training" model="ir.actions.report">
    <field name="name">欄位類型訓練報表</field>
    <field name="model">cpk.field.training</field>
    <field name="report_type">qweb-pdf</field>
    <field name="binding_model_id" ref="model_cpk_field_training"/>
    <field name="binding_type">report</field>
</record>

<!-- HTML 版本報表 -->
<record id="action_report_field_training_html" model="ir.actions.report">
    <field name="name">欄位類型訓練報表 (HTML)</field>
    <field name="model">cpk.field.training</field>
    <field name="report_type">qweb-html</field>
    <field name="binding_model_id" ref="model_cpk_field_training"/>
    <field name="binding_type">report</field>
</record>

<!-- 詳細報表 -->
<record id="action_report_field_training_detailed" model="ir.actions.report">
    <field name="name">欄位類型訓練詳細報表</field>
    <field name="model">cpk.field.training</field>
    <field name="report_type">qweb-pdf</field>
    <field name="binding_model_id" ref="model_cpk_field_training"/>
    <field name="binding_type">report</field>
</record>
```

## 🔍 正確的報表位置

QWeb 報表 **不會出現在左側選單中**，它們會出現在：

### 1. 記錄檢視的列印選單
```
欄位類型訓練 記錄檢視 → 列印按鈕 (⚙️) → 報表選項
├── 欄位類型訓練報表 (PDF)
├── 欄位類型訓練報表 (HTML)
└── 欄位類型訓練詳細報表 (PDF)
```

### 2. 清單檢視的批量操作
```
欄位類型訓練 列表檢視 → 選取多筆記錄 → 動作選單 → 列印
```

## 🚀 測試報表功能步驟

### 步驟 1：進入記錄檢視
1. 進入「欄位類型訓練」→「欄位類型演示」
2. 點選任一筆記錄進入詳細檢視
3. 或建立一筆新記錄

### 步驟 2：尋找列印按鈕
- 在記錄檢視頂部工具列尋找「列印」按鈕 (通常是齒輪圖示 ⚙️)
- 或「動作」選單中的「列印」選項

### 步驟 3：選擇報表
應該會看到以下報表選項：
- **欄位類型訓練報表**：標準 PDF 格式
- **欄位類型訓練報表 (HTML)**：網頁預覽格式
- **欄位類型訓練詳細報表**：完整欄位展示

## 🔧 模組升級方法

### 方法 1：透過 Odoo 介面
1. 進入「應用程式」選單
2. 移除「應用程式」篩選器
3. 搜尋「cpk_odoo_field_training」
4. 點選「升級」按鈕

### 方法 2：重新啟動 Odoo 服務
```bash
# 停止 Odoo 服務
sudo service odoo stop

# 清除快取並重新啟動
sudo service odoo start
```

### 方法 3：指令升級（需要正確的資料庫連線）
```bash
python3 odoo-bin -d [database_name] -u cpk_odoo_field_training --stop-after-init
```

## 🎯 預期行為

### 成功的報表功能應該：
1. **在記錄檢視顯示列印選項**
2. **支援 PDF 下載**：點選後自動下載 PDF 檔案
3. **支援 HTML 預覽**：在新視窗開啟網頁版報表
4. **批量列印**：選取多筆記錄可一次列印

### 報表內容包含：
- **基本資訊**：姓名、代碼、狀態、負責人等
- **數值資訊**：數量、價格、總金額等
- **明細資訊**：一對多關聯明細列表
- **布林值資訊**：圖示化的是/否顯示
- **文字內容**：完整的描述欄位

## 🛠️ 疑難排解

### 如果報表仍未出現：

1. **檢查瀏覽器**
   - 清除瀏覽器快取
   - 重新整理頁面
   - 嘗試無痕瀏覽模式

2. **檢查使用者權限**
   - 確認使用者具有模型存取權限
   - 檢查是否為管理員帳號

3. **檢查模組狀態**
   - 確認模組為「已安裝」狀態
   - 嘗試解除安裝後重新安裝

4. **檢查資料**
   - 確保有建立測試資料
   - 某些報表可能需要特定欄位有值

## 📋 報表功能驗證清單

- [ ] 能在記錄檢視找到「列印」按鈕
- [ ] 點選「列印」顯示報表選單
- [ ] 「欄位類型訓練報表」可產生 PDF
- [ ] 「欄位類型訓練報表 (HTML)」可預覽
- [ ] 「詳細報表」顯示完整欄位資訊
- [ ] 報表內容正確顯示資料
- [ ] 批量列印功能正常

## 💡 教學重點

這個 QWeb 報表功能示範了：
- **report binding**：如何將報表綁定到模型
- **QWeb 模板語法**：`t-field`、`t-foreach`、`t-if` 使用
- **多種報表格式**：PDF 和 HTML 輸出
- **完整欄位展示**：所有 Odoo 欄位類型的報表呈現
- **專業排版**：表格化資料展示和版面設計

當報表功能正常運作時，學員就能完整體驗從資料建立、檢視分析到報表輸出的完整 Odoo 工作流程！ 🎓