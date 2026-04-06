# MemoChat - Local AI Memory Routing System

A modular local AI memory routing system that can interface with llama.cpp server. Provides structured memory management with query/write markers.

## Features

- **Structured Memory Management**: Store and retrieve memories using category/key/value pairs
- **Memory Markers Protocol**: Use `#[MEM_QUERY: category=X, key=Y]` and `#[MEM_WRITE: ...]` for AI interaction
- **SQLite with WAL Mode**: Persistent storage with concurrent access support
- **Llama.cpp Compatibility**: Direct integration with llama.cpp server API
- **Configurable**: Environment-based configuration for API keys, timeouts, and more

## Project Structure

```
MemoChat/
├── memochat/              # Main package
│   ├── __init__.py       # Package exports
│   ├── config.py         # Configuration
│   ├── db_handler.py     # Database operations
│   ├── llama_client.py   # Llama API client
│   ├── memory_router.py  # Memory routing logic
│   └── pipeline.py       # Main pipeline
├── tests/                # Test files
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project metadata
├── .env.example          # Environment template
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

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Command Line

```bash
# Interactive mode
python main.py

# Single query
python main.py -i "Your question here"

# Verbose mode
python main.py -i "Your question" -v
```

### Python API

```python
from memochat import MemoryPipeline, run_single_query

# Single query
result = run_single_query("What is my name?")

# Using pipeline
pipeline = MemoryPipeline()
response = pipeline.process_input("Hello!")
history = pipeline.get_history()
```

## AI Interaction Protocol

The system uses special markers for AI communication:

- **Query Memory**: `#[MEM_QUERY: category=分类, key=键]`
- **Write Memory**: `#[MEM_WRITE: category=分类, key=键, value=内容]`
- **Empty Memory**: `#[MEM_EMPTY: category=分类, key=键]`

## Configuration

Edit `.env` file:

```env
DB_PATH=memochat.db
LLAMA_API_URL=http://localhost:8080/v1/chat/completions
LLAMA_API_KEY=your_api_key_here
LLAMA_TIMEOUT=120
LLAMA_TEMPERATURE=0.7
LLAMA_MAX_TOKENS=1024
LOG_LEVEL=INFO
```

## License

MIT
