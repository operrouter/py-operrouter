#!/usr/bin/env python3
"""Simple debug test"""

import ctypes
from pathlib import Path

class ProtoBuffer(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("len", ctypes.c_size_t),
    ]

lib_path = Path("/root/go/src/operrouter-core/bridges/operrouter-core-ffi/target/debug/liboperrouter_core_ffi.so")
lib = ctypes.CDLL(str(lib_path))

lib.ping_proto.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
lib.ping_proto.restype = ProtoBuffer

# Test with empty input (valid for PingRequest which is empty)
empty_array = (ctypes.c_uint8 * 1)()
ptr = ctypes.cast(empty_array, ctypes.POINTER(ctypes.c_uint8))

print(f"Calling ping_proto with ptr={ptr}, len=0")
result = lib.ping_proto(ptr, 0)

print(f"Result: data={result.data}, len={result.len}")
print(f"Data is null: {result.data is None or not result.data}")

if result.len > 0 and result.data:
    response_bytes = bytes(ctypes.cast(result.data, ctypes.POINTER(ctypes.c_uint8 * result.len)).contents)
    print(f"Response bytes ({len(response_bytes)}): {response_bytes.hex()}")
    lib.proto_buffer_free(result)
