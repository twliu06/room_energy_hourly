# 📘 教室用電資料 ETL 系統（RAW / STG）

## 🧱 系統架構

```
MSSQL（來源視圖）
↓
RAW 層（原始落地）
↓
STG 層（統一指標模型）
```

---

# 📊 資料層設計

## ① RAW 層（原始資料層）

📌 表名：`sensor.room_xxx_energy_hourly`

### 特性：

* 直接從 MSSQL 匯入
* 保留原始欄位格式（多為 TEXT）
* 不做語意轉換
* 不做 metric 正規化
* 僅負責「資料落地」

### 唯一鍵（建議）：

```
(date, hour)
```

---

## ② STG 層（統一指標層）

📌 表名：`public.sensor_room_energy_hourly`

### 特性：

* 一列 = 一個用電指標
* 統一 room_id + metric schema
* 用於分析 / BI / 下游模型

### 結構：

```
room_id
energy_date
energy_hour
metric_type
metric_name
metric_value
```

---

# 🔄 ETL 流程設計

---

## 🟦 RAW ETL（MSSQL → RAW）

### 核心策略：水位線增量

RAW 使用「最後成功時間（watermark）」：

```
(last_date, last_hour)
```

---

### 查詢邏輯：

```sql
WHERE
(
    日期 = last_date
    AND 小時 > last_hour
)
OR
(
    日期 > last_date
)
```

---

### 特點：

* ✔ 只抓新增資料
* ✔ 支援跨日
* ✔ 支援中斷續跑
* ✔ 不做回補掃描

---

## 🟩 STG ETL（RAW → STG）

### 核心策略：水位線 + 尾巴補齊

STG 使用 RAW 的水位線，但多一個特性：

> 🔥 補齊「未完成的當日資料」

---

### 查詢邏輯：

```sql
WHERE
(
    日期 = last_date AND 小時 > last_hour
)
OR
(
    日期 > last_date
)
```

---

### 重要補充：

* 不會重抓整天
* 只補「上次停在的位置之後」
* 支援資料延遲寫入（late arrival）

---

# 🧠 水位線設計

### 定義：

```
watermark = (最後成功處理的日期, 小時)
```

### 用途：

* 控制增量範圍
* 避免重複抓取
* 支援斷點續跑

---

# 🚨 去重機制

## STG 去重：

使用唯一鍵：

```
(room_id, energy_date, energy_hour, metric_type, metric_name)
```

並搭配：

```sql
ON CONFLICT DO NOTHING
```

---

## RAW 去重：

```
(date, hour)
```

---

# 🔄 transform 邏輯（RAW → STG）

RAW 每個欄位會轉成 metric：

| RAW欄位  | STG映射         |
| ------ | ------------- |
| PC_L1  | 插座 / power_l1 |
| Light1 | 照明 / zone_1   |
| AC_A   | 空調 / A        |

---

# ⏱ 排程設計

## 🐳 執行方式

本系統採用：

> Docker + Cron 定時執行 ETL 任務

所有 ETL 程式在 container 內運行，透過 cron 控制週期。

---

## 🕐 執行頻率

```
每小時執行一次
```

建議 cron：

```
0 * * * * python -m marts.main
```

---

## 🔄 每小時 ETL 行為

每次執行會：

### ① RAW 層

* 根據水位線抓取新增資料
* 只補「最後成功點之後的資料」
* 跨日自動處理

---

### ② STG 層

* 同樣依水位線增量
* 補齊「未完成的當日資料」
* 轉換為 metric schema
* 自動去重

---

# ⚙️ 設計核心理念

## 1️⃣ RAW 是增量落地層

* 只負責存資料
* 不做語意處理

---

## 2️⃣ STG 是分析層

* metric 正規化
* 支援 BI / dashboard

---

## 3️⃣ ETL 是可重跑的（idempotent）

* 同一批資料重跑不會造成錯誤
* 不依賴單次成功

---

# 🚨 常見問題

## Q1：為什麼不用固定回補 N 天？

因為：

* 你已經有 watermark
* 固定回補會造成重複 IO
* 沒必要掃描歷史資料

---

## Q2：為什麼 STG 不會重複？

因為：

* ON CONFLICT DO NOTHING
* 唯一鍵控制

---

## Q3：為什麼會有 late data？

因為：

* sensor delay
* API 延遲
* 資料補寫

---

## Q4：為什麼要將多張來源表整合為一張 STG 表？

因為：

* Dashboard 效能：為了支援 Dashboard 的即時交叉分析，採用「寬表 (Wide Table) 轉 長表 (Long Table)」的正規化模型（Metric Schema）。若為每一張表都建立獨立的查詢邏輯，將導致前端連線與 SQL 計算複雜度指數級上升。
* 差異解釋：RAW 層與 STG 層筆數差異，係因「資料模型轉換（Mapping）」所致，屬正常設計行為。所有指標均已通過唯一鍵 (Unique Key) 去重與標準化，請以 STG 層之數據為準。

---

# 🏁 總結

本系統採用：

> ✔ 水位線增量 + 尾巴補齊 + 去重寫入

達成：

* 不漏資料
* 不重複資料
* 支援延遲寫入
* 支援每日排程
* 可重跑安全

---