# Odoo 報表與分析功能完整指南

## 功能概述

我已經為 `cpk.field.training` 模型創建了完整的報表與分析功能，包括樞紐分析、圖表分析、QWeb 報表等多種展示方式。

## 📊 分析檢視功能

### 1. 樞紐分析 (Pivot View)

#### 🎯 **功能特色：**
- 多維度數據透視分析
- 動態分組和聚合
- 可拖拉重新排列維度
- 支援數據下鑽分析

#### 📋 **預設設定：**
```xml
<pivot string="欄位類型訓練樞紐分析" sample="1">
    <!-- 列維度 -->
    <field name="status" type="row"/>
    <field name="user_id" type="row"/>
    
    <!-- 欄維度 -->
    <field name="start_date" type="col" interval="month"/>
    
    <!-- 測量值 -->
    <field name="quantity" type="measure"/>
    <field name="price" type="measure"/>
    <field name="amount_total" type="measure"/>
    <field name="total_lines" type="measure"/>
    <field name="__count" type="measure"/>
</pivot>
```

#### 💡 **使用方式：**
- 拖拉欄位到「列」、「欄」、「測量值」區域
- 點選數據進行下鑽分析
- 使用篩選器縮小分析範圍
- 匯出數據到 Excel

---

### 2. 圖表分析 (Graph View)

#### 📈 **支援圖表類型：**
- 長條圖 (Bar Chart)
- 折線圖 (Line Chart)  
- 圓餅圖 (Pie Chart)
- 堆疊圖 (Stacked Chart)

#### 🎨 **預設設定：**
```xml
<graph string="欄位類型訓練圖表分析" type="bar">
    <field name="status"/>
    <field name="start_date" interval="month"/>
    <field name="amount_total" type="measure"/>
</graph>
```

#### 💡 **視覺化特色：**
- 按狀態分組的金額分布
- 按月份顯示趨勢變化
- 可切換不同圖表類型
- 支援多測量值比較

---

### 3. 看板檢視 (Kanban View)

#### 🗂️ **卡片式儀表板：**
- 美觀的卡片設計
- 重要資訊一目了然
- 支援下拉選單操作
- 顯示負責人頭像

#### 🎯 **卡片內容：**
- 姓名和聯絡人資訊
- 狀態標籤顯示
- 金額和幣別
- 負責人、日期、明細行數
- 快捷編輯和刪除功能

#### 🎨 **視覺特色：**
```xml
<!-- 卡片標題 -->
<div class="o_primary">
    <strong>姓名</strong>
</div>

<!-- 狀態按鈕 -->
<button type="object" class="btn btn-primary btn-sm">
    狀態: 草稿/進行中/完成
</button>

<!-- 金額顯示 -->
<field name="amount_total" widget="monetary"/>

<!-- 負責人頭像 -->
<img class="o_avatar o_kanban_avatar"/>
```

---

### 4. 行事曆檢視 (Calendar View)

#### 📅 **時間軸資料展示：**
- 以開始日期為基礎的行事曆檢視
- 按負責人顏色區分
- 支援快速檢視和編輯
- 月/週/日多種檢視模式

#### ⚙️ **設定特色：**
```xml
<calendar string="欄位類型訓練行事曆" 
          date_start="start_date" 
          color="user_id" 
          event_open_popup="true">
    <field name="name"/>
    <field name="partner_id"/>
    <field name="status"/>
    <field name="amount_total"/>
</calendar>
```

---

## 📄 QWeb 報表功能

### 1. 標準報表 (PDF/HTML)

#### 📋 **報表內容：**
- **基本資訊區塊**：姓名、代碼、狀態、負責人等
- **數值資訊區塊**：數量、單價、總金額表格
- **明細資訊區塊**：一對多明細行完整展示
- **布林值資訊**：啟用狀態、完成狀態圖示
- **說明內容**：完整的文字描述

#### 🎨 **報表特色：**
- 專業的 A4 格式排版
- 清楚的區塊劃分
- 表格化數據展示
- 頁腳時間戳和說明

#### 💡 **使用方式：**
- 在記錄檢視中點選「列印」→「欄位類型訓練報表」
- 支援 PDF 下載和 HTML 預覽
- 支援批量列印多筆記錄

