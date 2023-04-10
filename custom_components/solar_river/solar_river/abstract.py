from __future__ import annotations

from typing import Protocol

from .model import InverterConfig, InverterPVData, InverterSpecs


class SamilInverter(Protocol):
    serial: bytes

    async def get_specs(self) -> InverterSpecs:
        ...

    async def get_config(self) -> InverterConfig:
        ...

    async def get_pv_data(self) -> InverterPVData:
        ...


class Samil(Protocol):
    inverters: list[SamilInverter]

    @staticmethod
    async def discover_inverters(host: str, port: int) -> Samil:
        ...
