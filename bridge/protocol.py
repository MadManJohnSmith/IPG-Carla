"""protocol.py — Protocolo UDP compartido para el puente IPG → CARLA."""
import struct
from collections import namedtuple

PACKET_FMT = "!I3f"
PACKET_SIZE = struct.calcsize(PACKET_FMT)
Packet = namedtuple("Packet", ["seq", "steer", "gas", "brake"])

def pack(seq: int, steer: float, gas: float, brake: float) -> bytes:
    return struct.pack(PACKET_FMT, seq, steer, gas, brake)

def unpack(data: bytes) -> Packet:
    return Packet(*struct.unpack(PACKET_FMT, data))
