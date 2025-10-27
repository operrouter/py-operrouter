"""HTTP Client for OperRouter using JSON-RPC 2.0."""

import httpx
from typing import Any, Dict, List, Optional

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


class HTTPClient:
    """
    HTTP JSON-RPC client for OperRouter.
    
    Example:
        >>> client = HTTPClient("http://localhost:8080")
        >>> resp = await client.ping()
        >>> print(resp.success)
        True
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL of the OperRouter HTTP server
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._request_id = 0

    async def _call_rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a JSON-RPC 2.0 call.
        
        Args:
            method: RPC method name
            params: Method parameters
            
        Returns:
            Result from the RPC call
            
        Raises:
            httpx.HTTPError: On network errors
            ValueError: On RPC errors
        """
        self._request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._request_id,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/jsonrpc",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                error = data["error"]
                raise ValueError(f"RPC error: {error}")
            
            return data.get("result", {})

    # ==================== Core Methods ====================

    async def ping(self) -> PingResponse:
        """Test server connection."""
        result = await self._call_rpc("ping")
        return PingResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def validate_config(self, config: Dict[str, Any]) -> ConfigResponse:
        """Validate operator configuration."""
        result = await self._call_rpc("validate_config", {"config": config})
        return ConfigResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def load_config(self, path: str) -> ConfigResponse:
        """Load configuration from file."""
        result = await self._call_rpc("load_config", {"path": path})
        return ConfigResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def get_metadata(self) -> Metadata:
        """Get server metadata."""
        result = await self._call_rpc("get_metadata")
        metadata = result.get("metadata", {})
        return Metadata(
            name=metadata.get("name", ""),
            version=metadata.get("version", ""),
            description=metadata.get("description"),
        )

    # ==================== DataSource Methods ====================

    async def create_datasource(
        self, name: str, config: DataSourceConfig
    ) -> DataSourceResponse:
        """Create a new DataSource connection."""
        config_dict = {
            "driver": config.driver,
            "host": config.host,
            "port": config.port,
            "database": config.database,
        }
        if config.username:
            config_dict["username"] = config.username
        if config.password:
            config_dict["password"] = config.password
            
        result = await self._call_rpc(
            "datasource.create",
            {"name": name, "config": config_dict},
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def query_datasource(
        self, name: str, query: str
    ) -> DataSourceQueryResponse:
        """Execute a query on a DataSource."""
        result = await self._call_rpc(
            "datasource.query",
            {"name": name, "query": query},
        )
        return DataSourceQueryResponse(
            success=result.get("success", False),
            rows=result.get("rows", []),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def execute_datasource(
        self, name: str, query: str
    ) -> DataSourceResponse:
        """Execute a write operation on a DataSource."""
        result = await self._call_rpc(
            "datasource.execute",
            {"name": name, "query": query},
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def insert_datasource(
        self, name: str, data: Dict[str, Any]
    ) -> DataSourceResponse:
        """Insert data into a DataSource."""
        result = await self._call_rpc(
            "datasource.insert",
            {"name": name, "data": data},
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def ping_datasource(self, name: str) -> DataSourceResponse:
        """Ping a DataSource to check health."""
        result = await self._call_rpc("datasource.ping", {"name": name})
        return DataSourceResponse(
            success=result.get("healthy", False) or result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def close_datasource(self, name: str) -> DataSourceResponse:
        """Close a DataSource connection."""
        result = await self._call_rpc("datasource.close", {"name": name})
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    # ==================== LLM Methods ====================

    async def create_llm(self, name: str, config: LLMConfig) -> LLMResponse:
        """Create a new LLM instance."""
        config_dict = {
            "provider": config.provider,
            "model": config.model,
        }
        if config.api_key:
            config_dict["api_key"] = config.api_key
            
        result = await self._call_rpc(
            "llm.create",
            {"name": name, "config": config_dict},
        )
        return LLMResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def generate_llm(
        self, name: str, prompt: str
    ) -> LLMGenerateResponse:
        """Generate text from an LLM."""
        result = await self._call_rpc(
            "llm.generate",
            {"name": name, "prompt": prompt},
        )
        return LLMGenerateResponse(
            success=result.get("success", False),
            text=result.get("text", ""),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def chat_llm(
        self, name: str, messages: List[ChatMessage]
    ) -> LLMChatResponse:
        """Chat with an LLM."""
        messages_dict = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]
        result = await self._call_rpc(
            "llm.chat",
            {"name": name, "messages": messages_dict},
        )
        return LLMChatResponse(
            success=result.get("success", False),
            text=result.get("text", ""),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def embedding_llm(
        self, name: str, text: str
    ) -> LLMEmbeddingResponse:
        """Generate embeddings from an LLM."""
        result = await self._call_rpc(
            "llm.embedding",
            {"name": name, "text": text},
        )
        return LLMEmbeddingResponse(
            success=result.get("success", False),
            embedding=result.get("embedding", []),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def ping_llm(self, name: str) -> LLMResponse:
        """Ping an LLM instance to check health."""
        result = await self._call_rpc("llm.ping", {"name": name})
        return LLMResponse(
            success=result.get("healthy", False) or result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def close_llm(self, name: str) -> LLMResponse:
        """Close an LLM instance."""
        result = await self._call_rpc("llm.close", {"name": name})
        return LLMResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )
