#!/usr/bin/env python3
"""
Python FFI Integration Test with Protobuf
Demonstrates calling operrouter-core-ffi using ctypes and generated protobuf types.
"""

import ctypes
import os
import sys
from pathlib import Path

# Add the generated proto directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "gen"))

from proto import operrouter_pb2


class ProtoBuffer(ctypes.Structure):
    """Matches the C ProtoBuffer struct"""
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("len", ctypes.c_size_t),
    ]


class OperRouterFFI:
    """Python wrapper for operrouter-core-ffi with protobuf support"""
    
    def __init__(self, lib_path: str):
        """Load the FFI library"""
        self.lib = ctypes.CDLL(lib_path)
        
        # Define function signatures
        # ping_proto(input_ptr, input_len) -> ProtoBuffer
        self.lib.ping_proto.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.ping_proto.restype = ProtoBuffer
        
        # validate_config_proto(input_ptr, input_len) -> ProtoBuffer
        self.lib.validate_config_proto.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.validate_config_proto.restype = ProtoBuffer
        
        # get_metadata_proto(input_ptr, input_len) -> ProtoBuffer
        self.lib.get_metadata_proto.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.get_metadata_proto.restype = ProtoBuffer
        
        # load_config_proto(input_ptr, input_len) -> ProtoBuffer
        self.lib.load_config_proto.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.load_config_proto.restype = ProtoBuffer
        
        # proto_buffer_free(buf)
        self.lib.proto_buffer_free.argtypes = [ProtoBuffer]
        self.lib.proto_buffer_free.restype = None
    
    def _call_proto_func(self, func, request_bytes: bytes):
        """Helper to call a protobuf FFI function and handle memory"""
        # Always create a buffer, even for empty messages
        # Python ctypes doesn't handle NULL pointers well, so use empty array
        if len(request_bytes) == 0:
            # Create a single-byte dummy array for empty messages
            input_array = (ctypes.c_uint8 * 1)()
            input_ptr = ctypes.cast(input_array, ctypes.POINTER(ctypes.c_uint8))
            input_len = 0  # Still pass 0 length
        else:
            input_array = (ctypes.c_uint8 * len(request_bytes)).from_buffer_copy(request_bytes)
            input_ptr = ctypes.cast(input_array, ctypes.POINTER(ctypes.c_uint8))
            input_len = len(request_bytes)
        
        # Call FFI function
        result_buf = func(input_ptr, input_len)
        
        if result_buf.data is None:
            raise RuntimeError("FFI function returned null data pointer")
        
        if result_buf.len == 0:
            raise RuntimeError("FFI function returned zero length")
        
        # Copy response bytes
        response_bytes = bytes(ctypes.cast(result_buf.data, ctypes.POINTER(ctypes.c_uint8 * result_buf.len)).contents)
        
        # Free the buffer
        self.lib.proto_buffer_free(result_buf)
        
        return response_bytes
    
    def ping(self) -> operrouter_pb2.PingResponse:
        """Call ping_proto and return response"""
        request = operrouter_pb2.PingRequest()
        request_bytes = request.SerializeToString()
        
        response_bytes = self._call_proto_func(self.lib.ping_proto, request_bytes)
        
        response = operrouter_pb2.PingResponse()
        response.ParseFromString(response_bytes)
        return response
    
    def validate_config(self, toml_content: str) -> operrouter_pb2.ValidateConfigResponse:
        """Call validate_config_proto and return response"""
        request = operrouter_pb2.ValidateConfigRequest()
        request.toml_content = toml_content
        request_bytes = request.SerializeToString()
        
        response_bytes = self._call_proto_func(self.lib.validate_config_proto, request_bytes)
        
        response = operrouter_pb2.ValidateConfigResponse()
        response.ParseFromString(response_bytes)
        return response
    
    def get_metadata(self) -> operrouter_pb2.GetMetadataResponse:
        """Call get_metadata_proto and return response"""
        request = operrouter_pb2.GetMetadataRequest()
        request_bytes = request.SerializeToString()
        
        response_bytes = self._call_proto_func(self.lib.get_metadata_proto, request_bytes)
        
        response = operrouter_pb2.GetMetadataResponse()
        response.ParseFromString(response_bytes)
        return response
    
    def load_config(self, config_path: str) -> operrouter_pb2.LoadConfigResponse:
        """Call load_config_proto and return response"""
        request = operrouter_pb2.LoadConfigRequest()
        request.config_path = config_path
        request_bytes = request.SerializeToString()
        
        response_bytes = self._call_proto_func(self.lib.load_config_proto, request_bytes)
        
        response = operrouter_pb2.LoadConfigResponse()
        response.ParseFromString(response_bytes)
        return response


