# py-operrouter

Python SDK for OperRouter - A unified SDK for DataSource and LLM operations with multiple transport options.

## Features

- ✅ **Three Transport Layers**: HTTP (JSON-RPC), gRPC (Protobuf), FFI (Direct Rust calls)
- 🔌 **DataSource Support**: PostgreSQL, MySQL, MongoDB, Redis, Kafka
- 🤖 **LLM Integration**: OpenAI, Claude, Ollama
- ⚡ **Async/Await**: Full async support with type hints
- 🛡️ **Type Safe**: Complete type definitions with dataclasses
- 📦 **Zero Dependencies**: FFI client uses only Python stdlib (ctypes)

## Installation

### Basic Installation

```bash
# Install from source
cd sdks/py-operrouter
pip install -e .
```

### Dependencies

- **HTTP Client**: Requires `httpx>=0.24.0`
- **gRPC Client**: Requires `grpcio>=1.50.0`, `protobuf>=4.21.0`
- **FFI Client**: No external dependencies (uses ctypes)

```bash
# Install with all transport layers
pip install -e ".[http,grpc]"

# Or install individually
pip install httpx  # For HTTP client
pip install grpcio protobuf  # For gRPC client
```

### Building FFI Library (for FFI Client)

```bash
cd ../../bridges/operrouter-core-ffi
cargo build --release
```

The FFI client will automatically search for the library in common locations. You can also set `OPERROUTER_FFI_PATH` to specify the library path.

## Quick Start

### HTTP Client (JSON-RPC)

```python
import asyncio
from py_operrouter import HTTPClient, DataSourceConfig

async def main():
    # Create HTTP client
    client = HTTPClient("http://localhost:8080")
    
    # Test connection
    ping_resp = await client.ping()
    print(f"Server alive: {ping_resp.success}")
    
    # Create datasource
    config = DataSourceConfig(
        driver="postgres",
        host="localhost",
        port=5432,
        database="mydb",
        username="user",
        password="pass"
    )
    
    create_resp = await client.create_datasource("my_db", config)
    
    # Query data
    query_resp = await client.query_datasource("my_db", "SELECT * FROM users")
    print(f"Found {len(query_resp.rows)} rows")
    
    # Close connection
    await client.close_datasource("my_db")

asyncio.run(main())
```

### gRPC Client (High Performance)

```python
import asyncio
from py_operrouter import GRPCClient, LLMConfig, ChatMessage

async def main():
    # Create gRPC client
    client = GRPCClient("localhost:50051")
    
    try:
        # Create LLM instance
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="sk-..."
        )
        
        await client.create_llm("my_llm", config)
        
        # Chat with LLM
        messages = [
            ChatMessage(role="system", content="You are helpful."),
            ChatMessage(role="user", content="Hello!")
        ]
        
        chat_resp = await client.chat_llm("my_llm", messages)
        print(f"Response: {chat_resp.text}")
        
        # Cleanup
        await client.close_llm("my_llm")
    
    finally:
        # Always close gRPC channel
        await client.close()

asyncio.run(main())
```

### FFI Client (Direct Rust Calls - Zero Overhead)

```python
import asyncio
from py_operrouter import FFIClient, DataSourceConfig

async def main():
    # Create FFI client (no network, direct Rust calls)
    client = FFIClient()
    
    # Test FFI connection
    ping_resp = await client.ping()
    print(f"FFI core alive: {ping_resp.success}")
    
    # Create MongoDB datasource
    config = DataSourceConfig(
        driver="mongodb",
        host="localhost",
        port=27017,
        database="testdb"
    )
    
    await client.create_datasource("my_mongo", config)
    
    # Query MongoDB
    query_resp = await client.query_datasource(
        "my_mongo",
        '{"find": "users", "limit": 10}'
    )
    
    print(f"Found {len(query_resp.rows)} documents")

asyncio.run(main())
```

## API Reference

### Client Classes

All three clients implement the same `OperRouterClient` protocol:

- **`HTTPClient(base_url: str)`** - JSON-RPC 2.0 over HTTP
- **`GRPCClient(address: str)`** - gRPC with Protobuf
- **`FFIClient(lib_path: Optional[str] = None)`** - Direct Rust FFI calls

### Core Methods

```python
# Test connection
await client.ping() -> PingResponse

# Validate TOML config
await client.validate_config(config_str: str) -> ConfigResponse

# Load operator config
await client.load_config(config_str: str) -> ConfigResponse

# Get metadata
await client.get_metadata(name: str) -> Metadata
```

### DataSource Methods

```python
# Create datasource
await client.create_datasource(
    name: str,
    config: DataSourceConfig
) -> DataSourceResponse

# Query (SELECT)
await client.query_datasource(
    name: str,
    query: str
) -> DataSourceQueryResponse

# Execute (DDL/DML)
await client.execute_datasource(
    name: str,
    statement: str
) -> DataSourceResponse

# Insert row
await client.insert_datasource(
    name: str,
    data: Dict[str, Any]
) -> DataSourceResponse

# Check health
await client.ping_datasource(name: str) -> DataSourceResponse

# Close connection
await client.close_datasource(name: str) -> DataSourceResponse
```

### LLM Methods

```python
# Create LLM instance
await client.create_llm(
    name: str,
    config: LLMConfig
) -> LLMResponse

# Generate completion
await client.generate_llm(
    name: str,
    prompt: str
) -> LLMGenerateResponse

# Chat conversation
await client.chat_llm(
    name: str,
    messages: List[ChatMessage]
) -> LLMChatResponse

# Get embeddings
await client.embedding_llm(
    name: str,
    text: str
) -> LLMEmbeddingResponse

# Check health
await client.ping_llm(name: str) -> LLMResponse

# Close instance
await client.close_llm(name: str) -> LLMResponse
```

