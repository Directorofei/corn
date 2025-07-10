"""
Dify API 配置模块
"""

# Dify 基础配置
BASE_URL = "http://192.168.163.1/v1"
API_KEY = "app-YRqDrxrIoSEeZdCe4cGEzAjM"

# 各功能Agent ID
AGENT_IDS = {
    "disease_detection": "dgwDnRc6UgpK01z0",  # 病害识别
    "diagnosis": "xxxxx123456",             # 病情诊断
    "pesticide_recommend": "CQOpi0xo0y9Z26EH" # 农药推荐
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": "app.log"
}

# 超时设置(秒)
TIMEOUT = 30