def main():
    """Run integration tests"""
    # Find the FFI library (try release first, then debug)
    base_path = Path(__file__).parent.parent.parent.parent / "bridges" / "operrouter-core-ffi" / "target"
    lib_path = base_path / "release" / "liboperrouter_core_ffi.so"
    
    if not lib_path.exists():
        lib_path = base_path / "debug" / "liboperrouter_core_ffi.so"
    
    if not lib_path.exists():
        print(f"❌ FFI library not found at: {lib_path}")
        print("   Please build it first: cd bridges/operrouter-core-ffi && cargo build --release")
        return 1
    
    print(f"🔧 Loading FFI library: {lib_path}")
    ffi = OperRouterFFI(str(lib_path))
    
    # Test 1: Ping
    print("\n📡 Test 1: Ping")
    try:
        response = ffi.ping()
        print(f"   Status: {response.status}")
        print(f"   Version: {response.version}")
        assert response.status == "ok"
        print("   ✅ PASS")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1
    
    # Test 2: Get Metadata
    print("\n📋 Test 2: Get Metadata")
    try:
        response = ffi.get_metadata()
        print(f"   Name: {response.metadata.name}")
        print(f"   Version: {response.metadata.version}")
        print(f"   Description: {response.metadata.description}")
        assert response.metadata.name == "operrouter-core"
        print("   ✅ PASS")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1
    
    # Test 3: Validate Valid Config
    print("\n✅ Test 3: Validate Valid Config")
    valid_toml = """
[metadata]
name = "python-test-operator"
version = "1.0.0"
description = "Test from Python"

[dependencies]

[inject]
"""
    try:
        response = ffi.validate_config(valid_toml)
        print(f"   Valid: {response.valid}")
        print(f"   Errors: {list(response.errors) if response.errors else 'None'}")
        assert response.valid == True
        assert len(response.errors) == 0
        print("   ✅ PASS")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1
    
    # Test 4: Validate Invalid Config
    print("\n❌ Test 4: Validate Invalid Config")
    invalid_toml = "invalid toml [[["
    try:
        response = ffi.validate_config(invalid_toml)
        print(f"   Valid: {response.valid}")
        print(f"   Errors: {list(response.errors)}")
        assert response.valid == False
        assert len(response.errors) > 0
        print("   ✅ PASS")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return 1
    
    # Test 5: Load Config from File
    print("\n📂 Test 5: Load Config from File")
    config_path = Path(__file__).parent.parent.parent.parent / "core" / "operrouter-core-sdk" / "examples" / "demo-operator" / "operator.toml"
    
    if config_path.exists():
        try:
            response = ffi.load_config(str(config_path))
            print(f"   Success: {response.success}")
            print(f"   Operator Name: {response.operator_name}")
            if response.error:
                print(f"   Error: {response.error}")
            assert response.success == True
            print("   ✅ PASS")
        except Exception as e:
            print(f"   ❌ FAIL: {e}")
            return 1
    else:
        print(f"   ⚠️  SKIP: Config file not found at {config_path}")
    
    print("\n" + "="*60)
    print("🎉 All Python FFI + Protobuf tests passed!")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
