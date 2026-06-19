from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import json
import struct
from typing import Any, Iterable

MAGIC = b"SUGI"
VERSION = 1
_HEADER = struct.Struct(">4sH")
_INSTRUCTION = struct.Struct(">HI")


class OpCode(IntEnum):
    CREATE_NODE = 1
    DELETE_NODE = 2
    SET_PROPERTY = 3
    SET_VARIABLE = 4
    APPEND_CHILD = 5
    REMOVE_CHILD = 6
    REGISTER_EVENT = 7
    MOUNT_PACKAGE = 8
    UNMOUNT_PACKAGE = 9
    CALL = 10
    NOOP = 11


@dataclass(frozen=True)
class Instruction:
    opcode: OpCode
    payload: dict[str, Any]


@dataclass(frozen=True)
class BytecodeProgram:
    instructions: tuple[Instruction, ...]
    version: int = VERSION

    def encode(self) -> bytes:
        data = bytearray(_HEADER.pack(MAGIC, self.version))
        for instruction in self.instructions:
            payload = json.dumps(instruction.payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            data.extend(_INSTRUCTION.pack(int(instruction.opcode), len(payload)))
            data.extend(payload)
        return bytes(data)

    @classmethod
    def decode(cls, data: bytes) -> "BytecodeProgram":
        if len(data) < _HEADER.size:
            raise ValueError("bytecode is shorter than the SUGI header")
        magic, version = _HEADER.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError("bytecode magic must be SUGI")
        if version != VERSION:
            raise ValueError(f"unsupported SUGI bytecode version: {version}")
        offset = _HEADER.size
        instructions: list[Instruction] = []
        while offset < len(data):
            if offset + _INSTRUCTION.size > len(data):
                raise ValueError("truncated instruction header")
            raw_opcode, length = _INSTRUCTION.unpack_from(data, offset)
            offset += _INSTRUCTION.size
            end = offset + length
            if end > len(data):
                raise ValueError("truncated instruction payload")
            payload = json.loads(data[offset:end].decode("utf-8")) if length else {}
            instructions.append(Instruction(OpCode(raw_opcode), payload))
            offset = end
        return cls(tuple(instructions), version)


def program(instructions: Iterable[Instruction]) -> BytecodeProgram:
    return BytecodeProgram(tuple(instructions))
