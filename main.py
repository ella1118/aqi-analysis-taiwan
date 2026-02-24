#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣即時空氣品質監測系統
串接環境部 API 並使用 Folium 在地圖上顯示 AQI 數據
"""

import os
import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import json
from datetime import datetime
from dotenv import load_dotenv
import logging
import urllib3
import math
from geopy.distance import geodesic

# 禁用 SSL 警告（僅用於開發環境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AQIMonitor:
    def __init__(self):
        """初始化 AQI 監測器"""
        self.api_key = os.getenv('MOENV_API_KEY')
        self.base_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        self.data = None
        self.map = None
        
        # 台北車站座標
        self.taipei_station = [25.0478, 121.5170]
        
        # 台灣主要測站座標數據
        self.station_coordinates = {
            "汐止": [25.0645, 121.6321],
            "中山": [25.0645, 121.5241],
            "大安": [25.0263, 121.5438],
            "古亭": [25.0128, 121.5274],
            "松山": [25.0477, 121.5750],
            "士林": [25.0877, 121.5240],
            "大同": [25.0645, 121.5178],
            "內湖": [25.0698, 121.5808],
            "南港": [25.0548, 121.6069],
            "文山": [24.9876, 121.5718],
            "板橋": [25.0167, 121.4624],
            "新莊": [25.0358, 121.4497],
            "土城": [24.9791, 121.4599],
            "蘆洲": [25.0848, 121.4660],
            "三重": [25.0829, 121.4914],
            "淡水": [25.1646, 121.4459],
            "林口": [25.0789, 121.3198],
            "桃園": [24.9936, 121.3010],
            "中壢": [24.9539, 121.2256],
            "平鎮": [24.9446, 121.2188],
            "龍潭": [24.8626, 121.2299],
            "新竹": [24.8138, 120.9675],
            "竹東": [24.7446, 121.0865],
            "苗栗": [24.5629, 120.8214],
            "頭份": [24.6876, 120.8806],
            "台中": [24.1477, 120.6736],
            "沙鹿": [24.2332, 120.5654],
            "豐原": [24.2525, 120.7176],
            "大里": [24.0995, 120.6788],
            "彰化": [24.0766, 120.5422],
            "員林": [23.9623, 120.5744],
            "南投": [23.9099, 120.6838],
            "雲林": [23.7090, 120.4316],
            "斗六": [23.7089, 120.4316],
            "嘉義": [23.4801, 120.4491],
            "朴子": [23.4619, 120.2479],
            "台南": [22.9999, 120.2269],
            "新營": [23.3005, 120.3169],
            "善化": [23.1327, 120.2995],
            "高雄": [22.6273, 120.3014],
            "林園": [22.5019, 120.3943],
            "大寮": [22.5598, 120.3543],
            "鳳山": [22.6287, 120.3566],
            "左營": [22.6900, 120.2982],
            "楠梓": [22.7287, 120.3014],
            "小港": [22.5667, 120.3512],
            "屏東": [22.6828, 120.4908],
            "恆春": [22.0011, 120.7460],
            "宜蘭": [24.6929, 121.7355],
            "羅東": [24.6770, 121.7707],
            "花蓮": [23.9979, 121.6070],
            "台東": [22.7560, 121.1606],
            "馬祖": [26.1634, 119.9518],
            "金門": [24.4368, 118.3168],
            "澎湖": [23.5697, 119.5802]
        }
        
    def fetch_aqi_data(self):
        """從環境部 API 獲取即時 AQI 數據"""
        try:
            params = {
                'api_key': self.api_key,
                'format': 'json',
                'limit': 100  # 獲取所有測站數據
            }
            
            logger.info("正在獲取環境部 AQI 數據...")
            response = requests.get(self.base_url, params=params, timeout=30, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            # 環境部 API 直接返回數組格式
            if isinstance(data, list):
                self.data = data
                logger.info(f"成功獲取 {len(self.data)} 個測站的數據")
                return True
            elif 'records' in data:
                self.data = data['records']
                logger.info(f"成功獲取 {len(self.data)} 個測站的數據")
                return True
            else:
                logger.error(f"API 回應格式錯誤: {type(data)}")
                logger.error(f"回應內容: {data}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取數據時發生錯誤: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析錯誤: {e}")
            return False
    
    def process_data(self):
        """處理和清理 AQI 數據"""
        if not self.data:
            return None
            
        # 轉換為 DataFrame
        df = pd.DataFrame(self.data)
        
        # 選擇需要的欄位
        columns_to_keep = [
            'sitename',      # 測站名稱
            'county',        # 縣市
            'aqi',           # AQI 值
            'pm25',          # PM2.5
            'pm10',          # PM10
            'o3',            # 臭氧
            'no2',           # 二氧化氮
            'so2',           # 二氧化硫
            'co',            # 一氧化碳
            'publishtime'    # 發布時間
        ]
        
        # 確保欄位存在
        available_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[available_columns]
        
        # 添加座標信息
        df['latitude'] = df['sitename'].map(lambda x: self.station_coordinates.get(x, [None, None])[0])
        df['longitude'] = df['sitename'].map(lambda x: self.station_coordinates.get(x, [None, None])[1])
        
        # 轉換數據類型
        numeric_columns = ['aqi', 'pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'latitude', 'longitude']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 移除無效座標的數據
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # 重命名 publishtime 為 datacreationdate 以保持一致性
        if 'publishtime' in df.columns:
            df = df.rename(columns={'publishtime': 'datacreationdate'})
        
        # 計算每個測站到台北車站的距離
        df['distance_to_taipei'] = df.apply(
            lambda row: self.calculate_distance_to_taipei(row['latitude'], row['longitude']), 
            axis=1
        )
        
        logger.info(f"處理完成，有效數據 {len(df)} 筆")
        return df
    
    def calculate_distance_to_taipei(self, lat, lon):
        """計算測站到台北車站的距離（公里）"""
        try:
            station_coords = (lat, lon)
            taipei_coords = (self.taipei_station[0], self.taipei_station[1])
            distance = geodesic(station_coords, taipei_coords).kilometers
            return round(distance, 2)
        except:
            return None
    
    def get_aqi_color(self, aqi_value):
        """根據 AQI 值返回對應顏色（簡化版）"""
        if aqi_value <= 50:
            return '#00E400'  # 綠色 - 良好
        elif aqi_value <= 100:
            return '#FFFF00'  # 黃色 - 中等
        else:
            return '#FF0000'  # 紅色 - 不健康
    
    def get_aqi_level(self, aqi_value):
        """根據 AQI 值返回空氣品質等級（簡化版）"""
        if aqi_value <= 50:
            return '良好'
        elif aqi_value <= 100:
            return '中等'
        else:
            return '不健康'
    
    def create_map(self, df):
        """創建 Folium 地圖並標示 AQI 測站"""
        if df.empty:
            logger.error("沒有有效數據可創建地圖")
            return None
            
        # 計算台灣中心點
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # 創建地圖
        self.map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 添加測站標記
        for idx, row in df.iterrows():
            aqi_value = row['aqi'] if pd.notna(row['aqi']) else 0
            color = self.get_aqi_color(aqi_value)
            level = self.get_aqi_level(aqi_value)
            
            # 創建彈出窗口內容（簡化版 + 距離）
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px;">
                <h4 style="margin: 5px 0; color: #333;">{row['sitename']}</h4>
                <p style="margin: 3px 0;"><strong>所在地：</strong>{row['county']}</p>
                <p style="margin: 3px 0;"><strong>AQI 數值：</strong><span style="color: {color}; font-weight: bold;">{aqi_value}</span></p>
                <p style="margin: 3px 0;"><strong>距離台北車站：</strong>{row['distance_to_taipei']} 公里</p>
                <p style="margin: 3px 0; font-size: 12px; color: #666;">等級：{level}</p>
            </div>
            """
            
            # 創建圓形標記
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8 + (aqi_value / 50),  # 根據 AQI 值調整大小
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['sitename']} - AQI: {aqi_value}",
                color='black',
                weight=1,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(self.map)
        
        # 添加台北車站標記
        folium.Marker(
            location=self.taipei_station,
            popup='<div style="font-family: Arial, sans-serif; text-align: center;"><h4 style="margin: 5px 0; color: #FF6B35;">🚄 台北車站</h4><p style="margin: 3px 0;">參考點座標</p></div>',
            tooltip="台北車站",
            icon=folium.Icon(color='red', icon='train', prefix='fa')
        ).add_to(self.map)
        
        # 添加圖例（簡化版）
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 180px; height: auto; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; border-radius: 5px; padding: 10px;">
        <p style="margin: 5px 0; font-weight: bold;">AQI 空氣品質指標</p>
        <p style="margin: 3px 0; color: #00E400;">● 0-50 良好</p>
        <p style="margin: 3px 0; color: #FFFF00;">● 51-100 中等</p>
        <p style="margin: 3px 0; color: #FF0000;">● 101+ 不健康</p>
        </div>
        '''
        self.map.get_root().html.add_child(folium.Element(legend_html))
        
        logger.info("地圖創建完成")
        return self.map
    
    def save_map(self, filename='outputs/taiwan_aqi_map.html'):
        """保存地圖到文件"""
        if self.map is None:
            logger.error("沒有地圖可保存")
            return False
            
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            self.map.save(filename)
            logger.info(f"地圖已保存至 {filename}")
            return True
        except Exception as e:
            logger.error(f"保存地圖時發生錯誤: {e}")
            return False
    
    def save_data(self, filename='outputs/aqi_data.csv'):
        """保存數據到 CSV 文件"""
        if self.data is None:
            logger.error("沒有數據可保存")
            return False
            
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            df = self.process_data()
            if df is not None:
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                logger.info(f"數據已保存至 {filename}")
                return True
        except Exception as e:
            logger.error(f"保存數據時發生錯誤: {e}")
            return False
    
    def run(self):
        """執行完整的監測流程"""
        logger.info("開始執行 AQI 監測流程")
        
        # 獲取數據
        if not self.fetch_aqi_data():
            logger.error("無法獲取 AQI 數據")
            return False
        
        # 處理數據
        df = self.process_data()
        if df is None or df.empty:
            logger.error("數據處理失敗")
            return False
        
        # 創建地圖
        aqi_map = self.create_map(df)
        if aqi_map is None:
            logger.error("地圖創建失敗")
            return False
        
        # 保存結果
        self.save_map()
        self.save_data()
        
        logger.info("AQI 監測流程完成")
        return True

def main():
    """主函數"""
    print("=" * 50)
    print("台灣即時空氣品質監測系統")
    print("=" * 50)
    
    # 檢查 API 金鑰
    if not os.getenv('MOENV_API_KEY'):
        print("錯誤：請在 .env 文件中設置 MOENV_API_KEY")
        return
    
    # 創建監測器並執行
    monitor = AQIMonitor()
    success = monitor.run()
    
    if success:
        print("\n✅ 監測完成！")
        print("📍 地圖文件：outputs/taiwan_aqi_map.html")
        print("📊 數據文件：outputs/aqi_data.csv")
        print("\n請在地圖文件中查看結果。")
    else:
        print("\n❌ 監測失敗，請檢查日誌訊息。")

if __name__ == "__main__":
    main()
