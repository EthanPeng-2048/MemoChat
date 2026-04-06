# MemoChat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server. Provides structured memory management with query/write markers.

## Features

- **Structured Memory Management**: Store and retrieve memories using category/key/value pairs
- **Memory Markers Protocol**: Use `#[MEM_QUERY: category=X, key=Y]` and `#[MEM_WRITE: ...]` for AI interaction
- **SQLite with WAL Mode**: Persistent storage with concurrent access support
- **Llama.cpp Compatibility**: Direct integration with llama.cpp server API
- **Simple API**: Easy-to-use `MemoChat` class with `.chat()` method

## Project Structure

```
MemoChat/
├── memochat/              # Main package
│   ├── __init__.py       # Package exports (includes MemoChat class)
│   ├── config.py         # Configuration
│   ├── db_handler.py     # Database operations
│   ├── llama_client.py   # Llama API client
│   ├── memory_router.py  # Memory routing logic
│   └── version.py        # Version info
├── tests/                # Test files
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project metadata
└── README.md
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd MemoChat

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Python API (Recommended)

```python
from memochat import MemoChat

# Initialize with custom settings
memo = MemoChat(
    api_url="http://localhost:8080/v1/chat/completions",
    api_key="your_api_key_here",
    model="GLM-5",
    db_path="memochat.db",
    log_level="INFO",
)

# Chat
response = memo.chat("你好！")

# Get conversation history
history = memo.get_history()

# Get all memories
memories = memo.get_memory()

# Reset conversation
memo.reset()
```

### Command Line

```bash
# Interactive mode
python main.py --api-url "http://localhost:8080/v1/chat/completions" --api-key "your_key" --model "GLM-5" --db-path "memochat.db"

# Single query
python main.py -i "Your question here" --api-url "http://localhost:8080/v1/chat/completions" --api-key "your_key" --model "GLM-5" --db-path "memochat.db"

# Verbose mode
python main.py -i "Your question" -v --api-key "your_key"
```

### Command Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--input` | `-i` | Single input query to process |
| `--verbose` | `-v` | Enable verbose/debug logging |
| `--api-url` | | Llama API URL (default: http://localhost:8080/v1/chat/completions) |
| `--api-key` | | Llama API Key |
| `--model` | | Model name |
| `--db-path` | | Database path (default: memochat.db) |

## AI Interaction Protocol

The system uses special markers for AI communication:

- **Query Memory**: `#[MEM_QUERY: category=分类, key=键]`
- **Write Memory**: `#[MEM_WRITE: category=分类, key=键, value=内容]`
- **Empty Memory**: `#[MEM_EMPTY: category=分类, key=键]`

## Configuration

Configuration is done through command line arguments or the Python API. Default values:

| Setting | Default | Description |
|---------|---------|-------------|
| `api_url` | `http://localhost:8080/v1/chat/completions` | Llama API URL |
| `api_key` | (empty) | API key for authentication |
| `model` | (empty) | Model name to use |
| `db_path` | `memochat.db` | Database file path |
| `temperature` | `0.7` | AI temperature parameter |
| `max_tokens` | `1024` | Maximum tokens to generate |
| `timeout` | `120` | API timeout in seconds |
| `log_level` | `INFO` | Logging level |

## License

LGPL-3.0