## Configuration Types

### DataSource Configuration

```python
from py_operrouter import DataSourceConfig

config = DataSourceConfig(
    driver="postgres",      # postgres, mysql, mongodb, redis, kafka
    host="localhost",       # Database host
    port=5432,             # Database port
    database="mydb",       # Database name
    username="user",       # Optional username
    password="pass",       # Optional password
    options={}             # Optional driver-specific options
)
```

### LLM Configuration

```python
from py_operrouter import LLMConfig

config = LLMConfig(
    provider="openai",     # openai, claude, ollama
    model="gpt-3.5-turbo", # Model name
    api_key="sk-...",      # API key (not needed for Ollama)
    base_url=None,         # Optional custom endpoint
    options={}             # Optional provider-specific options
)
```

### Chat Messages

```python
from py_operrouter import ChatMessage

messages = [
    ChatMessage(role="system", content="You are helpful."),
    ChatMessage(role="user", content="Hello!"),
    ChatMessage(role="assistant", content="Hi there!"),
]
```

## Transport Comparison

| Feature | HTTP | gRPC | FFI |
|---------|------|------|-----|
| **Protocol** | JSON-RPC 2.0 | Protobuf | Direct calls |
| **Performance** | Good | Better | Best |
| **Network** | Required | Required | Not needed |
| **Setup** | Easiest | Moderate | Complex |
| **Use Case** | Web services | Microservices | Embedded/CLI |
| **Streaming** | No | Yes (future) | No |
| **Dependencies** | httpx | grpcio, protobuf | None |

### When to Use Each

- **HTTP Client**: Best for web applications, REST APIs, simple integrations
- **gRPC Client**: Best for microservices, high-performance RPC, future streaming support
- **FFI Client**: Best for CLI tools, embedded systems, maximum performance

## Examples

See the [examples/](examples/) directory for complete working examples:

- `datasource_http.py` - PostgreSQL operations via HTTP
- `datasource_grpc.py` - MySQL operations via gRPC
- `datasource_ffi.py` - MongoDB operations via FFI
- `llm_http.py` - OpenAI integration via HTTP
- `llm_grpc.py` - Claude integration via gRPC
- `llm_ffi.py` - Ollama integration via FFI

Run any example:

```bash
# HTTP examples (requires server on localhost:8080)
python examples/datasource_http.py
export OPENAI_API_KEY='sk-...'
python examples/llm_http.py

# gRPC examples (requires server on localhost:50051)
python examples/datasource_grpc.py
export CLAUDE_API_KEY='sk-...'
python examples/llm_grpc.py

# FFI examples (requires built library, no server)
python examples/datasource_ffi.py
python examples/llm_ffi.py
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=py_operrouter --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ examples/

# Type checking
mypy src/

# Linting
ruff check src/
```

### Building

```bash
# Build wheel
python -m build

# Install locally
pip install dist/py_operrouter-*.whl
```

## Troubleshooting

### Import Errors

```bash
# Make sure SDK is installed
pip install -e .

# Verify installation
python -c "from py_operrouter import HTTPClient; print('OK')"
```

### gRPC Proto Files Not Found

```bash
# Generate proto files
cd ../..
buf generate --path proto/operrouter.proto

# Verify proto files
ls sdks/py-operrouter/gen/proto/operrouter_pb2.py
```

### FFI Library Not Found

```bash
# Build FFI library
cd ../../bridges/operrouter-core-ffi
cargo build --release

# Or set library path
export OPERROUTER_FFI_PATH="/path/to/liboperrouter_core_ffi.so"

# Check library exists
ls ../../bridges/operrouter-core-ffi/target/release/liboperrouter_core_ffi.*
```

### Server Connection Errors

```bash
# Start HTTP server
cd ../../bridges/operrouter-core-http
cargo run --release  # Runs on :8080

# Start gRPC server
cd ../../bridges/operrouter-core-grpc
cargo run --release  # Runs on :50051
```

## Architecture

```
py-operrouter/
├── src/py_operrouter/
│   ├── __init__.py          # Main exports
│   ├── types.py             # Type definitions (10 dataclasses)
│   └── client/
│       ├── __init__.py      # Client exports
│       ├── http_client.py   # HTTP JSON-RPC client (310 lines)
│       ├── grpc_client.py   # gRPC Protobuf client (420 lines)
│       └── ffi_client.py    # FFI ctypes client (420 lines)
├── examples/
│   ├── README.md            # Examples documentation
│   ├── datasource_http.py   # HTTP DataSource demo
│   ├── datasource_grpc.py   # gRPC DataSource demo
│   ├── datasource_ffi.py    # FFI DataSource demo
│   ├── llm_http.py          # HTTP LLM demo
│   ├── llm_grpc.py          # gRPC LLM demo
│   └── llm_ffi.py           # FFI LLM demo
├── gen/proto/               # Generated protobuf files
├── pyproject.toml           # Modern Python packaging
└── README.md                # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure code passes `black`, `mypy`, and `ruff`
5. Submit a pull request

## License

See the main repository LICENSE file.

## Related Projects

- [js-operrouter](../js-operrouter/) - JavaScript/TypeScript SDK
- [go-operrouter](../go-operrouter/) - Go SDK
- [rust-operrouter](../rust-operrouter/) - Rust SDK
- [operrouter-core-http](../../bridges/operrouter-core-http/) - HTTP server
- [operrouter-core-grpc](../../bridges/operrouter-core-grpc/) - gRPC server
- [operrouter-core-ffi](../../bridges/operrouter-core-ffi/) - FFI library
