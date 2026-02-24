#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動安裝和設置腳本
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """執行命令並處理錯誤"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"🐍 Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    return True

def create_virtual_environment():
    """創建虛擬環境"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 虛擬環境已存在")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "創建虛擬環境")

def install_requirements():
    """安裝依賴套件"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt 文件不存在")
        return False
    
    # 根據作業系統選擇 pip 執行檔
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # 升級 pip
    run_command(f"{pip_cmd} install --upgrade pip", "升級 pip")
    
    # 安裝依賴套件
    return run_command(f"{pip_cmd} install -r requirements.txt", "安裝依賴套件")

def check_env_file():
    """檢查 .env 文件"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        return False
    
    # 檢查 API 金鑰是否設置
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'your_epa_taiwan_api_key_here' in content:
            print("⚠️  請在 .env 文件中設置您的環境部 API 金鑰")
            return False
    
    print("✅ .env 文件檢查通過")
    return True

def create_directories():
    """創建必要的目錄"""
    directories = ['data', 'outputs']
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"📁 目錄 {directory} 已準備")

def run_test():
    """執行測試運行"""
    print("\n🧪 執行測試運行...")
    
    # 根據作業系統選擇 Python 執行檔
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} aqi_monitor.py", "執行 AQI 監測程式")

def main():
    """主設置流程"""
    print("=" * 60)
    print("🌍 台灣 AQI 監測系統 - 自動安裝程式")
    print("=" * 60)
    
    # 檢查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 創建虛擬環境
    if not create_virtual_environment():
        sys.exit(1)
    
    # 安裝依賴套件
    if not install_requirements():
        sys.exit(1)
    
    # 檢查 .env 文件
    if not check_env_file():
        print("\n📝 請編輯 .env 文件，設置您的環境部 API 金鑰")
        print("🔑 獲取 API 金鑰：https://data.moenv.gov.tw/")
        sys.exit(1)
    
    # 創建目錄
    create_directories()
    
    print("\n" + "=" * 60)
    print("🎉 安裝完成！")
    print("=" * 60)
    
    # 詢問是否執行測試
    response = input("\n是否要立即執行 AQI 監測程式？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        run_test()
    else:
        print("\n📋 後續步驟：")
        print("1. 啟動虛擬環境：")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("   source venv/bin/activate")
        print("2. 執行程式：")
        print("   python aqi_monitor.py")
        print("3. 查看結果：")
        print("   打開 outputs/taiwan_aqi_map.html")

if __name__ == "__main__":
    main()
