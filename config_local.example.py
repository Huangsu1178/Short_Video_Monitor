"""
TikTok Monitor - 本地配置模板（可选）

⚠️ 推荐使用 .env 文件进行配置（见 .env.example）
此文件仅用于向后兼容，新用户建议使用 .env 文件

注意：config_local.py 已加入 .gitignore，不会被提交到版本控制系统
"""

# ==================== 使用说明 ====================
# 推荐方式：使用 .env 文件（更简单直观）
# 1. 复制 .env.example 为 .env
# 2. 编辑 .env 文件，填入你的配置
#
# 此文件（config_local.py）仅在你需要更多自定义配置时使用
# ====================================================

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
