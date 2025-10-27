# Python SDK Quick Start Guide

## Installation

```bash
cd sdks/py-operrouter
pip install -e .
```

## Verify Installation

```bash
python3 -c "from py_operrouter import HTTPClient, GRPCClient, FFIClient; print('✅ Installation successful!')"
```

## 30-Second Examples

### 1. HTTP Client (Web Services)

```python
import asyncio
from py_operrouter import HTTPClient, DataSourceConfig

async def main():
    client = HTTPClient("http://localhost:8080")
    
    # Test connection
    ping = await client.ping()
    print(f"Server alive: {ping.success}")
    
    # Create PostgreSQL datasource
    config = DataSourceConfig(
        driver="postgres",
        host="localhost",
        port=5432,
        database="mydb",
        username="user",
        password="pass"
    )
    
    await client.create_datasource("db", config)
    
    # Query data
    result = await client.query_datasource("db", "SELECT * FROM users")
    print(f"Found {len(result.rows)} rows")

asyncio.run(main())
```

### 2. gRPC Client (Microservices)

```python
import asyncio
from py_operrouter import GRPCClient, LLMConfig, ChatMessage

async def main():
    client = GRPCClient("localhost:50051")
    
    try:
        # Create OpenAI LLM
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="sk-..."
        )
        
        await client.create_llm("ai", config)
        
        # Chat
        messages = [
            ChatMessage(role="user", content="Hello!")
        ]
        
        response = await client.chat_llm("ai", messages)
        print(f"AI: {response.text}")
    
    finally:
        await client.close()

asyncio.run(main())
```

### 3. FFI Client (Maximum Performance)

```python
import asyncio
from py_operrouter import FFIClient, DataSourceConfig

async def main():
    # Direct Rust calls - no network overhead
    client = FFIClient()
    
    # Test FFI
    ping = await client.ping()
    print(f"FFI alive: {ping.success}")
    
    # Create MongoDB datasource
    config = DataSourceConfig(
        driver="mongodb",
        host="localhost",
        port=27017,
        database="testdb"
    )
    
    await client.create_datasource("mongo", config)
    
    # Query MongoDB
    result = await client.query_datasource(
        "mongo",
        '{"find": "users", "limit": 10}'
    )
    
    print(f"Found {len(result.rows)} documents")

asyncio.run(main())
```

## All Available Methods

### Core (4 methods)
- `ping()` - Test connection
- `validate_config(config_str)` - Validate TOML
- `load_config(config_str)` - Load config
- `get_metadata(name)` - Get metadata

### DataSource (6 methods)
- `create_datasource(name, config)` - Create datasource
- `query_datasource(name, query)` - SELECT query
- `execute_datasource(name, statement)` - DDL/DML
- `insert_datasource(name, data)` - Insert row
- `ping_datasource(name)` - Health check
- `close_datasource(name)` - Close connection

### LLM (6 methods)
- `create_llm(name, config)` - Create LLM
- `generate_llm(name, prompt)` - Generate text
- `chat_llm(name, messages)` - Chat conversation
- `embedding_llm(name, text)` - Get embeddings
- `ping_llm(name)` - Health check
- `close_llm(name)` - Close instance

## Run Examples

```bash
# HTTP examples
python examples/datasource_http.py
export OPENAI_API_KEY='sk-...' && python examples/llm_http.py

# gRPC examples
python examples/datasource_grpc.py
export CLAUDE_API_KEY='sk-...' && python examples/llm_grpc.py

# FFI examples (requires built library)
python examples/datasource_ffi.py
python examples/llm_ffi.py
```

## Choose Your Client

| Use Case | Client | Why |
|----------|--------|-----|
| Web apps | HTTPClient | Easy REST-like integration |
| Microservices | GRPCClient | High performance RPC |
| CLI tools | FFIClient | Zero network overhead |
| Embedded | FFIClient | Maximum performance |

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Explore [examples/](examples/) for complete demos
3. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details

## Troubleshooting

### Import errors?
```bash
pip install -e .
```

### Proto files missing?
```bash
cd ../.. && buf generate --path proto/operrouter.proto
```

### FFI library not found?
```bash
cd ../../bridges/operrouter-core-ffi && cargo build --release
```

### Server not running?
```bash
# HTTP: cargo run --release (in bridges/operrouter-core-http)
# gRPC: cargo run --release (in bridges/operrouter-core-grpc)
```

---

**That's it!** You now have a fully functional Python SDK with 3 transport options. 🎉
