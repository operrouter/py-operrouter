"""gRPC Client for OperRouter."""

import grpc
from typing import Any, Dict, List

from py_operrouter.types import (
    ChatMessage,
    ConfigResponse,
    DataSourceConfig,
    DataSourceQueryResponse,
    DataSourceResponse,
    LLMChatResponse,
    LLMConfig,
    LLMEmbeddingResponse,
    LLMGenerateResponse,
    LLMResponse,
    Metadata,
    PingResponse,
)

# Import generated protobuf files
# Add proto directory to path for imports
import os
import sys

# Try to find and add the proto directory to sys.path
_proto_dir = None
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up to package root and look for gen/proto
for _ in range(3):
    _current_dir = os.path.dirname(_current_dir)
    _candidate = os.path.join(_current_dir, "gen", "proto")
    if os.path.exists(_candidate):
        _proto_dir = _candidate
        break

if _proto_dir and _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

try:
    import operrouter_pb2
    import operrouter_pb2_grpc
except ImportError as e:
    # Proto files not available, GRPCClient will fail at instantiation
    operrouter_pb2 = None
    operrouter_pb2_grpc = None


class GRPCClient:
    """
    gRPC client for OperRouter.
    
    Example:
        >>> client = GRPCClient("localhost:50051")
        >>> resp = await client.ping()
        >>> print(resp.success)
        True
    """

    def __init__(self, address: str, insecure: bool = True):
        """
        Initialize gRPC client.
        
        Args:
            address: gRPC server address (host:port)
            insecure: Use insecure channel (default: True)
        """
        self.address = address
        
        if insecure:
            self.channel = grpc.aio.insecure_channel(address)
        else:
            # For TLS, you would use:
            # credentials = grpc.ssl_channel_credentials()
            # self.channel = grpc.aio.secure_channel(address, credentials)
            raise NotImplementedError("Secure channels not yet implemented")
        
        self.stub = operrouter_pb2_grpc.OperRouterStub(self.channel)

    async def close(self) -> None:
        """Close the gRPC channel."""
        await self.channel.close()

    # ==================== Core Methods ====================

    async def ping(self) -> PingResponse:
        """Test server connection."""
        request = operrouter_pb2.PingRequest()
        response = await self.stub.Ping(request)
        return PingResponse(
            success=response.success,
            message=response.error or "",
        )

    async def validate_config(self, config: Dict[str, Any]) -> ConfigResponse:
        """Validate operator configuration."""
        import json
        request = operrouter_pb2.ValidateConfigRequest(
            config=json.dumps(config)
        )
        response = await self.stub.ValidateConfig(request)
        return ConfigResponse(
            success=response.success,
            message=response.error or "",
        )

    async def load_config(self, path: str) -> ConfigResponse:
        """Load configuration from file."""
        request = operrouter_pb2.LoadConfigRequest(path=path)
        response = await self.stub.LoadConfig(request)
        return ConfigResponse(
            success=response.success,
            message=response.error or "",
        )

    async def get_metadata(self) -> Metadata:
        """Get server metadata."""
        request = operrouter_pb2.GetMetadataRequest()
        response = await self.stub.GetMetadata(request)
        return Metadata(
            name=response.metadata.name if response.metadata else "",
            version=response.metadata.version if response.metadata else "",
            description=response.metadata.description if response.metadata else None,
        )

    # ==================== DataSource Methods ====================

    def _datasource_type_to_enum(self, driver: str) -> int:
        """Convert driver string to proto enum."""
        mapping = {
            "postgres": 1,  # DATASOURCE_TYPE_POSTGRES
            "mysql": 2,     # DATASOURCE_TYPE_MYSQL
            "redis": 3,     # DATASOURCE_TYPE_REDIS
            "mongodb": 4,   # DATASOURCE_TYPE_MONGODB
            "kafka": 5,     # DATASOURCE_TYPE_KAFKA
        }
        return mapping.get(driver.lower(), 0)

    def _build_datasource_url(self, config: DataSourceConfig) -> str:
        """Build connection URL from config."""
        if config.driver == "postgres":
            return f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        elif config.driver == "mysql":
            return f"mysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        else:
            return f"{config.driver}://{config.host}:{config.port}"

    async def create_datasource(
        self, name: str, config: DataSourceConfig
    ) -> DataSourceResponse:
        """Create a new DataSource connection."""
        ds_config = operrouter_pb2.DataSourceConfig(
            type=self._datasource_type_to_enum(config.driver),
            url=self._build_datasource_url(config),
        )
        request = operrouter_pb2.CreateDataSourceRequest(
            name=name,
            config=ds_config,
        )
        response = await self.stub.CreateDataSource(request)
        return DataSourceResponse(
            success=response.success,
            message=response.error or "",
        )

    async def query_datasource(
        self, name: str, query: str
    ) -> DataSourceQueryResponse:
        """Execute a query on a DataSource."""
        request = operrouter_pb2.QueryDataSourceRequest(
            name=name,
            query=query,
        )
        response = await self.stub.QueryDataSource(request)
        
        # Convert proto rows to dicts
        rows = []
        for row in response.rows:
            row_dict = {}
            for key, value in row.columns.items():
                row_dict[key] = self._proto_value_to_python(value)
            rows.append(row_dict)
        
        return DataSourceQueryResponse(
            success=response.success,
            rows=rows,
            message=response.error or "",
        )

    def _proto_value_to_python(self, value: Any) -> Any:
        """Convert proto Value to Python value."""
        if not value or not hasattr(value, 'value'):
            return None
        
        which = value.WhichOneof('value')
        if which == 'null_value':
            return None
        elif which == 'bool_value':
            return value.bool_value
        elif which == 'int_value':
            return int(value.int_value)
        elif which == 'float_value':
            return value.float_value
        elif which == 'string_value':
            return value.string_value
        elif which == 'bytes_value':
            return value.bytes_value
        return None

    def _python_value_to_proto(self, val: Any) -> Any:
        """Convert Python value to proto Value."""
        value = operrouter_pb2.Value()
        if val is None:
            value.null_value = 0
        elif isinstance(val, bool):
            value.bool_value = val
        elif isinstance(val, int):
            value.int_value = val
        elif isinstance(val, float):
            value.float_value = val
        elif isinstance(val, str):
            value.string_value = val
        elif isinstance(val, bytes):
            value.bytes_value = val
        else:
            value.string_value = str(val)
        return value

    async def execute_datasource(
        self, name: str, query: str
    ) -> DataSourceResponse:
        """Execute a write operation on a DataSource."""
        request = operrouter_pb2.ExecuteDataSourceRequest(
            name=name,
            query=query,
        )
        response = await self.stub.ExecuteDataSource(request)
        return DataSourceResponse(
            success=response.success,
            message=response.error or "",
        )

    async def insert_datasource(
        self, name: str, data: Dict[str, Any]
    ) -> DataSourceResponse:
        """Insert data into a DataSource."""
        row = operrouter_pb2.Row()
        for key, val in data.items():
            row.columns[key].CopyFrom(self._python_value_to_proto(val))
        
        request = operrouter_pb2.InsertDataSourceRequest(
            name=name,
            data=row,
        )
        response = await self.stub.InsertDataSource(request)
        return DataSourceResponse(
            success=response.success,
            message=response.error or "",
        )

    async def ping_datasource(self, name: str) -> DataSourceResponse:
        """Ping a DataSource to check health."""
        request = operrouter_pb2.PingDataSourceRequest(name=name)
        response = await self.stub.PingDataSource(request)
        return DataSourceResponse(
            success=response.healthy,
            message=response.error or "",
        )

    async def close_datasource(self, name: str) -> DataSourceResponse:
        """Close a DataSource connection."""
        request = operrouter_pb2.CloseDataSourceRequest(name=name)
        response = await self.stub.CloseDataSource(request)
        return DataSourceResponse(
            success=response.success,
            message=response.error or "",
        )

    # ==================== LLM Methods ====================

    def _llm_provider_to_enum(self, provider: str) -> int:
        """Convert provider string to proto enum."""
        mapping = {
            "openai": 1,      # LLM_PROVIDER_OPENAI
            "ollama": 2,      # LLM_PROVIDER_OLLAMA
            "anthropic": 3,   # LLM_PROVIDER_ANTHROPIC
            "local": 4,       # LLM_PROVIDER_LOCAL
        }
        return mapping.get(provider.lower(), 0)

    def _message_role_to_enum(self, role: str) -> int:
        """Convert message role to proto enum."""
        mapping = {
            "system": 1,      # MESSAGE_ROLE_SYSTEM
            "user": 2,        # MESSAGE_ROLE_USER
            "assistant": 3,   # MESSAGE_ROLE_ASSISTANT
        }
        return mapping.get(role.lower(), 0)

    async def create_llm(self, name: str, config: LLMConfig) -> LLMResponse:
        """Create a new LLM instance."""
        llm_config = operrouter_pb2.LLMConfig(
            provider=self._llm_provider_to_enum(config.provider),
            model=config.model,
            api_key=config.api_key or "",
        )
        request = operrouter_pb2.CreateLLMRequest(
            name=name,
            config=llm_config,
        )
        response = await self.stub.CreateLLM(request)
        return LLMResponse(
            success=response.success,
            message=response.error or "",
        )

    async def generate_llm(
        self, name: str, prompt: str
    ) -> LLMGenerateResponse:
        """Generate text from an LLM."""
        request = operrouter_pb2.GenerateLLMRequest(
            name=name,
            prompt=prompt,
        )
        response = await self.stub.GenerateLLM(request)
        return LLMGenerateResponse(
            success=response.success,
            text=response.text,
            message=response.error or "",
        )

    async def chat_llm(
        self, name: str, messages: List[ChatMessage]
    ) -> LLMChatResponse:
        """Chat with an LLM."""
        proto_messages = [
            operrouter_pb2.Message(
                role=self._message_role_to_enum(msg.role),
                content=msg.content,
            )
            for msg in messages
        ]
        request = operrouter_pb2.ChatLLMRequest(
            name=name,
            messages=proto_messages,
        )
        response = await self.stub.ChatLLM(request)
        return LLMChatResponse(
            success=response.success,
            text=response.text,
            message=response.error or "",
        )

    async def embedding_llm(
        self, name: str, text: str
    ) -> LLMEmbeddingResponse:
        """Generate embeddings from an LLM."""
        request = operrouter_pb2.EmbeddingLLMRequest(
            name=name,
            text=text,
        )
        response = await self.stub.EmbeddingLLM(request)
        return LLMEmbeddingResponse(
            success=response.success,
            embedding=list(response.embedding),
            message=response.error or "",
        )

    async def ping_llm(self, name: str) -> LLMResponse:
        """Ping an LLM instance to check health."""
        request = operrouter_pb2.PingLLMRequest(name=name)
        response = await self.stub.PingLLM(request)
        return LLMResponse(
            success=response.healthy,
            message=response.error or "",
        )

    async def close_llm(self, name: str) -> LLMResponse:
        """Close an LLM instance."""
        request = operrouter_pb2.CloseLLMRequest(name=name)
        response = await self.stub.CloseLLM(request)
        return LLMResponse(
            success=response.success,
            message=response.error or "",
        )
