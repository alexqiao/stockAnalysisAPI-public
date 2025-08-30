# DeepSeek API 集成指南

本文档介绍如何在股票分析API项目中集成和使用DeepSeek在线模型API。

## 功能概述

项目现在支持两种AI模型：
1. **Ollama本地模型** - 使用本地部署的Ollama服务
2. **DeepSeek在线模型** - 使用DeepSeek的在线API服务

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# AI Model Selection
AI_MODEL_TYPE=ollama  # ollama or deepseek
```

### 参数说明

- `DEEPSEEK_API_KEY`: 你的DeepSeek API密钥
- `DEEPSEEK_API_URL`: DeepSeek API端点（通常不需要修改）
- `DEEPSEEK_MODEL`: 使用的DeepSeek模型（默认：deepseek-chat）
- `AI_MODEL_TYPE`: 模型类型选择，可选值：`ollama` 或 `deepseek`

## 获取DeepSeek API密钥

1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台中获取API密钥
4. 将API密钥填入 `.env` 文件中的 `DEEPSEEK_API_KEY`

## 切换模型类型

### 方法1：修改环境变量

在 `.env` 文件中修改 `AI_MODEL_TYPE`：

```env
# 使用DeepSeek在线模型
AI_MODEL_TYPE=deepseek

# 使用Ollama本地模型
AI_MODEL_TYPE=ollama
```

### 方法2：运行时配置

你也可以在启动应用时设置环境变量：

```bash
# 使用DeepSeek
export AI_MODEL_TYPE=deepseek
python run.py

# 使用Ollama
export AI_MODEL_TYPE=ollama
python run.py
```

## 测试连接

项目提供了测试脚本来验证DeepSeek API连接：

```bash
# 测试DeepSeek连接
python test_deepseek.py

# 或者直接运行（需要先设置AI_MODEL_TYPE=deepseek）
export AI_MODEL_TYPE=deepseek
python test_deepseek.py
```

## 使用说明

### 1. 配置DeepSeek API密钥

首先，确保你已获取有效的DeepSeek API密钥，并在 `.env` 文件中正确配置。

### 2. 切换模型类型

根据需要选择使用的模型：
- 开发和测试阶段：可以使用Ollama本地模型（免费）
- 生产环境：建议使用DeepSeek在线模型（稳定可靠）

### 3. 验证配置

运行测试脚本确认配置正确：

```bash
python test_deepseek.py
```

### 4. 启动应用

正常启动应用即可，AI分析器会自动根据配置选择相应的模型服务。

```bash
python run.py
```

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `DEEPSEEK_API_KEY` 是否正确
   - 确认API密钥是否有足够的额度

2. **连接超时**
   - 检查网络连接
   - 确认API端点URL是否正确

3. **模型不响应**
   - 检查 `DEEPSEEK_MODEL` 参数是否正确
   - 确认模型服务是否正常

### 调试模式

如果需要更详细的调试信息，可以修改 `services/ai_analyzer.py` 中的日志输出级别。

## 性能考虑

- **DeepSeek在线模型**: 响应速度取决于网络状况和API负载，但通常更稳定
- **Ollama本地模型**: 响应速度取决于本地硬件性能，但无需网络连接

## 成本考虑

- DeepSeek API按token数量计费，请关注使用量
- Ollama本地模型完全免费，但需要本地硬件资源

## 备份配置

建议保留原有的Ollama配置作为备份，以便在需要时可以快速切换回本地模型。

---

如有任何问题，请参考DeepSeek官方文档或联系技术支持。
