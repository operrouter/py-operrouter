"""Python SDK for OperRouter - Unified DataSource and LLM operations."""

__version__ = "0.1.0"

# Export client classes
from py_operrouter.client import HTTPClient, GRPCClient, FFIClient

# Export type definitions
from py_operrouter.types import (
    # Configuration types
    DataSourceConfig,
    LLMConfig,
    ChatMessage,
    # Response types
    PingResponse,
    ConfigResponse,
    Metadata,
    DataSourceResponse,
    DataSourceQueryResponse,
    LLMResponse,
    LLMGenerateResponse,
    LLMChatResponse,
    LLMEmbeddingResponse,
    # Protocol
    OperRouterClient,
)

__all__ = [
    "__version__",
    "HTTPClient",
    "GRPCClient",
    "FFIClient",
    "DataSourceConfig",
    "LLMConfig",
    "ChatMessage",
    "PingResponse",
    "ConfigResponse",
    "Metadata",
    "DataSourceResponse",
    "DataSourceQueryResponse",
    "LLMResponse",
    "LLMGenerateResponse",
    "LLMChatResponse",
    "LLMEmbeddingResponse",
    "OperRouterClient",
]
