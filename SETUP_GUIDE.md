# TikTok Monitor - 配置指南

本指南将帮助你快速配置 TikTok Monitor 项目。

## 📋 目录

- [快速开始](#快速开始)
- [配置方式](#配置方式)
  - [方式一：使用 .env 文件（推荐）](#方式一使用-env-文件推荐)
  - [方式二：使用 config_local.py 文件](#方式二使用-config_localpy-文件)
  - [方式三：使用环境变量](#方式三使用环境变量)
- [详细配置说明](#详细配置说明)
  - [OpenAI API 配置](#openai-api-配置)
  - [代理配置](#代理配置)
  - [其他配置](#其他配置)
- [常见问题](#常见问题)

---

## 快速开始

1. **复制配置模板**

   ```bash
   # 复制 .env 模板
   cp .env.example .env
   
   # 或复制 config_local 模板
   cp config_local.example.py config_local.py
   ```

2. **编辑配置文件**，填入你的 API Key

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**

   ```bash
   python main.py
   ```

---

## 配置方式

本项目支持三种配置方式，优先级从高到低：

1. `.env` 文件（推荐）
2. `config_local.py` 文件
3. 系统环境变量

### 方式一：使用 .env 文件（推荐）

**优点**：简单直观，所有配置集中管理

**步骤**：

1. 复制模板文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件：
   ```env
   OPENAI_API_KEY=your-actual-api-key-here
   OPENAI_API_BASE=  # 留空使用官方 API
   ```

3. 保存后运行程序即可

### 方式二：使用 config_local.py 文件

**优点**：支持更多配置项，包括代理设置

**步骤**：

1. 复制模板文件：
   ```bash
   cp config_local.example.py config_local.py
   ```

2. 编辑 `config_local.py` 文件：
   ```python
   AI_LOCAL_CONFIG = {
       "api_key": "your-actual-api-key-here",
       "api_base": "",  # 留空使用官方 API
       "default_model": "gpt-5-chat-latest",
   }
   
   SCRAPER_LOCAL_CONFIG = {
       "proxy_url": "",  # 如需要代理，填入代理地址
   }
   ```

3. 保存后运行程序即可

### 方式三：使用环境变量

**优点**：适合生产环境或 Docker 部署

**Windows (PowerShell)**：
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
python main.py
```

**Windows (CMD)**：
```cmd
set OPENAI_API_KEY=your-api-key-here
python main.py
```

**Linux/Mac**：
```bash
export OPENAI_API_KEY="your-api-key-here"
python main.py
```

---

## 详细配置说明

### OpenAI API 配置

#### 获取 API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录或注册账号
3. 点击 "Create new secret key"
4. 复制生成的 API Key

#### API Base 配置

- **官方 API**：留空或删除该行
- **第三方代理**：填入代理地址，例如：
  ```
  OPENAI_API_BASE=https://your-proxy.com/v1
  ```

#### 模型选择

默认使用 `gpt-5-chat-latest`，你可以在 `config_local.py` 中修改：

```python
AI_LOCAL_CONFIG = {
    "default_model": "gpt-4o",  # 或其他支持的模型
}
```

### 代理配置

如果你需要代理访问 TikTok，可以配置代理：

**方式一：在 config_local.py 中配置**
```python
SCRAPER_LOCAL_CONFIG = {
    "proxy_url": "http://127.0.0.1:7890",
}
```

**方式二：在 .env 中配置**
```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 其他配置

项目中还有其他可配置项，都在 [config.py](config.py) 中：

- **数据库配置**：`DB_CONFIG`
- **抓取配置**：`SCRAPER_CONFIG`
- **调度器配置**：`SCHEDULER_CONFIG`
- **UI 配置**：`UI_CONFIG`
- **业务规则配置**：`BUSINESS_CONFIG`

一般情况下，使用默认值即可，无需修改。

---

## 常见问题

### Q1: 提示 "API Key 未配置" 怎么办？

确保你已经：
1. 复制了配置模板文件（`.env` 或 `config_local.py`）
2. 在文件中填入了有效的 API Key
3. 保存文件后重新启动程序

### Q2: 使用第三方代理如何配置？

在 `.env` 文件中添加：
```env
OPENAI_API_BASE=https://your-proxy.com/v1
```

或在 `config_local.py` 中：
```python
AI_LOCAL_CONFIG = {
    "api_base": "https://your-proxy.com/v1",
}
```

### Q3: 配置文件应该放在哪里？

配置文件应该放在项目根目录，与 `main.py` 同级：

```
tiktok_monitor/
├── main.py
├── config.py
├── .env              ← 放在这里
├── config_local.py   ← 或放在这里
└── ...
```

### Q4: 为什么我的配置没有生效？

检查以下几点：
1. 文件名是否正确（`.env` 或 `config_local.py`）
2. 文件是否在项目根目录
3. 是否正确保存了文件
4. 是否重新启动了程序
5. 查看控制台是否有加载配置的提示信息

### Q5: 可以同时使用多种配置方式吗？

可以，优先级为：
1. `.env` 文件（最高）
2. `config_local.py` 文件
3. 系统环境变量（最低）

高优先级的配置会覆盖低优先级的配置。

---

## 安全提示

⚠️ **重要**：
- 不要将 `.env` 或 `config_local.py` 文件提交到 Git
- 不要将 API Key 分享给他人
- 定期轮换你的 API Key
- 如果 API Key 泄露，立即在 OpenAI 平台撤销并重新生成

这些文件已经添加到 `.gitignore`，正常情况下不会被提交。

---

## 需要帮助？

如果遇到问题，请：
1. 检查控制台输出的错误信息
2. 查看本指南的常见问题部分
3. 查阅项目的 README.md
4. 提交 Issue 寻求帮助
