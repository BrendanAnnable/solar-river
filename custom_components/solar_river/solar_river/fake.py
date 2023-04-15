from __future__ import annotations
import asyncio
from .abstract import (
    Samil,
    SamilInverter,
)
from .model import (
    InverterConfig,
    InverterPVData,
    InverterSpecs,
)
from random import randint


class FakeSamilSolarRiver(SamilInverter):
    def __init__(self, serial):
        self.serial = serial
        self.last_pv_power = 50000

    async def get_specs(self) -> InverterSpecs:
        await asyncio.sleep(1)
        return InverterSpecs(
            1,  # type
            "4000",  # va_rating
            "V1.00",  # firmware
            "SolarRiver 4.4KW",  # model
            "SAMILPOWER",  # manufacturer
            self.serial,  # serial
        )

    async def get_config(self) -> InverterConfig:
        await asyncio.sleep(1)
        return InverterConfig(
            150.0,  # startup_voltage
            60,  # time_to_connected_grid
            200.0,  # min_grid_voltage
            270.0,  # max_grid_voltage
            49.00,  # min_grid_frequency
            51.00,  # max_grid_frequency
        )

    async def get_pv_data(self) -> InverterPVData:
        await asyncio.sleep(1)
        self.last_pv_power = self.last_pv_power + randint(-50, 50)
        return InverterPVData(
            randint(20, 50),  # internal_temperature
            202.1,  # p1_voltage
            0.8,  # p1_current
            43963,  # working_hours
            1,  # operating_mode
            5.85,  # total_kwh_today
            0.7,  # grid_current
            243.7,  # grid_voltage
            50.06,  # grid_frequency
            self.last_pv_power,  # output_power
            56429,  # total_lifetime_kwh
        )


class FakeSamil(Samil):
    def __init__(self, inverters):
        self.inverters = inverters

    @staticmethod
    async def discover_inverters(host: str, port: int, num_inverters: int = None) -> FakeSamil:
        return FakeSamil([
            FakeSamilSolarRiver("FAKESERIAL1"),
        ])
