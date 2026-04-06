# MemoChat - 本地 AI 内存路由系统

一个模块化的本地 AI 内存路由系统，可与 llama.cpp 服务器对接。提供结构化的内存管理，支持查询/写入标记协议。

## 功能特性

- **结构化内存管理**：使用类别/键/值对存储和检索记忆
- **内存标记协议**：使用 `#[MEM_QUERY: category=X, key=Y]` 和 `#[MEM_WRITE: ...]` 进行 AI 交互
- **SQLite WAL 模式**：支持并发访问的持久化存储
- **Llama.cpp 兼容性**：直接集成 llama.cpp 服务器 API
- **简洁 API**：易于使用的 `MemoChat` 类，提供 `.chat()` 方法

## 项目结构

```
MemoChat/
├── memochat/              # 主要包
│   ├── __init__.py       # 包导出（包含 MemoChat 类）
│   ├── config.py         # 配置文件
│   ├── db_handler.py     # 数据库操作
│   ├── llama_client.py   # Llama API 客户端
│   ├── memory_router.py  # 内存路由逻辑
│   └── version.py        # 版本信息
├── tests/                # 测试文件
├── main.py               # 入口文件
├── requirements.txt      # 依赖项
├── pyproject.toml        # 项目元数据
└── README.md
```

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd MemoChat

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### Python API（推荐）

```python
from memochat import MemoChat

# 使用自定义设置初始化
memo = MemoChat(
    api_url="http://localhost:8080/v1/chat/completions",
    api_key="your_api_key_here",
    model="GLM-5",
    db_path="memochat.db",
    log_level="INFO",
)

# 聊天
response = memo.chat("你好！")

# 获取对话历史
history = memo.get_history()

# 获取所有记忆
memories = memo.get_memory()

# 重置对话
memo.reset()
```

### 命令行

```bash
# 交互模式
python main.py --api-url "http://localhost:8080/v1/chat/completions" --api-key "your_key" --model "GLM-5" --db-path "memochat.db"

# 单次查询
python main.py -i "你的问题" --api-url "http://localhost:8080/v1/chat/completions" --api-key "your_key" --model "GLM-5" --db-path "memochat.db"

# 详细模式
python main.py -i "你的问题" -v --api-key "your_key"
```

### 命令行参数

| 参数 | 短参数 | 描述 |
|------|--------|------|
| `--input` | `-i` | 单次输入查询并处理 |
| `--verbose` | `-v` | 启用详细/调试日志 |
| `--api-url` | | Llama API URL（默认：http://localhost:8080/v1/chat/completions） |
| `--api-key` | | Llama API 密钥 |
| `--model` | | 模型名称 |
| `--db-path` | | 数据库路径（默认：memochat.db） |

## AI 交互协议

系统使用特殊标记进行 AI 通信：

- **查询记忆**：`#[MEM_QUERY: category=分类, key=键]`
- **写入记忆**：`#[MEM_WRITE: category=分类, key=键, value=内容]`
- **空记忆**：`#[MEM_EMPTY: category=分类, key=键]`

## 配置

配置可通过命令行参数或 Python API 进行。默认值：

| 设置项 | 默认值 | 描述 |
|--------|--------|------|
| `api_url` | `http://localhost:8080/v1/chat/completions` | Llama API URL |
| `api_key` | （空） | API 认证密钥 |
| `model` | （空） | 使用的模型名称 |
| `db_path` | `memochat.db` | 数据库文件路径 |
| `temperature` | `0.7` | AI 温度参数 |
| `max_tokens` | `1024` | 最大生成 token 数 |
| `timeout` | `120` | API 超时时间（秒） |
| `log_level` | `INFO` | 日志级别 |

## 许可证

LGPL-3.0