"""Type definitions for py-operrouter."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class PingResponse:
    """Response from ping operation."""
    success: bool
    message: str = ""


@dataclass
class ConfigResponse:
    """Response from config operations."""
    success: bool
    message: str = ""


@dataclass
class Metadata:
    """Operator metadata."""
    name: str
    version: str
    description: Optional[str] = None


@dataclass
class DataSourceConfig:
    """Configuration for DataSource connection."""
    driver: str  # postgres, mysql, redis, mongodb, kafka
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    # Additional driver-specific options as kwargs


@dataclass
class DataSourceResponse:
    """Response from DataSource operations."""
    success: bool
    message: str = ""


@dataclass
class DataSourceQueryResponse:
    """Response from DataSource query with rows."""
    success: bool
    rows: List[Dict[str, Any]]
    message: str = ""


@dataclass
class LLMConfig:
    """Configuration for LLM instance."""
    provider: str  # openai, ollama, anthropic, local
    model: str
    api_key: Optional[str] = None


@dataclass
class LLMResponse:
    """Response from LLM operations."""
    success: bool
    message: str = ""


@dataclass
class LLMGenerateResponse:
    """Response from LLM text generation."""
    success: bool
    text: str = ""
    message: str = ""


@dataclass
class ChatMessage:
    """Chat message for LLM chat interface."""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMChatResponse:
    """Response from LLM chat."""
    success: bool
    text: str = ""
    message: str = ""


@dataclass
class LLMEmbeddingResponse:
    """Response from LLM embedding generation."""
    success: bool
    embedding: List[float]
    message: str = ""


class OperRouterClient(Protocol):
    """Protocol defining the OperRouter client interface."""

    async def ping(self) -> PingResponse:
        """Test server connection."""
        ...

    async def validate_config(self, config: Dict[str, Any]) -> ConfigResponse:
        """Validate operator configuration."""
        ...

    async def load_config(self, path: str) -> ConfigResponse:
        """Load configuration from file."""
        ...

    async def get_metadata(self) -> Metadata:
        """Get server metadata."""
        ...

    # DataSource methods
    async def create_datasource(
        self, name: str, config: DataSourceConfig
    ) -> DataSourceResponse:
        """Create a new DataSource connection."""
        ...

    async def query_datasource(
        self, name: str, query: str
    ) -> DataSourceQueryResponse:
        """Execute a query on a DataSource."""
        ...

    async def execute_datasource(
        self, name: str, query: str
    ) -> DataSourceResponse:
        """Execute a write operation on a DataSource."""
        ...

    async def insert_datasource(
        self, name: str, data: Dict[str, Any]
    ) -> DataSourceResponse:
        """Insert data into a DataSource."""
        ...

    async def ping_datasource(self, name: str) -> DataSourceResponse:
        """Ping a DataSource to check health."""
        ...

    async def close_datasource(self, name: str) -> DataSourceResponse:
        """Close a DataSource connection."""
        ...

    # LLM methods
    async def create_llm(self, name: str, config: LLMConfig) -> LLMResponse:
        """Create a new LLM instance."""
        ...

    async def generate_llm(
        self, name: str, prompt: str
    ) -> LLMGenerateResponse:
        """Generate text from an LLM."""
        ...

    async def chat_llm(
        self, name: str, messages: List[ChatMessage]
    ) -> LLMChatResponse:
        """Chat with an LLM."""
        ...

    async def embedding_llm(
        self, name: str, text: str
    ) -> LLMEmbeddingResponse:
        """Generate embeddings from an LLM."""
        ...

    async def ping_llm(self, name: str) -> LLMResponse:
        """Ping an LLM instance to check health."""
        ...

    async def close_llm(self, name: str) -> LLMResponse:
        """Close an LLM instance."""
        ...
