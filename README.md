# 即時空氣品質監測與分析工具

一個專業的 Python 應用程式，用於即時空氣品質監測、數據收集和分析。

## 功能特色

- 從多個 API 收集即時 AQI 數據
- 數據儲存和管理
- 互動式儀表板和視覺化
- 自動數據更新
- 歷史數據分析
- 空氣品質不良警報系統

## 專案結構

```
├── data/              # 原始數據儲存
├── outputs/           # 處理後的輸出和視覺化圖表
├── src/               # 原始程式碼（待創建）
├── tests/             # 測試文件（待創建）
├── .env               # 環境變數和 API 金鑰
├── .gitignore         # Git 忽略文件
├── requirements.txt   # Python 依賴套件
└── README.md         # 專案文件
```

## 設置步驟

1. 複製儲存庫
2. 創建虛擬環境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 系統：venv\Scripts\activate
   ```
3. 安裝依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
4. 在 `.env` 文件中配置 API 金鑰：
   - OpenWeatherMap API 金鑰
   - AirVisual API 金鑰
   - EPA API 金鑰

## API 金鑰設置

1. **OpenWeatherMap**：在 https://openweathermap.org/api 註冊
2. **AirVisual**：在 https://www.airvisual.com/air-pollution-api 註冊
3. **EPA**：在 https://www.epa.gov/air-data 註冊

將 `.env` 文件中的預留位置值替換為您的實際 API 金鑰。

## 使用方式

```python
# 使用範例（待實作）
from src.aqi_monitor import AQIMonitor

monitor = AQIMonitor()
monitor.start_monitoring()
```

## 數據來源

- OpenWeatherMap 空氣污染 API
- AirVisual API
- EPA 空氣品質 API

## 貢獻指南

1. 分支儲存庫
2. 創建功能分支
3. 進行更改
4. 添加測試
5. 提交拉取請求

## 授權

MIT 授權