---

### 2. 詳細報表 (完整欄位展示)

#### 🔍 **完整欄位分類展示：**
- **基本欄位類型**：所有 Char、Integer、Float、Boolean、Date、Datetime、Selection 欄位
- **關係欄位類型**：Many2one、Related、Many2many、Computed 欄位
- **文字內容欄位**：Text 和 HTML 欄位完整展示

#### 📊 **表格化展示：**
```xml
<table class="table table-sm table-bordered">
    <tbody>
        <tr>
            <td><strong>Char 欄位 (姓名)</strong></td>
            <td><span t-field="doc.name"/></td>
            <td><strong>Char 欄位 (代碼)</strong></td>
            <td><span t-field="doc.code"/></td>
        </tr>
        <!-- 更多欄位展示... -->
    </tbody>
</table>
```

#### 🎯 **教學價值：**
- 展示所有欄位類型在報表中的呈現方式
- 示範不同 widget 的報表輸出效果
- 提供完整的 QWeb 模板範例

---

## 📍 選單結構

### 🗂️ **更新後的選單階層：**
```
欄位類型訓練 (主選單)
├── 欄位類型演示 (基本功能)
├── 欄位屬性展示 (屬性學習)
├── 報表與分析 (新功能) ⭐
│   └── 資料分析 (多維度分析檢視)
└── 設定
    └── 欄位類型說明
```

---

## 🚀 實際使用指南

### 📊 **樞紐分析使用步驟：**
1. 進入「報表與分析」→「資料分析」
2. 切換到「樞紐分析」檢視
3. 拖拉欄位到不同區域進行分析
4. 使用篩選器細化分析條件
5. 匯出分析結果

### 📈 **圖表分析使用步驟：**
1. 在分析檢視中切換到「圖表」
2. 選擇合適的圖表類型
3. 調整分組維度和測量值
4. 觀察數據趨勢和分布

### 📄 **報表生成步驟：**
1. 在任何記錄檢視中點選「列印」按鈕
2. 選擇「欄位類型訓練報表」或「詳細報表」
3. 系統自動產生 PDF 檔案
4. 支援直接列印或下載儲存

---

## 🎓 教學應用場景

### 📚 **樞紐分析教學：**
- 示範多維度數據分析概念
- 教導如何使用拖拉介面
- 展示不同聚合函數的效果
- 練習數據下鑽分析技巧

### 📊 **圖表視覺化教學：**
- 了解不同圖表類型的適用場景
- 學習數據視覺化最佳實務
- 練習趨勢分析和比較分析

### 📄 **QWeb 報表開發教學：**
- 學習 QWeb 模板語法
- 理解報表布局設計原則
- 掌握不同欄位類型的報表輸出方式
- 練習客製化報表開發

---

## ⚙️ 技術實作細節

### 🔧 **檔案結構：**
```
cpk_odoo_field_training/
├── views/training_views.xml (新增分析檢視)
├── views/menus.xml (新增報表選單)
├── reports/field_training_reports.xml (QWeb 報表) ⭐
└── __manifest__.py (更新檔案清單)
```

### 📋 **關鍵技術要點：**
- **Pivot View**: `type="row|col|measure"` 設定
- **Graph View**: `type="bar|line|pie"` 圖表類型
- **Kanban View**: 使用 QWeb 模板自訂卡片
- **Calendar View**: `date_start` 和 `color` 屬性設定
- **QWeb Reports**: `t-field`, `t-foreach`, `t-if` 語法使用

---

## 🎯 學習成果

完成這個報表與分析功能後，學員將掌握：

✅ **分析檢視開發**：樞紐、圖表、看板、行事曆  
✅ **QWeb 報表開發**：PDF/HTML 報表製作  
✅ **數據視覺化**：多維度分析和趨勢展示  
✅ **使用者體驗**：直觀的操作介面設計  
✅ **完整工作流程**：從數據輸入到報表輸出  

這些功能讓您的 Odoo 教育訓練模組成為了一個完整的學習平台，涵蓋了從基礎欄位到進階報表的所有核心概念！🚀