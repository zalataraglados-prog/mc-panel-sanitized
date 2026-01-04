from __future__ import annotations

import gzip
import io
import struct
from typing import Any, Dict


TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


def read_nbt(path: str) -> Dict[str, Any]:
    with gzip.open(path, "rb") as handle:
        data = handle.read()
    buffer = io.BytesIO(data)
    tag_type = _read_byte(buffer)
    if tag_type == TAG_END:
        raise ValueError("Invalid NBT root")
    name = _read_string(buffer)
    value = _read_payload(buffer, tag_type)
    return {"name": name, "type": tag_type, "value": value}


def write_nbt(path: str, root: Dict[str, Any]) -> None:
    buffer = io.BytesIO()
    _write_byte(buffer, root["type"])
    _write_string(buffer, root["name"])
    _write_payload(buffer, root["type"], root["value"])
    payload = buffer.getvalue()
    with gzip.open(path, "wb") as handle:
        handle.write(payload)


def _read_payload(buffer: io.BytesIO, tag_type: int) -> Any:
    if tag_type == TAG_BYTE:
        return _read_byte(buffer, signed=True)
    if tag_type == TAG_SHORT:
        return _read_short(buffer)
    if tag_type == TAG_INT:
        return _read_int(buffer)
    if tag_type == TAG_LONG:
        return _read_long(buffer)
    if tag_type == TAG_FLOAT:
        return _read_float(buffer)
    if tag_type == TAG_DOUBLE:
        return _read_double(buffer)
    if tag_type == TAG_BYTE_ARRAY:
        length = _read_int(buffer)
        return buffer.read(length)
    if tag_type == TAG_STRING:
        return _read_string(buffer)
    if tag_type == TAG_LIST:
        item_type = _read_byte(buffer)
        length = _read_int(buffer)
        items = [_read_payload(buffer, item_type) for _ in range(length)]
        return {"item_type": item_type, "items": items}
    if tag_type == TAG_COMPOUND:
        result: Dict[str, Dict[str, Any]] = {}
        while True:
            inner_type = _read_byte(buffer)
            if inner_type == TAG_END:
                break
            name = _read_string(buffer)
            value = _read_payload(buffer, inner_type)
            result[name] = {"type": inner_type, "value": value}
        return result
    if tag_type == TAG_INT_ARRAY:
        length = _read_int(buffer)
        return [_read_int(buffer) for _ in range(length)]
    if tag_type == TAG_LONG_ARRAY:
        length = _read_int(buffer)
        return [_read_long(buffer) for _ in range(length)]
    raise ValueError(f"Unsupported tag type {tag_type}")


def _write_payload(buffer: io.BytesIO, tag_type: int, value: Any) -> None:
    if tag_type == TAG_BYTE:
        _write_byte(buffer, value, signed=True)
        return
    if tag_type == TAG_SHORT:
        _write_short(buffer, value)
        return
    if tag_type == TAG_INT:
        _write_int(buffer, value)
        return
    if tag_type == TAG_LONG:
        _write_long(buffer, value)
        return
    if tag_type == TAG_FLOAT:
        _write_float(buffer, value)
        return
    if tag_type == TAG_DOUBLE:
        _write_double(buffer, value)
        return
    if tag_type == TAG_BYTE_ARRAY:
        data = bytes(value)
        _write_int(buffer, len(data))
        buffer.write(data)
        return
    if tag_type == TAG_STRING:
        _write_string(buffer, value)
        return
    if tag_type == TAG_LIST:
        item_type = value["item_type"]
        items = value["items"]
        _write_byte(buffer, item_type)
        _write_int(buffer, len(items))
        for item in items:
            _write_payload(buffer, item_type, item)
        return
    if tag_type == TAG_COMPOUND:
        for name, entry in value.items():
            _write_byte(buffer, entry["type"])
            _write_string(buffer, name)
            _write_payload(buffer, entry["type"], entry["value"])
        _write_byte(buffer, TAG_END)
        return
    if tag_type == TAG_INT_ARRAY:
        _write_int(buffer, len(value))
        for item in value:
            _write_int(buffer, item)
        return
    if tag_type == TAG_LONG_ARRAY:
        _write_int(buffer, len(value))
        for item in value:
            _write_long(buffer, item)
        return
    raise ValueError(f"Unsupported tag type {tag_type}")


def _read_byte(buffer: io.BytesIO, signed: bool = False) -> int:
    data = buffer.read(1)
    if not data:
        raise EOFError("Unexpected end of stream")
    return struct.unpack(">b" if signed else ">B", data)[0]


def _read_short(buffer: io.BytesIO) -> int:
    return struct.unpack(">h", buffer.read(2))[0]


def _read_int(buffer: io.BytesIO) -> int:
    return struct.unpack(">i", buffer.read(4))[0]


def _read_long(buffer: io.BytesIO) -> int:
    return struct.unpack(">q", buffer.read(8))[0]


def _read_float(buffer: io.BytesIO) -> float:
    return struct.unpack(">f", buffer.read(4))[0]


def _read_double(buffer: io.BytesIO) -> float:
    return struct.unpack(">d", buffer.read(8))[0]


def _read_string(buffer: io.BytesIO) -> str:
    length = _read_short(buffer)
    data = buffer.read(length)
    return data.decode("utf-8", errors="ignore")


def _write_byte(buffer: io.BytesIO, value: int, signed: bool = False) -> None:
    buffer.write(struct.pack(">b" if signed else ">B", value))


def _write_short(buffer: io.BytesIO, value: int) -> None:
    buffer.write(struct.pack(">h", value))


def _write_int(buffer: io.BytesIO, value: int) -> None:
    buffer.write(struct.pack(">i", value))


def _write_long(buffer: io.BytesIO, value: int) -> None:
    buffer.write(struct.pack(">q", value))


def _write_float(buffer: io.BytesIO, value: float) -> None:
    buffer.write(struct.pack(">f", value))


def _write_double(buffer: io.BytesIO, value: float) -> None:
    buffer.write(struct.pack(">d", value))


def _write_string(buffer: io.BytesIO, value: str) -> None:
    encoded = value.encode("utf-8")
    _write_short(buffer, len(encoded))
    buffer.write(encoded)
