"""
TikTok Monitor - 本地配置模板
复制此文件为 config_local.py 并填入你的配置信息

注意：config_local.py 已加入 .gitignore，不会被提交到版本控制系统
"""

# ==================== AI 配置 ====================
# 从环境变量读取或使用下面的配置
# 推荐方式：设置环境变量 OPENAI_API_KEY
# Windows: setx OPENAI_API_KEY "your-api-key-here"
# Linux/Mac: export OPENAI_API_KEY="your-api-key-here"

AI_LOCAL_CONFIG = {
    # API Key（推荐从环境变量读取，留空则使用环境变量）
    "api_key": "",  # 在此填入你的 OpenAI API Key
    
    # API Base（如果使用第三方代理，填入代理地址）
    # 官方 API: 留空
    # 第三方代理: "https://your-proxy.com/v1"
    "api_base": "",
    
    # 使用的模型
    "default_model": "gpt-5-chat-latest",
}


# ==================== 代理配置 ====================
SCRAPER_LOCAL_CONFIG = {
    # 代理 URL（如果需要翻墙访问 TikTok）
    # 例如: "http://127.0.0.1:7890"
    "proxy_url": "",
}


# ==================== 使用方式 ====================
# 1. 复制此文件为 config_local.py
# 2. 填入你的 API Key 和代理配置
# 3. 在 config.py 中导入并使用：
#
# try:
#     from config_local import AI_LOCAL_CONFIG, SCRAPER_LOCAL_CONFIG
#     AI_CONFIG.update(AI_LOCAL_CONFIG)
#     SCRAPER_CONFIG.update(SCRAPER_LOCAL_CONFIG)
# except ImportError:
#     pass  # config_local.py 不存在，使用默认配置
