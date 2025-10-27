# Python SDK Examples

This directory contains complete examples for using the OperRouter Python SDK with all three transport layers.

## Prerequisites

```bash
# Install the SDK
cd /root/go/src/operrouter-core/sdks/py-operrouter
pip install -e .

# For FFI examples, build the Rust FFI library
cd ../../bridges/operrouter-core-ffi
cargo build --release
```

## Examples

### HTTP Client Examples

**DataSource Example** - `datasource_http.py`
- Demonstrates PostgreSQL operations over HTTP JSON-RPC
- Creates datasource, queries, inserts, and manages connections
- Uses `HTTPClient` with async/await

```bash
# Make sure HTTP server is running on localhost:8080
python examples/datasource_http.py
```

**LLM Example** - `llm_http.py`
- Demonstrates OpenAI integration over HTTP JSON-RPC
- Text generation, chat, and embeddings
- Requires `OPENAI_API_KEY` environment variable

```bash
export OPENAI_API_KEY='sk-...'
python examples/llm_http.py
```

### gRPC Client Examples

**DataSource Example** - `datasource_grpc.py`
- Demonstrates MySQL operations over gRPC
- High-performance binary protocol with protobuf
- Uses `GRPCClient` with async channel management

```bash
# Make sure gRPC server is running on localhost:50051
python examples/datasource_grpc.py
```

**LLM Example** - `llm_grpc.py`
- Demonstrates Claude integration over gRPC
- Streaming-capable protocol for LLM responses
- Requires `CLAUDE_API_KEY` environment variable

```bash
export CLAUDE_API_KEY='sk-...'
python examples/llm_grpc.py
```

### FFI Client Examples

**DataSource Example** - `datasource_ffi.py`
- Demonstrates MongoDB operations via direct Rust calls
- Zero-copy performance, no network overhead
- Uses `FFIClient` with ctypes

```bash
# FFI client calls Rust library directly - no server needed
python examples/datasource_ffi.py
```

**LLM Example** - `llm_ffi.py`
- Demonstrates Ollama (local) integration via FFI
- Maximum performance for local LLM inference
- No API key needed for local Ollama

```bash
# Make sure Ollama is running
ollama serve
python examples/llm_ffi.py
```

## Transport Comparison

| Feature | HTTP | gRPC | FFI |
|---------|------|------|-----|
| **Protocol** | JSON-RPC 2.0 | Protobuf | Direct Rust calls |
| **Performance** | Good | Better | Best |
| **Network** | Required | Required | Not needed |
| **Setup** | Easiest | Moderate | Complex |
| **Use Case** | Web services | Microservices | Embedded/CLI |
| **Streaming** | No | Yes | No |

## Common Patterns

### Error Handling

```python
try:
    response = await client.query_datasource("db", "SELECT * FROM users")
    if response.success:
        print(f"Found {len(response.rows)} rows")
    else:
        print(f"Query failed: {response.message}")
except Exception as e:
    print(f"Error: {e}")
```

### Resource Cleanup

```python
# HTTP client - no cleanup needed
client = HTTPClient("http://localhost:8080")
await client.ping()

# gRPC client - always close channel
client = GRPCClient("localhost:50051")
try:
    await client.ping()
finally:
    await client.close()

# FFI client - no cleanup needed
client = FFIClient()
await client.ping()
```

### Configuration

```python
# DataSource configuration
from py_operrouter import DataSourceConfig

config = DataSourceConfig(
    driver="postgres",  # postgres, mysql, mongodb, redis, kafka
    host="localhost",
    port=5432,
    database="mydb",
    username="user",
    password="pass",
)

# LLM configuration
from py_operrouter import LLMConfig

config = LLMConfig(
    provider="openai",  # openai, claude, ollama
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

## All Available Methods

### Core Methods (4)
- `ping()` - Test connection
- `validate_config(config_str)` - Validate TOML config
- `load_config(config_str)` - Load operator config
- `get_metadata(name)` - Get operator metadata

### DataSource Methods (6)
- `create_datasource(name, config)` - Create datasource
- `query_datasource(name, query)` - Execute SELECT query
- `execute_datasource(name, statement)` - Execute DDL/DML
- `insert_datasource(name, data)` - Insert row
- `ping_datasource(name)` - Check health
- `close_datasource(name)` - Close connection

### LLM Methods (6)
- `create_llm(name, config)` - Create LLM instance
- `generate_llm(name, prompt)` - Generate completion
- `chat_llm(name, messages)` - Chat conversation
- `embedding_llm(name, text)` - Get embeddings
- `ping_llm(name)` - Check health
- `close_llm(name)` - Close instance

## Troubleshooting

### Import Errors
```bash
# Make sure SDK is installed
pip install -e .

# Verify installation
python -c "from py_operrouter import HTTPClient; print('OK')"
```

### gRPC Proto Errors
```bash
# Make sure proto files are generated
cd ../../
buf generate --path proto/operrouter.proto

# Check proto files exist
ls sdks/py-operrouter/gen/proto/operrouter_pb2.py
```

### FFI Library Not Found
```bash
# Build the FFI library
cd ../../bridges/operrouter-core-ffi
cargo build --release

# Set library path (optional)
export OPERROUTER_FFI_PATH="/path/to/liboperrouter_core_ffi.so"
```

### Server Not Running
```bash
# HTTP server
cd ../../bridges/operrouter-core-http
cargo run --release

# gRPC server
cd ../../bridges/operrouter-core-grpc
cargo run --release
```

## Next Steps

1. Read the [main README](../README.md) for installation guide
2. Check the [type definitions](../src/py_operrouter/types.py) for API reference
3. Explore the [client implementations](../src/py_operrouter/client/) for details
4. Run the examples to verify your setup works

## Contributing

Found a bug or have an improvement? Please open an issue or submit a PR!
