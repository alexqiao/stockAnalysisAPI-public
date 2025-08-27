# 股票分析系统

一个基于FastAPI的股票分析系统，集成Alpha Vantage API获取实时股票数据，使用Ollama进行AI分析。

## 功能特性

- 🔐 用户认证和授权
- 📈 实时股票数据获取
- 🤖 AI驱动的股票分析
- 📰 新闻情绪分析
- 📊 技术分析指标
- 🧪 完整的测试套件

## 技术栈

- **后端**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT
- **AI分析**: Ollama + Llama 2
- **股票数据**: Alpha Vantage API
- **测试**: pytest + responses

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd stockAPI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要的配置：
```bash
# Alpha Vantage API密钥
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Ollama配置
OLLAMA_API_URL=http://localhost:11434

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 启动服务

#### 启动Ollama服务
```bash
# 启动Ollama
ollama serve

# 拉取Llama 2模型
ollama pull llama2
```

#### 启动FastAPI应用
```bash
# 开发模式
python run.py

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API文档

启动服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### 认证相关
- `POST /api/register` - 用户注册
- `POST /api/token` - 获取访问令牌
- `GET /api/users/me` - 获取当前用户信息

### 股票分析
- `GET /api/analyze/{symbol}` - 分析指定股票
- `GET /api/health` - 健康检查

## 测试

### 运行所有测试
```bash
python run_tests.py
```

### 运行特定类型测试
```bash
# 单元测试
python run_tests.py --type unit

# 集成测试
python run_tests.py --type integration

# 详细输出
python run_tests.py -v

# 生成覆盖率报告
python run_tests.py --coverage
```

### 手动运行测试
```bash
# 安装测试依赖
pip install -r tests/test_requirements.txt

# 运行测试
pytest tests/ -v
```

## 项目结构

```
stockAPI/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI应用入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic模型
│   ├── auth.py          # 认证逻辑
│   └── routers/         # API路由
│       ├── __init__.py
│       ├── auth.py      # 认证路由
│       └── analysis.py  # 分析路由
├── services/
│   ├── __init__.py
│   ├── alpha_vantage_api.py  # Alpha Vantage API封装
│   └── ai_analyzer.py        # AI分析服务
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 测试配置
│   ├── test_requirements.txt # 测试依赖
│   ├── unit/               # 单元测试
│   │   ├── __init__.py
│   │   ├── test_alpha_vantage_api.py
│   │   └── test_ai_analyzer.py
│   └── integration/        # 集成测试
│       ├── __init__.py
│       ├── test_auth_flow.py
│       └── test_stock_analysis_flow.py
├── run.py                 # 应用启动脚本
├── run_tests.py          # 测试运行器
├── requirements.txt      # 项目依赖
├── .env.example         # 环境变量模板
└── README.md            # 项目文档
```

## 开发指南

### 添加新功能
1. 在 `app/routers/` 中添加新的路由文件
2. 在 `app/schemas.py` 中定义请求/响应模型
3. 在 `services/` 中添加业务逻辑
4. 在 `tests/` 中添加对应的测试

### 代码规范
- 使用PEP 8风格指南
- 添加类型注解
- 编写文档字符串
- 保持测试覆盖率 > 80%

## 故障排除

### 常见问题

1. **Ollama连接失败**
   - 确保Ollama服务已启动：`ollama serve`
   - 检查OLLAMA_API_URL配置是否正确

2. **Alpha Vantage API限制**
   - 免费版限制：5次/分钟，500次/天
   - 考虑升级API套餐或实现缓存机制

3. **测试失败**
   - 确保测试依赖已安装：`pip install -r tests/test_requirements.txt`
   - 检查环境变量是否正确设置

## 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
