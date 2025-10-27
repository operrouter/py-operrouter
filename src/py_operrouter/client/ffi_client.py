"""FFI Client for OperRouter calling Rust core directly."""

import ctypes
import json
import os
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


class FFIClient:
    """
    FFI client for OperRouter calling Rust core directly via C ABI.
    
    Requires:
        - liboperrouter_core_ffi.so/.dylib/.dll in library path
        - Or set OPERROUTER_FFI_PATH environment variable
    
    Example:
        >>> client = FFIClient()
        >>> resp = await client.ping()
        >>> print(resp.success)
        True
    """

    def __init__(self, ffi_path: Optional[str] = None):
        """
        Initialize FFI client.
        
        Args:
            ffi_path: Path to FFI library (optional, will search common locations)
        """
        self.lib = self._load_ffi_library(ffi_path)
        self._setup_function_signatures()

    def _load_ffi_library(self, path: Optional[str] = None) -> ctypes.CDLL:
        """Load the FFI library."""
        candidates = []
        
        if path:
            candidates.append(path)
        
        env_path = os.getenv("OPERROUTER_FFI_PATH")
        if env_path:
            candidates.append(env_path)
        
        # Common library names by platform
        lib_names = [
            "liboperrouter_core_ffi.so",      # Linux
            "liboperrouter_core_ffi.dylib",   # macOS
            "operrouter_core_ffi.dll",        # Windows
        ]
        candidates.extend(lib_names)
        
        # Also try in bridges directory
        script_dir = os.path.dirname(__file__)
        bridge_dir = os.path.join(script_dir, "../../../../bridges/operrouter-core-ffi/target/release")
        for name in lib_names:
            candidates.append(os.path.join(bridge_dir, name))
        
        for candidate in candidates:
            try:
                lib = ctypes.CDLL(candidate)
                return lib
            except OSError:
                continue
        
        raise RuntimeError(
            "Failed to load FFI library. Set OPERROUTER_FFI_PATH or build the library."
        )

    def _setup_function_signatures(self) -> None:
        """Setup ctypes function signatures."""
        # operrouter_version
        self.lib.operrouter_version.restype = ctypes.c_char_p
        self.lib.operrouter_version.argtypes = []
        
        # operrouter_ping
        self.lib.operrouter_ping.restype = ctypes.c_char_p
        self.lib.operrouter_ping.argtypes = []
        
        # operrouter_validate_config
        self.lib.operrouter_validate_config.restype = ctypes.c_char_p
        self.lib.operrouter_validate_config.argtypes = [ctypes.c_char_p]
        
        # operrouter_load_config
        self.lib.operrouter_load_config.restype = ctypes.c_char_p
        self.lib.operrouter_load_config.argtypes = [ctypes.c_char_p]
        
        # operrouter_get_metadata
        self.lib.operrouter_get_metadata.restype = ctypes.c_char_p
        self.lib.operrouter_get_metadata.argtypes = [ctypes.c_char_p]
        
        # DataSource functions
        self.lib.operrouter_datasource_create.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_create.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_datasource_query.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_query.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_datasource_execute.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_execute.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_datasource_insert.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_insert.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_datasource_ping.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_ping.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_datasource_close.restype = ctypes.c_char_p
        self.lib.operrouter_datasource_close.argtypes = [ctypes.c_char_p]
        
        # LLM functions
        self.lib.operrouter_llm_create.restype = ctypes.c_char_p
        self.lib.operrouter_llm_create.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_llm_generate.restype = ctypes.c_char_p
        self.lib.operrouter_llm_generate.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_llm_chat.restype = ctypes.c_char_p
        self.lib.operrouter_llm_chat.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_llm_embedding.restype = ctypes.c_char_p
        self.lib.operrouter_llm_embedding.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_llm_ping.restype = ctypes.c_char_p
        self.lib.operrouter_llm_ping.argtypes = [ctypes.c_char_p]
        
        self.lib.operrouter_llm_close.restype = ctypes.c_char_p
        self.lib.operrouter_llm_close.argtypes = [ctypes.c_char_p]
        
        # Free function for memory cleanup
        self.lib.operrouter_free_string.restype = None
        self.lib.operrouter_free_string.argtypes = [ctypes.c_char_p]

    def _call_ffi(self, func: Any, *args: Any) -> Dict[str, Any]:
        """Call FFI function and parse JSON response."""
        result_ptr = func(*args)
        if not result_ptr:
            return {"success": False, "error": "FFI call returned null"}
        
        try:
            result_str = ctypes.string_at(result_ptr).decode('utf-8')
            result = json.loads(result_str)
        finally:
            # Free the string allocated by Rust
            self.lib.operrouter_free_string(result_ptr)
        
        return result

    # ==================== Core Methods ====================

    async def ping(self) -> PingResponse:
        """Test server connection."""
        result = self._call_ffi(self.lib.operrouter_ping)
        return PingResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def validate_config(self, config: Dict[str, Any]) -> ConfigResponse:
        """Validate operator configuration."""
        config_json = json.dumps(config).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_validate_config,
            ctypes.c_char_p(config_json)
        )
        return ConfigResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def load_config(self, path: str) -> ConfigResponse:
        """Load configuration from file."""
        path_bytes = path.encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_load_config,
            ctypes.c_char_p(path_bytes)
        )
        return ConfigResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def get_metadata(self) -> Metadata:
        """Get server metadata."""
        config_json = json.dumps({}).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_get_metadata,
            ctypes.c_char_p(config_json)
        )
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
        request = {
            "name": name,
            "config": {
                "driver": config.driver,
                "host": config.host,
                "port": config.port,
                "database": config.database,
                "username": config.username,
                "password": config.password,
            }
        }
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_create,
            ctypes.c_char_p(request_json)
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def query_datasource(
        self, name: str, query: str
    ) -> DataSourceQueryResponse:
        """Execute a query on a DataSource."""
        request = {"name": name, "query": query}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_query,
            ctypes.c_char_p(request_json)
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
        request = {"name": name, "query": query}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_execute,
            ctypes.c_char_p(request_json)
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def insert_datasource(
        self, name: str, data: Dict[str, Any]
    ) -> DataSourceResponse:
        """Insert data into a DataSource."""
        request = {"name": name, "data": data}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_insert,
            ctypes.c_char_p(request_json)
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def ping_datasource(self, name: str) -> DataSourceResponse:
        """Ping a DataSource to check health."""
        request = {"name": name}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_ping,
            ctypes.c_char_p(request_json)
        )
        return DataSourceResponse(
            success=result.get("healthy", False) or result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def close_datasource(self, name: str) -> DataSourceResponse:
        """Close a DataSource connection."""
        request = {"name": name}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_datasource_close,
            ctypes.c_char_p(request_json)
        )
        return DataSourceResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    # ==================== LLM Methods ====================

    async def create_llm(self, name: str, config: LLMConfig) -> LLMResponse:
        """Create a new LLM instance."""
        request = {
            "name": name,
            "config": {
                "provider": config.provider,
                "model": config.model,
                "api_key": config.api_key,
            }
        }
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_create,
            ctypes.c_char_p(request_json)
        )
        return LLMResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def generate_llm(
        self, name: str, prompt: str
    ) -> LLMGenerateResponse:
        """Generate text from an LLM."""
        request = {"name": name, "prompt": prompt}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_generate,
            ctypes.c_char_p(request_json)
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
        request = {
            "name": name,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_chat,
            ctypes.c_char_p(request_json)
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
        request = {"name": name, "text": text}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_embedding,
            ctypes.c_char_p(request_json)
        )
        return LLMEmbeddingResponse(
            success=result.get("success", False),
            embedding=result.get("embedding", []),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def ping_llm(self, name: str) -> LLMResponse:
        """Ping an LLM instance to check health."""
        request = {"name": name}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_ping,
            ctypes.c_char_p(request_json)
        )
        return LLMResponse(
            success=result.get("healthy", False) or result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )

    async def close_llm(self, name: str) -> LLMResponse:
        """Close an LLM instance."""
        request = {"name": name}
        request_json = json.dumps(request).encode('utf-8')
        result = self._call_ffi(
            self.lib.operrouter_llm_close,
            ctypes.c_char_p(request_json)
        )
        return LLMResponse(
            success=result.get("success", False),
            message=result.get("error", "") or result.get("message", ""),
        )
